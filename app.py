from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokemon.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    hp = db.Column(db.Integer)
    defense = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    ability = db.Column(db.String(50))
    image_url = db.Column(db.String(255))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/pokemon', methods=['GET', 'POST'])
def pokemon():
    if request.method == 'POST':
        pokemon_name = request.form['pokemon_name']
        pokemon_data = get_pokemon_data(pokemon_name)

        if not pokemon_data:
            flash('Pokemon not found!', 'error')
        else:
            save_pokemon_to_db(pokemon_data)
            flash('Pokemon information saved!', 'success')

    return render_template('pokemon.html')

def get_pokemon_data(pokemon_name):
    api_url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}'
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        pokemon_data = {
            'name': data['name'],
            'hp': data['stats'][0]['base_stat'],
            'defense': data['stats'][2]['base_stat'],
            'attack': data['stats'][1]['base_stat'],
            'ability': data['abilities'][0]['ability']['name'],
            'image_url': data['sprites']['front_shiny'],
        }
        return pokemon_data
    else:
        return None

def save_pokemon_to_db(pokemon_data):
    existing_pokemon = Pokemon.query.filter_by(name=pokemon_data['name']).first()

    if not existing_pokemon:
        new_pokemon = Pokemon(
            name=pokemon_data['name'],
            hp=pokemon_data['hp'],
            defense=pokemon_data['defense'],
            attack=pokemon_data['attack'],
            ability=pokemon_data['ability'],
            image_url=pokemon_data['image_url']
        )
        db.session.add(new_pokemon)
        db.session.commit()

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
