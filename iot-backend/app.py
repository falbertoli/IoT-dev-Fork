from flask import Flask, jsonify
import requests
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# config for multiple locations and sensors
locations = {
    'location_1': {
        'indoor': {'sensor_name': 'A', 'channel_id': 2580816},
        'outdoor': {'sensor_name': 'B', 'channel_id': 2099116}
    }
}

fields = {
    'co2': 4,
    'temperature': 5,
    'humidity': 6,
    'pressure': 7
}

read_api_key = 'XHA11H2XAGGWMDY1'
num_results = 8000

# fetch data from ThingSpeak
def fetch_data_from_thingspeak(channel_id, field):
    url = f"https://api.thingspeak.com/channels/{channel_id}/fields/{field}.json?results={num_results}&api_key={read_api_key}"
    response = requests.get(url)
    data = response.json()
    feeds = data['feeds']

    df = pd.DataFrame(feeds)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['value'] = pd.to_numeric(df[f'field{field}'], errors='coerce')
    df = df.dropna()
    
    return df

# compute delta between indoor and outdoor data for a given location
def compute_delta(location, field):
    indoor_channel_id = locations[location]['indoor']['channel_id']
    outdoor_channel_id = locations[location]['outdoor']['channel_id']

    indoor_data = fetch_data_from_thingspeak(indoor_channel_id, field)
    outdoor_data = fetch_data_from_thingspeak(outdoor_channel_id, field)

    # find the common time range
    start_date = max(indoor_data['created_at'].min(), outdoor_data['created_at'].min())
    end_date = min(indoor_data['created_at'].max(), outdoor_data['created_at'].max())

    # trim the data to the common time range
    indoor_data = indoor_data[(indoor_data['created_at'] >= start_date) & (indoor_data['created_at'] <= end_date)]
    outdoor_data = outdoor_data[(outdoor_data['created_at'] >= start_date) & (outdoor_data['created_at'] <= end_date)]

    # resample the data to hourly frequency
    indoor_data_resampled = indoor_data.set_index('created_at').resample('1h').mean(numeric_only=True).interpolate().reset_index()
    outdoor_data_resampled = outdoor_data.set_index('created_at').resample('1h').mean(numeric_only=True).interpolate().reset_index()

    # merge the data
    merged_data = pd.merge(indoor_data_resampled, outdoor_data_resampled, on='created_at', suffixes=('_indoor', '_outdoor'))
    merged_data['delta'] = merged_data['value_indoor'] - merged_data['value_outdoor']

    return merged_data

# API to get data for a single sensor (either indoor or outdoor)
@app.route('/api/data/<string:location>/<string:sensor_type>/<string:indoor_or_outdoor>')
def get_single_sensor_data(location, sensor_type, indoor_or_outdoor):
    if location not in locations:
        return jsonify({'error': 'Invalid location'}), 400
    if sensor_type not in fields:
        return jsonify({'error': 'Invalid sensor type'}), 400
    if indoor_or_outdoor not in ['indoor', 'outdoor']:
        return jsonify({'error': 'Invalid sensor specifier, choose "indoor" or "outdoor"'}), 400

    # Get the correct channel_id
    channel_info = locations[location].get(indoor_or_outdoor)
    if not channel_info:
        return jsonify({'error': f'{indoor_or_outdoor} sensor not found for {location}'}), 404

    field = fields[sensor_type]
    data = fetch_data_from_thingspeak(channel_info['channel_id'], field)

    return jsonify({
        'timestamps': data['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'values': data['value'].tolist()
    })

# Compute delta between indoor and outdoor data for a given location
@app.route('/api/delta/<string:location>/<string:sensor_type>')
def get_delta(location, sensor_type):
    if location not in locations:
        return jsonify({'error': 'Invalid location'}), 400
    if sensor_type not in fields:
        return jsonify({'error': 'Invalid sensor type'}), 400

    location_data = locations[location]
    indoor_info = location_data.get('indoor')
    outdoor_info = location_data.get('outdoor')

    if not indoor_info or not outdoor_info:
        return jsonify({'error': 'Both indoor and outdoor sensors are required for delta calculation'}), 400

    field = fields[sensor_type]

    # Fetch indoor and outdoor data
    indoor_data = fetch_data_from_thingspeak(indoor_info['channel_id'], field)
    outdoor_data = fetch_data_from_thingspeak(outdoor_info['channel_id'], field)

    # Find the common time range
    start_date = max(indoor_data['created_at'].min(), outdoor_data['created_at'].min())
    end_date = min(indoor_data['created_at'].max(), outdoor_data['created_at'].max())

    # Trim the data to the common time range
    indoor_data = indoor_data[(indoor_data['created_at'] >= start_date) & (indoor_data['created_at'] <= end_date)]
    outdoor_data = outdoor_data[(outdoor_data['created_at'] >= start_date) & (outdoor_data['created_at'] <= end_date)]

    # Resample the data to hourly frequency
    indoor_data_resampled = indoor_data.set_index('created_at').resample('1h').mean(numeric_only=True).interpolate().reset_index()
    outdoor_data_resampled = outdoor_data.set_index('created_at').resample('1h').mean(numeric_only=True).interpolate().reset_index()

    # Merge the data
    merged_data = pd.merge(indoor_data_resampled, outdoor_data_resampled, on='created_at', suffixes=('_indoor', '_outdoor'))
    merged_data['delta'] = merged_data['value_indoor'] - merged_data['value_outdoor']

    return jsonify({
        'timestamps': merged_data['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'indoor_value': merged_data['value_indoor'].tolist(),
        'outdoor_value': merged_data['value_outdoor'].tolist(),
        'values': merged_data['delta'].tolist()
    })

if __name__ == '__main__':
    app.run(debug=True)
