import pusher
import os
from database import db_session
from flask import Flask, request, jsonify, render_template, redirect
from models import Ingredient, Product
from search import init_search, ingredient_search, product_search, ingredients_processing

app = Flask(__name__)

pusher_client = pusher.Pusher(
    app_id=u'699311',
    key=u'146c752d46a28d41c1df',
    secret=u'ff2867c3e5f2de78a65e',
    cluster=u'us2',
    ssl=True)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

def dropdown():
    brands=['Clarins','Peter Thomas']
    product=['multi vitamine','cleanser']


@app.route('/backend', methods=["POST", "GET"])
def backend():
    if request.method == "POST":
        search_brand = request.form["brand"]
        search_name = request.form["name"]
        es = init_search()
        product_result = product_search(search_brand, search_name, es)
        if product_result:
            brand = product_result[0]
            product_name = product_result[1]
            ing_raw = product_result[2]
            listPrice = product_result[3]
            size=product_result[4]
            rating=product_result[5]
        else:
            brand =  product_name = ing_raw = listPrice = size = rating = None
        
        ing_clean_list = ingredients_processing(ing_raw)
        ing_name_list=[]
        ing_safety_list=[]      
        
        for ing in ing_clean_list:
            ing_result = ingredient_search(ing, es)
            if ing_result:
                ing_name = ing_result[0]
#                 about =ing_result[1]
                ing_safety = ing_result[2]
#                 function =ing_result[3]
                ing_name_list.append(ing_name)
                ing_safety_list.append(ing_safety)
            else:
                  ing_name = ing_safety = None
           #new_ingredient = Ingredient(name, about, safety, function)
            
        
        ing_name_string=",".join(ing_name_list)
        lowest_safety=min(ing_safety_list)
         
        new_product = Product(brand, product_name, ing_name_string, lowest_safety,listPrice,size,rating)
        db_session.add(new_product)
        db_session.commit()
          
        data_product = {
            "brand": new_product.brand,
            "product_name": new_product.product_name,
            "ingredients": new_product.ingredients,
            "safety_score": new_product.safety_score,
            "listPrice": new_product.listPrice,
            "size":new_product.size,
            "rating":new_product.rating
            }

        print(data_product)
        pusher_client.trigger('table', 'new-record', {'data': data_product })
        return redirect("/backend", code=302)
    else:
        products = Product.query.all()
        return render_template('backend.html', products=products)

# @app.route('/ing', methods=["POST", "GET"])
# def ingredient():
#     if request.method == "POST":
#         search_name = request.form["ingredient"]
#         es = init_search()
#         result = ingredient_search(search_name, es)
#         if result:
#             name = result[0]
#             about = result[1]
#             safety = result[2]
#             function = result[3]
#         else:
#             name = about = safety = function = None

#         print(name)
#         print("foo0 " + about)
#         new_ingredient = Ingredient(name, about, safety, function)
#         print("foo1 " + about)
#         db_session.add(new_ingredient)
#         print("foo2 " + about)
#         db_session.commit()

#         data = {
#             "name": new_ingredient.name,
#             "about": new_ingredient.about,
#             "safety": new_ingredient.safety,
#             "function": new_ingredient.function,
#             }

#         print(data)
#         pusher_client.trigger('table', 'new-record', {'data': data })

#         return redirect("/ing", code=302)
#     else:
#         ingredients = Ingredient.query.all()
#         return render_template('backend_ing.html', ingredients=ingredients)

#@app.route('/edit/<int:id>', methods=["POST", "GET"])
#def update_record(id):
#    if request.method == "POST":
#        flight = request.form["flight"]
#        destination = request.form["destination"]
#        check_in = datetime.strptime(request.form['check_in'], '%d-%m-%Y %H:%M %p')
#        departure = datetime.strptime(request.form['departure'], '%d-%m-%Y %H:%M %p')
#        status = request.form["status"]
#
#        update_flight = Flight.query.get(id)
#        update_flight.flight = flight
#        update_flight.destination = destination
#        update_flight.check_in = check_in
#        update_flight.departure = departure
#        update_flight.status = status
#
#        db_session.commit()
#
#        data = {
#            "id": id,
#            "flight": flight,
#            "destination": destination,
#            "check_in": request.form['check_in'],
#            "departure": request.form['departure'],
#            "status": status}
#
#        pusher_client.trigger('table', 'update-record', {'data': data })
#
#        return redirect("/
#", code=302)
#    else:
#        new_flight = Flight.query.get(id)
#        new_flight.check_in = new_flight.check_in.strftime("%d-%m-%Y %H:%M %p")
#        new_flight.departure = new_flight.departure.strftime("%d-%m-%Y %H:%M %p")
#
#        return render_template('update_flight.html', data=new_flight)

# run Flask app
if __name__ == "__main__":
    app.run()
