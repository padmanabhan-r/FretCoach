"""
AI Agent Service for FretCoach
Uses LangGraph orchestration to analyze practice history and generate practice recommendations
"""

from typing import Literal, Dict, Any, Optional
from datetime import datetime
import json
import os
import uuid
from dotenv import load_dotenv, find_dotenv

from langchain_openai import ChatOpenAI
from langchain.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

# Import Opik for tracking (optional)
try:
    from opik import configure
    from opik.integrations.langchain import OpikTracer
    configure()
    OPIK_ENABLED = True
except ImportError:
    OPIK_ENABLED = False
    OpikTracer = None

# Load environment variables
load_dotenv(find_dotenv())

# Get PostgreSQL credentials from environment
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Create PostgreSQL connection
db_uri = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
db = SQLDatabase.from_uri(db_uri)

# Initialize LLM
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create SQL toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()


class PracticeRecommendation(BaseModel):
    """Structured output for practice recommendations"""
    scale_name: str = Field(description="The recommended scale to practice (e.g., 'C', 'D', 'E')")
    scale_type: str = Field(description="Type of scale: 'diatonic' or 'pentatonic'")
    focus_area: str = Field(description="The area to focus on: 'pitch', 'scale', or 'timing'")
    reasoning: str = Field(description="Explanation for why this practice session is recommended")
    strictness: float = Field(description="Recommended strictness level (0.0-1.0)", ge=0.0, le=1.0)
    sensitivity: float = Field(description="Recommended sensitivity level (0.0-1.0)", ge=0.0, le=1.0)


# Setup tool nodes
get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
get_schema_node = ToolNode([get_schema_tool], name="get_schema")

run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
run_query_node = ToolNode([run_query_tool], name="run_query")


def list_tables(state: MessagesState):
    """List available database tables"""
    tool_call = {
        "name": "sql_db_list_tables",
        "args": {},
        "id": "abc123",
        "type": "tool_call",
    }
    tool_call_message = AIMessage(content="", tool_calls=[tool_call])

    list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
    tool_message = list_tables_tool.invoke(tool_call)
    response = AIMessage(f"Available tables: {tool_message.content}")

    return {"messages": [tool_call_message, tool_message, response]}


def call_get_schema(state: MessagesState):
    """Force model to retrieve schema information"""
    llm_with_tools = model.bind_tools([get_schema_tool], tool_choice="any")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


generate_query_system_prompt = """
You are an AI guitar coach analyzing a student's practice history.
You have access to two tables:
1. sessions - Contains all practice session data with metrics
2. ai_practice_plans - Contains previously generated practice plans

Your task is to:
1. Check if there's a recent practice plan that hasn't been executed yet (executed_session_id IS NULL)
2. Analyze the student's recent performance from the sessions table
3. Identify areas needing improvement (pitch_accuracy, scale_conformity, timing_stability)

Important PostgreSQL rules:
- When using aggregate functions like MAX(), MIN(), COUNT(), use GROUP BY for all non-aggregated columns
- Or use ORDER BY with LIMIT instead of aggregation when getting recent records
- NEVER use SELECT * - only select necessary columns

Create syntactically correct PostgreSQL queries to gather this information.
DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP).
""".format(dialect=db.dialect)


def generate_query(state: MessagesState):
    """Generate SQL query to analyze practice data"""
    system_message = {
        "role": "system",
        "content": generate_query_system_prompt,
    }
    llm_with_tools = model.bind_tools([run_query_tool])
    response = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [response]}


check_query_system_prompt = """
You are a SQL expert reviewing PostgreSQL queries.
Check for common mistakes:
- Using NOT IN with NULL values
- Missing GROUP BY for non-aggregated columns with aggregations
- Data type mismatches
- Proper column names and table references

If there are mistakes, rewrite the query. Otherwise, reproduce it.
You will call the query execution tool after this check.
""".format(dialect=db.dialect)


def check_query(state: MessagesState):
    """Validate and correct SQL query"""
    system_message = {
        "role": "system",
        "content": check_query_system_prompt,
    }
    
    tool_call = state["messages"][-1].tool_calls[0]
    user_message = {"role": "user", "content": tool_call["args"]["query"]}
    llm_with_tools = model.bind_tools([run_query_tool], tool_choice="any")
    response = llm_with_tools.invoke([system_message, user_message])
    response.id = state["messages"][-1].id
    
    return {"messages": [response]}


def should_continue(state: MessagesState) -> str:
    """Decide whether to continue query generation or end"""
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return END
    else:
        return "check_query"


# Build the LangGraph agent
builder = StateGraph(MessagesState)
builder.add_node(list_tables)
builder.add_node(call_get_schema)
builder.add_node(get_schema_node, "get_schema")
builder.add_node(generate_query)
builder.add_node(check_query)
builder.add_node(run_query_node, "run_query")

