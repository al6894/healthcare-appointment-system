from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
db_name = os.getenv("DB_NAME")

if not uri or not db_name:
    raise RuntimeError("Missing environment variables: MONGODB_URI={}, DB_NAME={}".format(uri, db_name))

print("Connecting to MongoDB URI: {}".format(uri))
print("Using database: {}".format(db_name))
try:
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client[db_name]
    providers_collection = db["provider-data"]
except Exception as e:
    print("Error connecting to MongoDB: {}".format(e))
    raise


def test_connection():
    try:
        client.admin.command("ping")
        print("Pinged your deployment. Successfully connected to MongoDB!")
    except Exception as error:
        print("Error connecting to MongoDB: {}".format(error))
        raise