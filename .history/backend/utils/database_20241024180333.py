from pymongo.mongo_client import MongoClient
import os
from urllib.parse import urlparse

app = ""

uri = "mongodb+srv://weslagarde:Beaubeau2023!@cluster0.zpowdpt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)

def init_db(app, recreate=True):
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        
        if recreate:
            # Parse the URI to get the database name
            parsed_uri = urlparse(uri)
            db_name = parsed_uri.path.strip('/')
            
            # If no database name is specified, use a default one
            if not db_name:
                db_name = "exocortex"
            
            client.drop_database(db_name)
            print(f"Database '{db_name}' deleted.")
            
        return client[db_name]  # Return the database instance
            
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

db = init_db(app)