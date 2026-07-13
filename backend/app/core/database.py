from sqlalchemy import create_engine
from app.core.config import settings

# In a real app, you might want to use a connection pool or async engine
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True) if settings.DATABASE_URL else None
