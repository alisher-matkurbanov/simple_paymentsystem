import databases
from sqlalchemy import MetaData
from .config import settings

# TODO secure the credentials
metadata = MetaData()

db = databases.Database(settings.db_url)
