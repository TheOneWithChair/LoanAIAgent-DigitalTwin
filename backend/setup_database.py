"""
Database initialization and migration script.

Run this script to:
1. Test database connection
2. Create all tables
3. Verify schema
"""

import asyncio
import logging
from sqlalchemy import text

from app.database import init_db, close_db, engine
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_connection():
    """Test database connection"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info("✅ Database connection successful!")
            logger.info(f"PostgreSQL version: {version}")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def create_tables():
    """Create all database tables"""
    try:
        await init_db()
        logger.info("✅ All tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False


async def verify_tables():
    """Verify that tables exist"""
    try:
        async with engine.begin() as conn:
            # Check for loan_applications table
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('loan_applications', 'agent_execution_logs')
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if 'loan_applications' in tables:
                logger.info("✅ loan_applications table exists")
            else:
                logger.warning("⚠️ loan_applications table not found")
            
            if 'agent_execution_logs' in tables:
                logger.info("✅ agent_execution_logs table exists")
            else:
                logger.warning("⚠️ agent_execution_logs table not found")
            
            return len(tables) == 2
    except Exception as e:
        logger.error(f"❌ Failed to verify tables: {e}")
        return False


async def main():
    """Main setup function"""
    logger.info("=" * 60)
    logger.info("Loan Processing AI Agent - Database Setup")
    logger.info("=" * 60)
    logger.info(f"Database URL: {settings.DATABASE_URL[:50]}...")
    logger.info("")
    
    # Test connection
    logger.info("Step 1: Testing database connection...")
    if not await test_connection():
        logger.error("Please check your DATABASE_URL in .env file")
        return
    logger.info("")
    
    # Create tables
    logger.info("Step 2: Creating database tables...")
    if not await create_tables():
        logger.error("Failed to create tables")
        return
    logger.info("")
    
    # Verify tables
    logger.info("Step 3: Verifying tables...")
    if not await verify_tables():
        logger.warning("Some tables may be missing")
    logger.info("")
    
    # Cleanup
    await close_db()
    
    logger.info("=" * 60)
    logger.info("✅ Database setup complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("You can now start the server:")
    logger.info("  python -m uvicorn app.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())
