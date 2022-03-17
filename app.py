# IMPORTS

# From libraries 
from flask import Flask, redirect, render_template, session, request, abort, url_for 
from pymongo import MongoClient
from pprint import pprint

# Full libraries
import json

# From different .py files
from date import current_date
from products import Product
from promo_codes import Promo
from users import User
from orders import Order
from affilitate import Affiliate






# Load 'config.json' file
conf = json.load(
    open("config.json", "r+")
)

# MongoDB Init
client = MongoClient(conf["mongodb"]["connection-string"])
db = client.MyEshop

products = db.Products
promos = db.PromoCodes
stats = db.Statistics
users = db.Users
orders = db.Orders
visits = db.Statistics
affiliates = db.Affiliate

# Flask Init
app = Flask(__name__)

app.secret_key = conf["flask"]["secret-key"]


# Set session to not be permanent.
# It increases security, although it also means
# that user (like and admin) will need to login always
# when he restarts the browser.
# This could be overcome by saving username and password 
# in browser.
# session.permanent = False


"""
HERE STARTS THE VIEWS SETUP
"""

# Homepage
@app.route("/")
def page_index():
    # Add a record to DB that the page has been accessed 
    if "accessed" not in session:
        
        stats.insert_one({
            "date": str(current_date()),
            "client": str(request.headers["User-Agent"])
        })

        # Create record in session so it'll know that
        # this client was already counted
        session["accessed"] = True


    # Get all items and return them in list 'items'
    items = []
    for product in products.find({}):
        items = [product] + items     


    # Get eshop info
    general = conf["general"]

    # Get number of items in cart
    if 'cart' in session:
        cart_state = len(session["cart"])

    else:
        session["cart"] = [] 

        cart_state = len(session["cart"])

    return render_template("/shop/index.html", general=general, items=items, cart_state = cart_state)


# Product page
@app.route("/product/<slug>")
def page_product(slug):

    # Create an object from the 'Product' class
    # using the request's provided slug.
    # We then use this object to get info about 
    # the product.
    item = Product(slug)

    # Get eshop info
    general = conf["general"]

    # Get number of items in cart
    if 'cart' in session:
        cart_state = len(session["cart"])

    else:
        session["cart"] = [] 

        cart_state = len(session["cart"])

    return render_template("/shop/product.html", item=item, general=general, cart_state = cart_state)  


# Products page
@app.route("/products")
def page_products():

    # Get all products
    items = []

        # Check for query parameters
    params = request.args.get("tag", None)

    if params != None:
        search_params = {"tag": str(params)}

    else:
        search_params = {}  

    for product in products.find(search_params):
        product = Product(product["slug"])

        items = [{
            "name": str(product.name),
            "price": str(product.price),
            "picture": str(product.picture),
            "slug": str(product.slug),
            "tag": str(product.tag),
            "visibility": str(product.visibility)
        }] + items    



    # Get eshop info
    general = conf["general"]

    # Get number of items in cart
    if 'cart' in session:
        cart_state = len(session["cart"])

    else:
        session["cart"] = [] 

        cart_state = len(session["cart"])

    return render_template("/shop/products.html", general=general, cart_state = cart_state, items=items)

# Cart
@app.route("/cart")
def page_cart():
    items = []

    # For item in 'cart' set an object and get
    # required info about the item.
    # Save it then as a dictionary and put it along 
    # with the other items into a list 'items' 
    if 'cart' in session:
        for item in session["cart"]:
            x = Product(item)

            items += [
                {"name": x.name,
                "price": x.price,
                "slug": item}
        ]

    else:
        session["cart"] = []

    # Do the same for promo codes

    discounts = []

    if 'promos' in session:
        for item in session["promos"]:
            x = Promo(item)

            discounts += [
                {"name": x.name,
                "discount": x.discount}
        ]

    # Calculate the total price (shipping included)
    total = float(conf["general"]["shipping-price"])

    # Get prices for all items
    for item in items:
        total += float(item["price"])

    # Add discounts
    for item in discounts:
        total -= float(item["discount"])

    # If total is lower than 0 (due to promo codes),
    # set it to total = 0
    if total < 0:
        total = 0


    # Round total so it does not create numbers with
    # too many floating points
    total = round(total, 2)
    


    # Get eshop info
    general = conf["general"]

    # Get number of items in cart
    if 'cart' in session:
        cart_state = len(session["cart"])

    else:
        session["cart"] = [] 

        cart_state = len(session["cart"])

    return render_template("/shop/cart.html", general=general, items=items, discounts=discounts, cart_state = cart_state, total=total)



