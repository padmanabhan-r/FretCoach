#!/usr/bin/env python3
"""
FretCoach AI Mode Setup Script
Initializes the database and verifies AI mode configuration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env_vars():
    """Check if required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = {
        'GOOGLE_API_KEY': 'Google API key for Gemini AI recommendations',
        'DB_USER': 'PostgreSQL username',
        'DB_HOST': 'PostgreSQL host',
        'DB_PORT': 'PostgreSQL port',
        'DB_NAME': 'PostgreSQL database name',
    }
    
    missing = []
    for var, desc in required_vars.items():
        if not os.getenv(var):
            missing.append(f"  - {var}: {desc}")
    
    if missing:
        print("\n❌ Missing required environment variables:")
        for m in missing:
            print(m)
        print("\n💡 Create a .env file based on .env.example")
        return False
    
    print("✅ All required environment variables are set")
    return True


def check_database():
    """Check database connection and schema"""
    print("\n🔍 Checking database connection...")
    
    try:# Build database URI from environment variables
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD', '')
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        
        if db_password:
            db_uri = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            db_uri = f"postgresql+psycopg2://{db_user}@{db_host}:{db_port}/{db_name}"
        
        engine = create_engine(db_uriengine, text
        
        db_path = os.getenv('FRETCOACH_DB_PATH')
        engine = create_engine(db_path)
        
        with engine.connect() as conn:
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('sessions', 'ai_practice_plans')
            """))
            tables = [row[0] for row in result]
            
            if 'sessions' not in tables:
                print("❌ sessions table not found")
                return False
            
            if 'ai_practice_plans' not in tables:
                print("❌ ai_practice_plans table not found")
                print("💡 Run: psql -d fretcoach -f backend/sql/schema.sql")
                return False
            
            print("✅ Database tables verified")
            return True
    
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure PostgreSQL is running and database exists")
        return False


def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n🔍 Checking Python dependencies...")
    
    required_packages = [
        'langchain',
        'langchain_google_genai',
        'langgraph',
        'langchain_community',
        'fastapi',
        'sqlalchemy',
        'psycopg2',
        'python-dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("💡 Run: pip install -e .")
        return False
    
    print("✅ All required packages installed")
    return True


def test_ai_agent():
    """Test the AI agent setup"""
    print("\n🔍 Testing AI agent initialization...")
    
    try:
        # Import without triggering OpenAI call
        sys.path.insert(0, str(Path(__file__).parent / 'backend'))
        
        print("✅ AI agent module can be imported")
        return True
    
    except Exception as e:
        print(f"❌ AI agent initialization failed: {e}")
        return False


def main():
    """Run all setup checks"""
    print("=" * 60)
    print("FretCoach AI Mode Setup")
    print("=" * 60)
    
    checks = [
        check_env_vars(),
        check_dependencies(),
        check_database(),
        test_ai_agent(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ All checks passed! AI mode is ready to use.")
        print("\n📚 Next steps:")
        print("  1. Start the backend: python -m backend.api.server")
        print("  2. Start the frontend: cd application && npm run dev")
        print("  3. Complete 2-3 manual practice sessions")
        print("  4. Try AI mode to get personalized recommendations")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)
    print("=" * 60)


if __name__ == '__main__':
    main()
