import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import logging

app = Flask(__name__)
CORS(app)

mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongo:27017/')
client = MongoClient(mongo_uri)
db = client['booking_db']
collection = db['bookings']

logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    name = request.form.get('name')
    hour = request.form.get('hour')
    reason = request.form.get('reason')

    if not name or not hour or not reason:
        logging.warning('Validation error: All fields are required!')
        return render_template('error.html', error="All fields are required!")

    if collection.find_one({'hour': hour}):
        logging.warning(f'Hour {hour} is already booked!')
        return render_template('error.html', error="This hour is already booked!")

    booking_data = {
        'name': name,
        'hour': hour,
        'reason': reason
    }
    result = collection.insert_one(booking_data)
    logging.info(f'Booking successful: {result.inserted_id}')

    bookings = collection.find()
    bookings_list = [{'id': str(booking['_id']), 'name': booking['name'], 'hour': booking['hour'], 'reason': booking['reason']} for booking in bookings]
    return render_template('bookings.html', bookings=bookings_list)

@app.route('/bookings')
def get_bookings():
    bookings = collection.find()
    bookings_list = [{'id': str(booking['_id']), 'name': booking['name'], 'hour': booking['hour'], 'reason': booking['reason']} for booking in bookings]
    return render_template('bookings.html', bookings=bookings_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