# Complete order
# => Take all stuff that's in cart, and connect in with
# client' details (name, adress, etc.)
@app.route("/order")
def page_order():
    # Get eshop info
    general = conf["general"]

    # Get number of items in cart
    if 'cart' in session:
        cart_state = len(session["cart"])

    else:
        session["cart"] = [] 

        cart_state = len(session["cart"])

    return render_template("/shop/order.html", general=general, cart_state=cart_state)


# Message
# Return a message that is specified as argument
# h=<heading>&m=<message>
@app.route("/message")
def page_message():

    h = request.args.get("h", None)
    m = request.args.get("m", None)


    # Get eshop info
    general = conf["general"]

    # Get number of items in cart
    if 'cart' in session:
        cart_state = len(session["cart"])

    else:
        session["cart"] = [] 

        cart_state = len(session["cart"])

    return render_template("/shop/message.html", h=h, m=m,  general=general, cart_state=cart_state)


# Tracking page - Allow the client to see order' current status
@app.route("/tracking")
def page_tracking():
    order_id = request.args["order-id"]

    order = Order(order_id)

    if order.order_query != None:
        order = {
            "order-id": str(order_id),
            "price": str(order.price),
            "last-change": str(order.last_change),
            "created": str(order.created),
            "state": str(order.state)
        }

        # Get eshop info
        general = conf["general"]

        # Get number of items in cart
        if 'cart' in session:
            cart_state = len(session["cart"])

        else:
            session["cart"] = [] 

            cart_state = len(session["cart"])

        return render_template("/shop/tracking.html", order=order, general=general, cart_state=cart_state)

    else:
        return abort(400)




# Actions:
# This routes are meant to do a certain action
# when requested.


