import argparse
import pymongo
import os
import logging
from pymongo import MongoClient
from gridfs import GridFS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeleneMongoDB:
    def __init__(self, mongo_uri, database_name, collection_name):
        try:
            self.client = pymongo.MongoClient(mongo_uri)
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            logger.info("Connected to MongoDB successfully.")
        except pymongo.errors.ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")

    def post_build(self, build_data):
        try:
            self.collection.insert_one(build_data)
            logger.info("Build data posted to MongoDB.")
        except pymongo.errors.PyMongoError as e:
            logger.error(f"Failed to post build data to MongoDB: {e}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Post build data to MongoDB")
    parser.add_argument("--build", required=True, help="Build name")
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument("--stage", required=True, help="Stage name")
    parser.add_argument("results_path", help="Results path")
    return parser.parse_args()

def upload_file(fs, file_path):
    try:
        with open(file_path, "rb") as file:
            file_id = fs.put(file, filename=os.path.basename(file_path))
            logger.info(f"File {file_path} uploaded with id: {file_id}")
    except Exception as e:
        logger.error(f"Failed to upload file {file_path}: {e}")

def upload_files_in_directory(fs, directory):
    if not os.path.isdir(directory):
        logger.error(f"{directory} is not a directory.")
        return

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            upload_file(fs, file_path)

def main():
    args = parse_arguments()

    mongo_uri = "mongodb://localhost:27017/"
    database_name = args.branch
    collection_name = args.build

    try:
        client = MongoClient(mongo_uri)
        db = client[database_name]
        fs = GridFS(db, collection=collection_name)

        selene_mongodb = SeleneMongoDB(mongo_uri, database_name, collection_name)

        build_data = {
            "stage": args.stage,
            "results_path": args.results_path
        }

        selene_mongodb.post_build(build_data)
        upload_files_in_directory(fs, args.results_path)
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
