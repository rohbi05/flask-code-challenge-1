#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower  # Ensure your models are imported correctly
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def heroes():
    heroes = [hero.to_dict(only=('id', 'name', 'super_name')) for hero in Hero.query.all()]
    return make_response(heroes, 200)

@app.route('/heroes/<int:id>', methods=['GET'])
def heroes_by_id(id):
    hero = Hero.query.get(id)
    if not hero:
        return make_response({"error": "Hero not found"}, 404)
    
    return make_response(hero.to_dict(), 200)

@app.route('/powers', methods=['GET'])
def powers():
    powers = [power.to_dict(only=('description', 'id', 'name')) for power in Power.query.all()]
    return make_response(powers, 200)

@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def powers_by_id(id):
    power = Power.query.get(id)
    if not power:
        return make_response({"error": "Power not found"}, 404)
    
    if request.method == 'GET':
        return make_response(power.to_dict(only=('description', 'id', 'name')), 200)

    elif request.method == 'PATCH':
        validation_errors = []

        # Update power attributes and validate
        if 'description' in request.json:
            description_value = request.json['description']
            if not isinstance(description_value, str) or len(description_value) < 20:
                validation_errors.append("Description must be a string with at least 20 characters.")

        # Update valid fields
        for attr in request.json:
            if attr != 'description':  # Skip description if it's invalid
                setattr(power, attr, request.json[attr])

        # If there are validation errors, return a standardized error response
        if validation_errors:
            return make_response({"errors": validation_errors}, 400)  # Bad Request status code

        # Update the description if it's valid
        if 'description' in request.json:
            power.description = request.json['description']

        db.session.commit()
        return make_response(power.to_dict(), 200)

@app.route('/hero_powers', methods=['GET', 'POST'])
def hero_powers():
    if request.method == 'GET':
        hero_power = HeroPower.query.all()
        return make_response([hp.to_dict() for hp in hero_power], 200)

    elif request.method == 'POST':
        strength = request.json.get('strength')
        power_id = request.json.get('power_id')
        hero_id = request.json.get('hero_id')

        # Validate strength
        valid_strengths = {'Strong', 'Weak', 'Average'}
        if strength not in valid_strengths:
            return make_response({"errors": ["Strength must be one of: Strong, Weak, Average."]}, 400)

        # Create a new HeroPower instance
        new_power = HeroPower(
            strength=strength,
            power_id=power_id,
            hero_id=hero_id
        )

        # Commit changes
        db.session.add(new_power)
        db.session.commit()

        return make_response(new_power.to_dict(), 200)  

# Main entry point
if __name__ == '__main__':
    app.run(port=5555, debug=True)
