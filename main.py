import random
import config

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''
app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = random.choice(result)
    # Simply convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def all_cafe():
    all_cafe_list = []
    result = db.session.execute(db.select(Cafe)).scalars().all()
    for item in result:
        all_cafe_list.append(item.to_dict())
    return jsonify(cafes=all_cafe_list)


# HTTP GET - Read Record
@app.route("/search",  methods=["GET"])
def search():
    loc_cafe_list = []
    cafe_loc = request.args.get('loc')
    result = db.session.execute(db.select(Cafe).where(Cafe.location == cafe_loc)).scalars().all()
    if not result:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404
    for item in result:
        loc_cafe_list.append(item.to_dict())
    return jsonify(cafes=loc_cafe_list)


# HTTP POST - Create Record
@app.route("/add",  methods=["POST"])
def add_cafe():
    name = request.form.get('name')
    map_url = request.form.get('map_url')
    img_url = request.form.get('img_url')
    location = request.form.get('location')
    seats = request.form.get('seats')
    has_toilet = bool(request.form.get('has_toilet'))
    has_wifi = bool(request.form.get('has_wifi'))
    has_sockets = bool(request.form.get('has_sockets'))
    can_take_calls = bool(request.form.get('can_take_calls'))
    coffee_price = request.form.get('coffee_price')
    new_cafe = Cafe(name=name, map_url=map_url, img_url=img_url, location=location, seats=seats,
                    has_toilet=has_toilet, has_wifi=has_wifi, has_sockets=has_sockets, can_take_calls=can_take_calls,
                    coffee_price=coffee_price)
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>",  methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get('new_price')
    cafe_to_update = db.session.get(Cafe, cafe_id)
    if not cafe_to_update:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found."}), 404
    cafe_to_update.coffee_price = new_price
    db.session.commit()
    return jsonify(response={"success": "Successfully updated coffee price."}), 200


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    if config.API_KEY == request.args.get('api-key'):
        cafe_to_delete = db.session.get(Cafe, cafe_id)
        if not cafe_to_delete:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found."}), 404
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
    else:
        return jsonify({"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
