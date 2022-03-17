import json

from pymongo import MongoClient


# Load 'config.json' file
conf = json.load(
    open("config.json", "r+")
)

# MongoDB Init
client = MongoClient(conf["mongodb"]["connection-string"])
db = client.MyEshop

promos = db.PromoCodes


# Create 'Promo' class
# It's main usecase is to make it easier
# to work with promo codes later

class Promo():
    def __init__(self, code):
        self.code = code

        promo_query = promos.find_one({"code": code})

        self.query = promo_query

        # Check if product already exists
        # If yes, set variables for product info
        if promo_query != None:
            self.name = promo_query["name"]
            self.discount = promo_query["discount"]


    def create_promo( 
        self, name, discount):

        # If product doesn't already exist
        # create a new one 
        if promos.find_one({"code": self.code}) == None:
            promos.insert_one({
                "name": str(name),
                "code": str(self.code),
                "discount": str(discount),
            })
            
            return True

        else:
            return False

    def delete_promo(self):
        try:
            promos.delete_one({"code": self.code})

            return True

        except:
            return False



