from pymongo.mongo_client import MongoClient
import os

uri = "mongodb+srv://weslagarde:Beaubeau2023!@cluster0.zpowdpt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)

def init_db(app, recreate=True):
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        
        if recreate:
            db_name = uri.split('/')[-1].split('?')[0]
            client.drop_database(db_name)
            print("Existing database deleted.")
            
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        


db = init_db(app)
