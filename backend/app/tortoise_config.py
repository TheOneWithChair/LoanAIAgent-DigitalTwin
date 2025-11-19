"""
Database Configuration and Initialization for Tortoise ORM
Handles connection to Neon PostgreSQL and schema generation
"""
import os
import logging
from typing import Optional, List
from tortoise import Tortoise, connections
from tortoise.exceptions import DBConnectionError
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration manager"""
    
    def __init__(self):
        # Get database URL from environment (Neon PostgreSQL)
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://user:password@ep-example.neon.tech/loandb?sslmode=require"
        )
        
        # Remove quotes if present (Windows SET command may add them)
        if self.database_url.startswith('"') and self.database_url.endswith('"'):
            self.database_url = self.database_url[1:-1]
        
        # Tortoise ORM requires 'postgres://' not 'postgresql://'
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgres://", 1)
        
        # Convert sslmode to ssl for asyncpg compatibility
        # asyncpg uses 'ssl=require' instead of 'sslmode=require'
        self.database_url = self.database_url.replace("sslmode=", "ssl=")
        
        # Remove channel_binding parameter (not supported by asyncpg)
        if "channel_binding=" in self.database_url:
            import re
            self.database_url = re.sub(r'[&?]channel_binding=[^&]*', '', self.database_url)
        
        # Simple string connection for Tortoise ORM
        self.config = {
            "connections": {
                "default": self.database_url
            },
            "apps": {
                "models": {
                    "models": ["app.db_models", "aerich.models"],
                    "default_connection": "default",
                }
            },
            "use_tz": True,
            "timezone": "UTC"
        }
    
    def get_tortoise_config(self) -> dict:
        """Get Tortoise ORM configuration"""
        return self.config


# Global database config instance
db_config = DatabaseConfig()


async def init_database(
    generate_schemas: bool = True,
    safe: bool = True,
    add_exception_handlers: bool = True
) -> None:
    """
    Initialize Tortoise ORM and connect to database
    
    Args:
        generate_schemas: Whether to generate database schemas
        safe: If True, only create missing tables (don't drop existing)
        add_exception_handlers: Add exception handlers for common DB errors
    
    Raises:
        DBConnectionError: If connection to database fails
    """
    try:
        logger.info("Initializing Tortoise ORM...")
        logger.info(f"Database URL: {db_config.database_url[:50]}...{db_config.database_url[-30:]}")
        
        # Initialize Tortoise
        await Tortoise.init(config=db_config.get_tortoise_config())
        
        logger.info("Connected to Neon PostgreSQL database")
        
        # Generate schemas if requested
        if generate_schemas:
            logger.info(f"Generating database schemas (safe={safe})...")
            try:
                await Tortoise.generate_schemas(safe=safe)
                logger.info("Database schemas generated successfully")
            except Exception as schema_error:
                logger.error(f"Schema generation failed: {schema_error}")
                logger.error(f"Error type: {type(schema_error).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise
        
        # Add exception handlers
        if add_exception_handlers:
            _setup_exception_handlers()
        
        logger.info("Database initialization completed successfully")
        
    except DBConnectionError as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise


async def close_database() -> None:
    """
    Close all database connections
    Should be called on application shutdown
    """
    try:
        logger.info("Closing database connections...")
        await connections.close_all()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


def _setup_exception_handlers() -> None:
    """Setup common database exception handlers"""
    # Add custom exception handling logic here if needed
    pass


@asynccontextmanager
async def get_db_connection():
    """
    Context manager for database connection
    Ensures proper connection handling and cleanup
    
    Usage:
        async with get_db_connection():
            # Perform database operations
            pass
    """
    try:
        # Connection is already managed by Tortoise
        yield
    except Exception as e:
        logger.error(f"Database operation error: {e}")
        raise
    finally:
        # Tortoise handles connection pooling automatically
        pass


async def health_check() -> dict:
    """
    Check database health and connection status
    
    Returns:
        dict: Health status information
    """
    try:
        # Try to get connection
        conn = connections.get("default")
        
        # Execute a simple query
        await conn.execute_query("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "backend": "asyncpg",
            "message": "Database connection is active"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "message": "Database connection failed"
        }


async def reset_database() -> None:
    """
    Drop all tables and recreate schemas
    WARNING: This will delete all data!
    Should only be used in development/testing
    """
    logger.warning("RESETTING DATABASE - ALL DATA WILL BE LOST!")
    try:
        await Tortoise.init(config=db_config.get_tortoise_config())
        await Tortoise.generate_schemas(safe=False)  # Drop and recreate
        logger.info("Database reset completed")
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        raise


# Migration utilities
async def run_migrations() -> None:
    """
    Run database migrations using Aerich
    Note: Aerich must be configured separately
    """
    logger.info("Running database migrations...")
    # Migrations are typically handled by Aerich CLI
    # This is a placeholder for programmatic migration execution
    pass


async def get_database_stats() -> dict:
    """
    Get database statistics and table information
    
    Returns:
        dict: Database statistics
    """
    try:
        from app.db_models import LoanApplication, AgentResult, ApplicationAnalytics, AuditLog
        
        stats = {
            "total_applications": await LoanApplication.all().count(),
            "approved_applications": await LoanApplication.filter(
                application_status="approved"
            ).count(),
            "rejected_applications": await LoanApplication.filter(
                application_status="rejected"
            ).count(),
            "in_progress_applications": await LoanApplication.filter(
                application_status="in_progress"
            ).count(),
            "total_agent_results": await AgentResult.all().count(),
            "total_analytics_records": await ApplicationAnalytics.all().count(),
            "total_audit_logs": await AuditLog.all().count(),
        }
        
        return stats
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return {"error": str(e)}


# Lifespan context manager for FastAPI
@asynccontextmanager
async def lifespan_handler(app):
    """
    FastAPI lifespan context manager
    Handles database initialization and cleanup
    
    Usage in FastAPI:
        app = FastAPI(lifespan=lifespan_handler)
    """
    # Startup
    logger.info("Application startup - Initializing database...")
    try:
        await init_database(generate_schemas=True, safe=True)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.warning("Application will continue without database")
    
    yield
    
    # Shutdown
    logger.info("Application shutdown - Closing database connections...")
    try:
        await close_database()
    except Exception as e:
        logger.error(f"Error during database shutdown: {e}")


# Export key functions and config
__all__ = [
    "DatabaseConfig",
    "db_config",
    "init_database",
    "close_database",
    "get_db_connection",
    "health_check",
    "reset_database",
    "run_migrations",
    "get_database_stats",
    "lifespan_handler",
]
