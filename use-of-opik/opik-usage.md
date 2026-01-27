# Opik Integration in FretCoach

## Features Used

### 1. Agent Graphs (LangGraph Visualization)

Agent graphs provide visual representation of LangGraph execution flow, making debugging and understanding agent behavior much easier.

**Implementation:**
```python
from opik.integrations.langchain import OpikTracer

# Enable graph visualization with xray=True
tracer = OpikTracer(
    project_name=os.getenv("OPIK_PROJECT_NAME", "FretCoach"),
    tags=["ai-coach", "langgraph", "practice-plan"],
    metadata={...},
    graph=workflow.get_graph(xray=True)  # Enables agent graph visualization
)
```

**Benefits:**
- Visual representation of agent execution flow (agent → tools → agent → end)
- See exact node transitions and decision paths
- Debug tool call sequences
- Understand when and why tools are invoked

**Location:** `web/web-backend/langgraph_workflow.py:321-332`

Access agent graphs in Opik dashboard by clicking **"Show Agent Graph"** in the trace sidebar.

---

### 2. Opik AI Assist

Opik's AI Assist feature analyzed our LangGraph traces and provided actionable optimization recommendations.

![Opik AI Assist](opik-assist.png)

**Key Insights Provided:**
1. **Excessive token usage** - Identified 4,877 tokens in single response with 8s duration
2. **Redundant context** - Detected full system prompt (~1,500 tokens) repeated on every turn
3. **Prompt inflation** - Found duplicated instructions and guidelines across LLM calls
4. **Optimization opportunity** - Suggested splitting prompts into core + detailed tiers

**Recommendations Implemented:**
- Split system prompt into CORE (~80 tokens) + DETAILED (~200 tokens)
- Send DETAILED only on first turn, CORE only on subsequent turns
- **Result:** 92% token reduction over 5-turn conversation (7,500 → 600 tokens)
- **Impact:** Faster responses (20-30% improvement), lower API costs

---

## Summary

Opik helped us:
- ✅ **Visualize** agent execution with graph views
- ✅ **Identify** performance bottlenecks with AI Assist
- ✅ **Optimize** prompts for 92% token reduction
- ✅ **Monitor** LLM calls with detailed traces
- ✅ **Debug** agent decision paths efficiently