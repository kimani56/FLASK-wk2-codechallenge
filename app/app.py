#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api,Resource, reqparse
from models import Hero, Power, HeroPower
from flask_cors import CORS

from models import db, Hero


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

CORS(app)

class Home(Resource):
    def get(self):
        response_dict = {
            "message" : "Welcome to my Flask Code Challenge - Heroes"
        }
        response = make_response(response_dict, 200)

        return response
    
api.add_resource(Home, '/')

hero_power_parser = reqparse.RequestParser()
hero_power_parser.add_argument('strength', type=str, choices=('Strong', 'Weak', 'Average'), required=True)
hero_power_parser.add_argument('power_id', type=int, required=True)
hero_power_parser.add_argument('hero_id', type=int, required=True)

class HeroesResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        hero_list = [
            {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name
            }
            for hero in heroes
        ]
        return make_response(jsonify(hero_list), 200)

class HeroResource(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if hero is None:
            return {"error": "Hero not found"}, 404
        
        powers = [
            {
                "id": power.id,
                "name": power.name,
                "description": power.description
            }
            for power in hero.powers
        ]

        hero_info = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
            "powers": powers
        }
        return make_response(jsonify(hero_info), 200)

class PowersResource(Resource):
    def get(self):
        powers = Power.query.all()
        power_list = [
            {
                "id": power.id,
                "name": power.name,
                "description": power.description
            }
            for power in powers
        ]
        return make_response(jsonify(power_list), 200)

class PowerResource(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if power is None:
            return {"error": "Power not found"}, 404

        power_info = {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
        return make_response(jsonify(power_info), 200)

class UpdatePowerResource(Resource):
    def patch(self, id):
        power = Power.query.get(id)
        if power is None:
            return {"error": "Power not found"}, 404

        data = request.get_json()
        description = data.get("description")

        if description and len(description) >= 20:
            power.description = description
            db.session.commit()
            return {
                "id": power.id,
                "name": power.name,
                "description": power.description
            }
        else:
            return {"errors": ["validation errors"]}, 400

class HeroPowersResource(Resource):
    def post(self):
        data = hero_power_parser.parse_args()
        strength = data["strength"]
        power_id = data["power_id"]
        hero_id = data["hero_id"]

        hero = Hero.query.get(hero_id)
        power = Power.query.get(power_id)

        if hero is None or power is None:
            return {"error": "Hero or Power not found"}, 404

        if strength in ['Strong', 'Weak', 'Average']:
            hero_power = HeroPower(strength=strength, hero=hero, power=power)
            db.session.add(hero_power)
            db.session.commit()

            # Re-fetch hero with updated powers
            updated_hero = Hero.query.get(hero_id)
            powers = [
                {
                    "id": power.id,
                    "name": power.name,
                    "description": power.description
                }
                for power in updated_hero.powers
            ]

            hero_info = {
                "id": updated_hero.id,
                "name": updated_hero.name,
                "super_name": updated_hero.super_name,
                "powers": powers
            }
            return make_response(jsonify(hero_info), 200)
        else:
            return {"errors": ["validation errors"]}, 400

# Add routes to the API
api.add_resource(HeroesResource, '/heroes')
api.add_resource(HeroResource, '/heroes/<int:id>')
api.add_resource(PowersResource, '/powers')
api.add_resource(PowerResource, '/powers/<int:id>')
api.add_resource(UpdatePowerResource, '/powers/<int:id>')
api.add_resource(HeroPowersResource, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555)
