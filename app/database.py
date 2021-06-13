import databases
from sqlalchemy import MetaData

from app.config import settings

metadata = MetaData()

db = databases.Database(settings.db_url)
