import databases
from sqlalchemy import MetaData

from config import settings

metadata = MetaData()

db = databases.Database(settings.db_url)
