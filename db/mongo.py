import pymongo
from pymongo.errors import ConfigurationError

from settings import CONNECTION_STRING
from utils.logger import mongodb_logger

try:
    client = pymongo.MongoClient(CONNECTION_STRING)
    db = client["deutsche-sprache"]
    verbformen_col = db["verbformen"]
    context_reverso_col = db["context_reverso"]
    context_synonyms_col = db["context_synonyms"]
    mongodb_logger.info(f"A client '{db.name}' has initialized successfully")
except ConfigurationError as e:
    mongodb_logger.error(f"Failed to connect to mongodb with {CONNECTION_STRING=} ({e})")
