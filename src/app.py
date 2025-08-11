import os
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db, Person, Planet, User, Favorite

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///yourdb.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

CURRENT_USER_ID = 1  # Simulated logged-in user

# -------------------------
# GET Endpoints
# -------------------------

@app.route('/people', methods=['GET'])
def get_people():
    people = Person.query.all()
    results = [{
        "id": p.id,
        "name": p.name,
        "species": p.species,
        "homeworld": p.homeworld
    } for p in people]
    return jsonify(results), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Person.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404
    return jsonify({
        "id": person.id,
        "name": person.name,
        "species": person.species,
        "homeworld": person.homeworld
    }), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    results = [{
        "id": pl.id,
        "name": pl.name,
        "climate": pl.climate,
        "terrain": pl.terrain
    } for pl in planets]
    return jsonify(results), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify({
        "id": planet.id,
        "name": planet.name,
        "climate": planet.climate,
        "terrain": planet.terrain
    }), 200

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    results = [{"id": u.id, "email": u.email} for u in users]
    return jsonify(results), 200

@app.route('/users/favorites', methods=['GET'])
def get_current_user_favorites():
    user = User.query.get(CURRENT_USER_ID)
    if not user:
        return jsonify({"error": "User not found"}), 404

    favs = []
    for fav in user.favorites:
        if fav.item_type == 'planet':
            item = Planet.query.get(fav.item_id)
            if item:
                favs.append({"type": "planet", "id": item.id, "name": item.name})
        elif fav.item_type == 'people':
            item = Person.query.get(fav.item_id)
            if item:
                favs.append({"type": "people", "id": item.id, "name": item.name})

    return jsonify(favs), 200

# -------------------------
# Favorites Endpoints
# -------------------------

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user = User.query.get(CURRENT_USER_ID)
    if not user:
        return jsonify({"error": "User not found"}), 404
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    existing = Favorite.query.filter_by(user_id=user.id, item_type='planet', item_id=planet_id).first()
    if existing:
        return jsonify({"message": "Planet already in favorites"}), 400

    fav = Favorite(user_id=user.id, item_type='planet', item_id=planet_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"message": f"Planet {planet.name} added to favorites"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user = User.query.get(CURRENT_USER_ID)
    if not user:
        return jsonify({"error": "User not found"}), 404
    person = Person.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    existing = Favorite.query.filter_by(user_id=user.id, item_type='people', item_id=people_id).first()
    if existing:
        return jsonify({"message": "Person already in favorites"}), 400

    fav = Favorite(user_id=user.id, item_type='people', item_id=people_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"message": f"Person {person.name} added to favorites"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user = User.query.get(CURRENT_USER_ID)
    if not user:
        return jsonify({"error": "User not found"}), 404

    fav = Favorite.query.filter_by(user_id=user.id, item_type='planet', item_id=planet_id).first()
    if not fav:
        return jsonify({"error": "Favorite planet not found"}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite planet removed"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user = User.query.get(CURRENT_USER_ID)
    if not user:
        return jsonify({"error": "User not found"}), 404

    fav = Favorite.query.filter_by(user_id=user.id, item_type='people', item_id=people_id).first()
    if not fav:
        return jsonify({"error": "Favorite person not found"}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite person removed"}), 200

# -------------------------
# People CRUD Endpoints
# -------------------------

@app.route('/people', methods=['POST'])
def create_person():
    data = request.get_json()
    if not data or not all(k in data for k in ("name", "species", "homeworld")):
        return jsonify({"error": "Missing data"}), 400
    person = Person(name=data["name"], species=data["species"], homeworld=data["homeworld"])
    db.session.add(person)
    db.session.commit()
    return jsonify({"message": "Person created", "id": person.id}), 201

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    person = Person.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400
    person.name = data.get("name", person.name)
    person.species = data.get("species", person.species)
    person.homeworld = data.get("homeworld", person.homeworld)
    db.session.commit()
    return jsonify({"message": "Person updated"}), 200

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    person = Person.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404
    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": "Person deleted"}), 200

# -------------------------
# Planets CRUD Endpoints
# -------------------------

@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    if not data or not all(k in data for k in ("name", "climate", "terrain")):
        return jsonify({"error": "Missing data"}), 400
    planet = Planet(name=data["name"], climate=data["climate"], terrain=data["terrain"])
    db.session.add(planet)
    db.session.commit()
    return jsonify({"message": "Planet created", "id": planet.id}), 201

@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400
    planet.name = data.get("name", planet.name)
    planet.climate = data.get("climate", planet.climate)
    planet.terrain = data.get("terrain", planet.terrain)
    db.session.commit()
    return jsonify({"message": "Planet updated"}), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": "Planet deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)
