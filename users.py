import json
import hashlib

from pymongo import MongoClient

from date import current_date


# Load 'config.json' file
conf = json.load(
    open("config.json", "r+")
)

# MongoDB Init
client = MongoClient(conf["mongodb"]["connection-string"])
db = client.MyEshop

users = db.Users


# Create 'User' class
# This will handle creating users and auth
class User():
    def __init__(self, username):
        self.username = username

        self.query = users.find_one({"username": str(username)})

    # Auth => Check if password is correct to the username
    def auth(self, password):
        if self.query != None:
            if self.query["hash"] == self.create_hash(password):
                
                return True

            else:
                return False

        else:
            return False


    # Create a new user
    def create_user(self, password):
        if self.query == None:
            try:
                users.insert_one({
                    "username": str(self.username),
                    "hash": str(self.create_hash(password)),
                    "created": str(current_date())
                })

                return True

            except:
                return False

    # This function returns a hash from the password 
    # salted by username
    def create_hash(self, password):
        return(
            hashlib.sha256(f"{password}{self.username}".encode()).hexdigest()
            )