builder.add_edge(START, "list_tables")
builder.add_edge("list_tables", "call_get_schema")
builder.add_edge("call_get_schema", "get_schema")
builder.add_edge("get_schema", "generate_query")
builder.add_conditional_edges(
    "generate_query",
    should_continue,
)
builder.add_edge("check_query", "run_query")
builder.add_edge("run_query", "generate_query")

sql_agent = builder.compile()

# Create Opik tracer if available
if OPIK_ENABLED:
    opik_tracer = OpikTracer(graph=sql_agent.get_graph(xray=True))
else:
    opik_tracer = None


async def analyze_practice_history(user_id: str) -> Dict[str, Any]:
    """
    Analyze user's practice history using SQL agent
    
    Args:
        user_id: The user's identifier
        
    Returns:
        Dictionary containing analysis results
    """
    question = f"""
    For user_id '{user_id}':
    1. Check if there's an unexecuted practice plan (executed_session_id IS NULL in ai_practice_plans)
    2. Get the last 5 practice sessions ordered by start_timestamp DESC
    3. Calculate average metrics: pitch_accuracy, scale_conformity, timing_stability
    4. Identify which metric is lowest and needs improvement
    5. Check which scales have been practiced recently
    """
    
    # Configure streaming with Opik tracer if enabled
    stream_config = {}
    if OPIK_ENABLED and opik_tracer:
        stream_config["callbacks"] = [opik_tracer]
    
    messages = []
    for step in sql_agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values",
        config=stream_config,
    ):
        messages.append(step["messages"][-1])
    
    # Extract the final analysis from messages
    analysis_text = messages[-1].content if messages else "No analysis available"
    
    return {
        "analysis": analysis_text,
        "messages": messages
    }


async def generate_practice_recommendation(user_id: str, analysis: str) -> PracticeRecommendation:
    """
    Generate structured practice recommendation based on analysis
    
    Args:
        user_id: The user's identifier
        analysis: Text analysis of practice history
        
    Returns:
        Structured practice recommendation
    """
    # Use structured output to generate recommendation
    structured_llm = model.with_structured_output(PracticeRecommendation)
    
    prompt = f"""
    Based on the following practice history analysis, generate a specific practice recommendation:
    
    {analysis}
    
    Consider:
    - Which metric needs the most improvement
    - Which scales haven't been practiced recently
    - Appropriate difficulty settings (strictness/sensitivity) based on skill level
    - If there's already an unexecuted plan, follow it; otherwise create a new one
    
    Generate a practice session recommendation with:
    - Specific scale to practice
    - Scale type (diatonic or pentatonic)
    - Primary focus area (pitch, scale, or timing)
    - Clear reasoning
    - Appropriate strictness and sensitivity levels
    """
    
    recommendation = structured_llm.invoke([{"role": "user", "content": prompt}])
    return recommendation


async def save_practice_plan(user_id: str, recommendation: PracticeRecommendation) -> str:
    """
    Save the practice plan to the database
    
    Args:
        user_id: The user's identifier
        recommendation: The practice recommendation to save
        
    Returns:
        The practice_id (UUID) of the saved plan
    """
    practice_id = str(uuid.uuid4())
    
    practice_plan_json = json.dumps({
        "scale_name": recommendation.scale_name,
        "scale_type": recommendation.scale_type,
        "focus_area": recommendation.focus_area,
        "reasoning": recommendation.reasoning,
        "strictness": recommendation.strictness,
        "sensitivity": recommendation.sensitivity,
        "generated_at": datetime.now().isoformat()
    })
    
    # Use raw SQL to insert the plan
    from sqlalchemy import text
    
    insert_query = text("""
        INSERT INTO ai_practice_plans (practice_id, user_id, practice_plan)
        VALUES (:practice_id, :user_id, :practice_plan)
    """)
    
    with db._engine.begin() as conn:  # begin() handles commit/rollback automatically
        conn.execute(
            insert_query,
            {
                "practice_id": practice_id,
                "user_id": user_id,
                "practice_plan": practice_plan_json
            }
        )
    
    return practice_id


async def get_ai_practice_session(user_id: str) -> Dict[str, Any]:
    """
    Main entry point for AI-driven practice session generation
    
    Args:
        user_id: The user's identifier
        
    Returns:
        Dictionary containing practice recommendation and metadata
    """
    # Step 1: Analyze practice history
    analysis_result = await analyze_practice_history(user_id)
    
    # Step 2: Generate recommendation
    recommendation = await generate_practice_recommendation(user_id, analysis_result["analysis"])
    
    # Step 3: Save practice plan
    practice_id = await save_practice_plan(user_id, recommendation)
    
    return {
        "practice_id": practice_id,
        "recommendation": {
            "scale_name": recommendation.scale_name,
            "scale_type": recommendation.scale_type,
            "focus_area": recommendation.focus_area,
            "reasoning": recommendation.reasoning,
            "strictness": recommendation.strictness,
            "sensitivity": recommendation.sensitivity,
        },
        "analysis": analysis_result["analysis"]
    }