# 'add-to-cart' - Adds ?item into session["cart"]
# 'empty-cart' - Pops the 'cart' out of session
# 'add-promo' - Adds promo code to session 'promos'
# 'create-order'
@app.route("/do/<action>", methods=["GET", "POST"])
def page_do(action):
    #Check which action is requested.
    if action == "add-to-cart":
    
        try:

            # Check item 'visibility'
            product = Product(str(request.args["item"]))

            if product.visibility == "TRUE":
        
        
                # If 'cart' already exists, add the new item into it. 
                if "cart" in session:

                    session["cart"] += [str(request.args["item"])]

                # If 'cart' does not yet exist, create the record in session.
                else:
                    session["cart"] = [str(request.args["item"])]

                
                return redirect("/cart")

            else:
                return abort(400)


        except:
            return abort(400)
        




    elif action == "empty-cart":
        # Delete the 'cart' from session
        session.pop("cart", None)
        session.pop("promos", None)


        return redirect("/cart")





    elif action == "add-promo":
        promo = Promo(str(request.args["code"]))

        if promo.query != None:

            try:
                # If 'promos' already exists, add the new item into it. 
                if "promos" in session:

                    # Check if promo code is already in session 
                    # -> Cannot use same code more than once

                    check = str(promo.code) in session["promos"]
                    
                    if check == False:
                        session["promos"] += [str(promo.code)]

                # If 'promos' does not yet exist, create the record in session.
                else:
                    session["promos"] = [str(promo.code)]

                
                return redirect("/cart")


            except:
                return abort(400)

        else:
            return redirect("/cart")

    



    elif action == "create-order":
        if 'cart' in session and len(session["cart"]) != 0:
            try:
                # This is copied code from /cart - Need to have exact price
                # and this looked like the best solution

                items = []

                # For item in 'cart' set an object and get
                # required info about the item.
                # Save it then as a dictionary and put it along 
                # with the other items into a list 'items' 
                if 'cart' in session:
                    for item in session["cart"]:
                        x = Product(item)

                        items += [
                            {"name": x.name,
                            "price": x.price,
                            "slug": item}
                    ]

                else:
                    session["cart"] = []

                # Do the same for promo codes

                discounts = []

                if 'promos' in session:
                    for item in session["promos"]:
                        x = Promo(item)

                        discounts += [
                            {"name": x.name,
                            "discount": x.discount}
                    ]

                # Calculate the total price (shipping included)
                total = float(conf["general"]["shipping-price"])

                # Get prices for all items
                for item in items:
                    total += float(item["price"])

                # Add discounts
                for item in discounts:
                    total -= float(item["discount"])

                # If total is lower than 0 (due to promo codes),
                # set it to total = 0
                if total < 0:
                    total = 0


                # Round total so it does not create numbers with
                # too many floating points
                total = round(total, 2)


                
                
                # Create new order using 'order' class
                new_order = Order("not assigned")

                new_order.create_order(
                    str(request.form["name"]),
                    str(request.form["email"]),
                    str(request.form["phone"]),

                    str(request.form["street"]),
                    str(request.form["apartment"]),
                    str(request.form["city"]),
                    str(request.form["postcode"]),
                    str(request.form["country"]),

                    session["cart"],
                    str(total)
                )

                session["cart"] = []

                return redirect("/message?h=THANK YOU&m=YOUR ORDER HAS BEEN SUCCESSFULLY CREATED")
        
            except:
                return redirect("/message?h=WE ARE SORRY&m=BUT SOMETHING WENT WRONG")

        else:
            return abort(400)








# Affiliate links
# Adds visit to corresponding campaign in DB
# and redirects to homepage
@app.route("/affiliate/<campaign>")
def page_affiliate(campaign):
    campaign_object = Affiliate(str(campaign))

    if campaign_object.add_visit() == True:
        return redirect("/")

    else:
        return abort(404)






"""
HERE STARTS THE VIEWS FOR THE ADMIN SECTION
"""

# All admin related stuff is hosted on subdomain 'admin'
# meaning in can be accessed on 'www.admin.<your-domain>.com'



# Admin Dashboard
@app.route("/admin")
def page_admin():

    if 'username' in session:
        # Get eshop info
        general = conf["general"]
        # Get username
        logged_name = session.get("username")



        # Get Analytics Data

        # PROFIT AND ORDERS
        
        profit_today = 0
        profit_month = 0

        orders_today = 0
        orders_month = 0

        today = str(current_date()).split("-")[1] + "-" + str(str(current_date()).split("-")[2]).split(" ")[0]

        for order in orders.find({}):
            order_date = str(order["created"]).split("-")[1] + "-" + str(str(order["created"]).split("-")[2]).split(" ")[0]

            if order_date  == today:
                profit_today += float(order["price"])
                
                orders_today += 1

            if order_date.split("-")[0] == today.split("-")[0]:
                profit_month += float(order["price"])
                
                orders_month += 1

        
        # VISITS

        visits_today = 0
        visits_month = 0

        for visit in visits.find({}):
            visit_date = str(visit["date"]).split("-")[1] + "-" + str(str(visit["date"]).split("-")[2]).split(" ")[0]

            if visit_date == today:
                visits_today += 1

            if visit_date.split("-")[0] == today.split("-")[0]:
                visits_month += 1


        # Round profits 
        profit_today = round(profit_today, 2)
        profit_month = round(profit_month, 2)

        return render_template("/admin/index.html", general=general, logged_name=logged_name,
        profit_month=profit_month, profit_today=profit_today,
        orders_today=orders_today, orders_month=orders_month,
        visits_today=visits_today, visits_month=visits_month)

    else:
        return redirect("/login")



