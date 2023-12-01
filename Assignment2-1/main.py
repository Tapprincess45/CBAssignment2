#Courtney Buxton
#1/12/2023


from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import requests
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather_data.db'
db = SQLAlchemy(app)

bot = ChatBot('TravelBot')
trainer = ChatterBotCorpusTrainer(bot)

# Train the chatbot with the English language corpus data
trainer.train('chatterbot.corpus.english')

itinerary_locations = [
    'Corfe Castle', 'The Cotswolds', 'Cambridge', 'Bristol', 'Oxford', 'Norwich', 'Stonehenge', 'Watergate Bay', 'Birmingham'
]

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=False)
    data = db.Column(db.Text, nullable=False)

db.create_all()

@app.route("/")
def home():
    return render_template("index.html", locations=itinerary_locations)

@app.route("/get_weather", methods=['POST'])
def get_weather():
    user_message = request.form['user_message']
    bot_response = bot.get_response(user_message)

    if any(location.lower() in user_message.lower() for location in itinerary_locations):
        weather_data = get_weather_data(user_message)
        save_weather_data(user_message, weather_data)
        return render_template("index.html", user_message=user_message, bot_response=str(bot_response), weather_data=weather_data)

    return render_template("index.html", user_message=user_message, bot_response=str(bot_response))

def get_weather_data(location):
    
    api_key = '69eaaf2d910d58cf89290bca4fdf7461'
    base_url = 'http://api.openweathermap.org/data/2.5/forecast'
    params = {'q': location, 'appid': api_key, 'units': 'metric'}  

    response = requests.get(base_url, params=params)
    weather_data = json.loads(response.text)

    return weather_data

def save_weather_data(location, data):
    weather_entry = WeatherData(location=location, data=json.dumps(data))
    db.session.add(weather_entry)
    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
