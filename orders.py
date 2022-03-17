import json

from pymongo import MongoClient

from date import current_date


# Load 'config.json' file
conf = json.load(
    open("config.json", "r+")
)

# MongoDB Init
client = MongoClient(conf["mongodb"]["connection-string"])
db = client.MyEshop

orders = db.Orders


# Create 'order' class
# It's main usecase is to make it easier
# to work with orders later

class Order():
    def __init__(self, order_id):
        self.order_id = order_id

        order_query = orders.find_one({"order-id": order_id})

        self.order_query = order_query


        # Check if product already exists
        # If yes, set variables for order info
        if order_query != None:
            self.name = order_query["name"]
            self.email = order_query["email"]
            self.phone = order_query["phone"]

            self.street = order_query["street"]
            self.apartment = order_query["apartment"]
            self.city = order_query["city"]
            self.postcode = order_query["postcode"]
            self.country = order_query["country"]

            self.products = order_query["products"]
            self.price = order_query["price"]

            self.state = order_query["state"]
            self.created = order_query["created"]
            self.last_change = order_query["last-change"]
            self.changed_by = order_query["changed-by"]
            

    def create_order( 
        self, name, email, phone,
        street, apartment, city, postcode, country,
        products, price):

        if self.order_query == None:
            orders.insert_one({
                "order-id": str(self.new_order_id()),

                "name": str(name),
                "email": str(email),
                "phone": str(phone),
                
                "street": str(street),
                "apartment": str(apartment),
                "city": str(city),
                "postcode": str(postcode),
                "country": str(country),

                "products": products,
                "price": str(price),

                "state": "CREATED",
                "created": str(current_date()),
                "last-change": str(current_date()),
                "changed-by": "Client"
            })

            return True

        else:
            return False

    
    # Change order state
    # CREATED, PROCESSING, PACKED, SENT, DELIVERED, CLOSED
    def update_state(self, state, user):
        if self.order_query != None:

            orders.update_one(
                {"order-id": str(self.order_id)},
                
                {"$set": {
                    "state": str(state),
                    "last-change": str(current_date()),
                    "changed-by": str(user)
                }
                }
            )
            
            
            return True

        else:
            return False  

        
    # Get the newews order number
    # This function searches what was the latest order
    # number and increases if with 1 for the new order
    def new_order_id(self):
        if orders.estimated_document_count() != 0:

            new_number = int(orders.estimated_document_count()) + 1

            return(new_number)


        else:
            return(1)