# Admin pages
# All pages are server within one function

# 'Orders' - Gives you a list of all orders
# 'Products' - Shows list of all products + allow to create new ones
# 'Promo Codes'
# 'Users' - Allow you create/delete accounts
# 'Affiliates'
@app.route("/admin/<page>")
def page_adminpages(page):
    # Check if person is logged in, else prompt them to auth
    if 'username' in session:
        # Get eshop info
        general = conf["general"]
        # Get username
        logged_name = session.get("username")


        # Serve pages by request
        if page == 'orders':

            # Get all orders
            all_orders = []

            # Check for query parameters
            params = request.args.get("q", None)

            if params != None:
                search_params = {"state": str(params)}

            else:
                search_params = {}  

            for item in orders.find(search_params):
                item = Order(item["order-id"])

                # Get products for that order
                order_products = []
                for product in item.products:

                    product = Product(product)

                    order_products += [{
                        "name": product.name,
                        "price": product.price,
                        "slug": product.slug
                    }]

                all_orders = [{
                "order-id": str(item.order_id),

                "name": str(item.name),
                "email": str(item.email),
                "phone": str(item.phone),
                
                "street": str(item.street),
                "apartment": str(item.apartment),
                "city": str(item.city),
                "postcode": str(item.postcode),
                "country": str(item.country),

                "products": order_products,
                "price": str(item.price),

                "state": str(item.state),
                "created": str(item.created),
                "last-change": str(item.last_change),
                "changed-by": str(item.changed_by)
            }] + all_orders

            return render_template("/admin/orders.html", general=general, logged_name=logged_name, all_orders=all_orders)


        elif page == "products":
            # Get all products
            all_products = []

             # Check for query parameters
            params = request.args.get("q", None)

            if params != None:
                search_params = {"tag": str(params)}

            else:
                search_params = {}  

            for product in products.find(search_params):
                product = Product(product["slug"])

                all_products = [{
                    "name": str(product.name),
                    "price": str(product.price),
                    "slug": str(product.slug),
                    "tag": str(product.tag),
                    "visibility": str(product.visibility)
                }] + all_products

            # Get all tags
            all_tags = general["product-categories"]


            return render_template("/admin/products.html", general=general, logged_name=logged_name, all_products=all_products, all_tags=all_tags)


        elif page == "promo-codes":

            all_promos = []

            for promo in promos.find({}):
                
                all_promos = [{
                    "name": promo["name"],
                    "code": promo["code"],
                    "discount": promo["discount"]
                }] + all_promos

            
            return render_template("/admin/promo-codes.html", general=general, logged_name=logged_name, all_promos=all_promos)




        elif page == "users":
            # Get all users
            all_users = []

            for user in users.find({}):
                all_users += [user["username"]]


            return render_template("/admin/users.html", general=general, logged_name=logged_name, all_users=all_users)




        elif page == "affiliates":
            all_affiliates = []

            for affiliate in affiliates.find({}):
                
                all_affiliates = [{
                    "campaign": affiliate["campaign"],
                    "visits": affiliate["visits"],
                }] + all_affiliates
            return render_template("/admin/affiliates.html", general=general, logged_name=logged_name, all_affiliates=all_affiliates)


    else:
        return redirect("/login")




# '/admindo' - Functions handler for admin panel

# 'logout' - Self explanitory
# 'handle-order' - Change order' current status
# 'create-product' - Creates new product

# 'change-product-visibility' - 
    # Changes product visibility - True/False
    # This way you can turn the product off without deleting 
    # it from the db -> Can be still accessed by order's query 

