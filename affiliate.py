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

affiliates = db.Affiliate


# Create 'Affiliate' class
# This will handle creating users and auth
class Affiliate():
    def __init__(self, campaign):
        self.campaign = campaign

        self.query = affiliates.find_one({"campaign": str(campaign)})

        if self.query != None:
            self.visits = self.query["visits"]

    # Create new campaign
    def create_campaign(self):
        
        try:
            if self.query == None:
                affiliates.insert_one({
                    "campaign": str(self.campaign),
                    "visits": 0
                })


            return True
            

        except:
            return False

    # Add campaign visit
    def add_visit(self):
        try:
            if self.query != None:
                current_visits = int(self.visits)

                affiliates.update_one({
                    "campaign": str(self.campaign)
                },
                {
                    "$set": {
                        "visits": str(current_visits + 1)
                    }
                })

                return True

            else:
                return False

        except:
            return False



    # Delete campaign
    def delete_affiliate(self):
        try:
            if self.query != None:
                affiliates.delete_one({
                    "campaign": str(self.campaign)
                })
                
                return True

            else:
                return False

        except:
            return False

