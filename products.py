import json
from numpy import product

from pymongo import MongoClient


# Load 'config.json' file
conf = json.load(
    open("config.json", "r+")
)

# MongoDB Init
client = MongoClient(conf["mongodb"]["connection-string"])
db = client.MyEshop

products = db.Products


# Create 'product' class
# It's main usecase is to make it easier
# to work with products later

class Product():
    def __init__(self, slug):
        self.slug = slug

        product_query = products.find_one({"slug": slug})


        # Check if product already exists
        # If yes, set variables for product info
        if product_query != None:
            self.name = product_query["name"]
            self.description = product_query["description"]
            self.price = product_query["price"]
            self.tag = product_query["tag"]
            self.picture = product_query["picture"]
            self.visibility = product_query["visibility"]

    def create_product( 
        self, name, description, price, tag, picture):

        # If product doesn't already exist
        # create a new one 
        if products.find_one({"slug": self.slug}) == None:
            products.insert_one({
                "name": str(name),
                "slug": str(self.slug),
                "description": str(description),
                "price": str(price),
                "tag": str(tag),
                "picture": str(picture),
                "visibility": "TRUE"
            })

            return True

        else:
            return False


    # Changes product visibility - True/False
    # This way you can turn the product off without deleting 
    # it from the db -> Can be still accessed by order's query 
    def change_product_visibility(self, state):
        try:
            products.update({
                "slug": str(self.slug)
            },
            {"$set": {
                "visibility": str(state)
            }})

            return True

        except:
            return False

    def delete_product(self):
        try:
            products.delete_one({"slug": str(self.slug)})
            
            return True

        except:
            return False


    def update_product(
        self, name, description, price, tag, picture):

        try:
            products.find_one_and_update({"slug": self.slug},
                {
                "name": str(name),
                "slug": str(self.slug),
                "description": str(description),
                "price": str(price),
                "tag": str(tag),
                "picture": str(picture)
            })
            
            return True

        except:
            return False