# 'create-promo'    
# 'delete-promo'
# 'create-user'
# 'delete-user'
# 'create-affiliate'
# 'delete-affiliate'
@app.route("/admindo/<action>", methods=["POST", "GET"])
def page_admindo(action):
    if 'username' in session:
        if action == 'handle-order':
            handled_order = Order(request.args["id"])

            handle = handled_order.update_state(
                str(request.args["state"]),
                str(session["username"])
            )

            if handle == True:
                return redirect(request.referrer)

            else:
                return abort(400)

        elif action == 'create-product':
            new_product = Product(str(request.form["slug"]))

            handle = new_product.create_product(
                str(request.form["name"]),
                str(request.form["description"]),
                str(request.form["price"]),
                str(request.form["tag"]),
                str(request.form["picture"])
            )

            if handle == True:
                return redirect(request.referrer)

            else:
                return abort(400)

        
        elif action == 'change-product-visibility':
            product_slug = request.args.get("slug", None)
            state = request.args.get("state", None)
        
            if product_slug != None and state != None:
        
                product = Product(str(product_slug))
        
                changed_product = product.change_product_visibility(state)
        
                if changed_product == True:
                    return redirect(request.referrer)
        
                else:
                    return abort(400) 
        
        


        elif action == 'create-promo':
            new_promo = Promo(str(request.form["code"]))

            create_promo = new_promo.create_promo(
                str(request.form["name"]),
                str(request.form["discount"])
            )

            if create_promo == True:
                return redirect(request.referrer)

            else:
                return abort(400)

        



        elif action == 'delete-promo':
            promo_code = request.args.get("code", None)
        
            if promo_code != None:
        
                promo = Promo(str(promo_code))
        
                delete_promo = promo.delete_promo()
        
                if delete_promo == True:
                    return redirect(request.referrer)
        
                else:
                    return abort(400) 



        elif action == "delete-user":
            username = request.args.get("username", None)

            if username != None:
                try:
                    users.delete_one({"username": str(username)})

                    return redirect(request.referrer)

                except:
                    return abort(400)

            else:
                return abort(400)





        elif action == "create-user":
            username = request.form["username"]

            if username != None:
                new_user = User(username)

                if new_user.create_user(request.form["password"]) == True:
                    
                    return redirect(request.referrer)

                else:
                    return abort(400)

            else: 
                return abort(400)



    

        elif action == "create-affiliate":
            try:
                new_campaign = Affiliate(str(request.form["campaign"])) 

                if new_campaign.create_campaign() == True:

                    return redirect(request.referrer)

                else:
                    return abort(400)

            except:
                return abort(400)

    



        elif action == "delete-affiliate":

            campaign = Affiliate(str(request.args.get("campaign", None)))

            if campaign.delete_affiliate() == True:
                
                return redirect(request.referrer)

            else:
                return abort(400)







        elif action == 'logout':
            session.pop("username", None)

            return redirect("/login")


    else:
        return abort(401)






# Login
# Uses shop' css file!!! (/static/css/shop.css)
@app.route("/login", methods=["POST", "GET"])
def page_login():

    if request.method == "POST":
        usr = User(str(request.form["username"]))

        check = usr.auth(str(request.form["password"]))

        if check == True:
            # Create record in session
            session["username"] = usr.username

            return redirect("/admin")

        else:
            abort(401)

    else:

        # Get eshop info
        general = conf["general"]


        # Create new user if no users are in DB
        if users.count() == 0:
            first_user = User("Admin")

            first_user.create_user("myeshop")

        # Get number of items in cart
        if 'cart' in session:
            cart_state = len(session["cart"])

        else:
            session["cart"] = [] 

            cart_state = len(session["cart"])

        return render_template("/admin/login.html", general=general, cart_state=cart_state)



"""
HERE ENDS THE VIEWS SETUP
"""





# Run the app
while __name__ == "__main__":

    # CHANGE THIS IN PRODUCTION !!!
    # Use server name to 'lvh.me' to be able to access subdomains on localhost
    # app.config["SERVER_NAME"] = "lvh.me:5000"


    # In production set 'Debug' to 'False'
    app.run(
        debug=False
    )