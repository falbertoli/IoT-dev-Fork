from flask import Flask, jsonify, request
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

locations = {
    'Kendeda': {
        'indoor': {
            'Arcalis': 2580816
        },
        'outdoor': {
            'Atlas': 2099116
        }
    },
    'CNES': {
        'indoor': {
            'Antares': 2027273,
            'Arcalis': 2580816,
            'Alcyone': 2099110,
            'Asterope': 2099111
        },
        'outdoor': {
            'Atlas': 2099116
        }
    },
}

fields = {
    'co2': 4,
    'temperature': 5,
    'humidity': 6,
    'pressure': 7
}

read_api_key = 'XHA11H2XAGGWMDY1'
num_results = 8000

def fetch_data_from_thingspeak(channel_id, field):
    url = f"https://api.thingspeak.com/channels/{channel_id}/fields/{field}.json?results={num_results}&api_key={read_api_key}"
    response = requests.get(url)
    data = response.json()
    feeds = data['feeds']

    df = pd.DataFrame(feeds)
    # 这里指定utc=True，使created_at为UTC时区的tz-aware时间
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    df['value'] = pd.to_numeric(df[f'field{field}'], errors='coerce')
    df = df.dropna()
    
    return df

def parse_date_range(range_str):
    now = datetime.now(timezone.utc)  # 使用UTC时间
    if range_str.endswith('d'):  # 日
        days = int(range_str[:-1])
        start_date = now - timedelta(days=days)
    elif range_str.endswith('m'):  # 月（简单用30天代替一月）
        months = int(range_str[:-1])
        start_date = now - timedelta(days=30 * months)
    elif range_str.endswith('y'):  # 年
        years = int(range_str[:-1])
        # 使用replace为简单起见，这里假设当前日期减去整年数
        start_date = now.replace(year=now.year - years)
    else:
        # 默认7天
        start_date = now - timedelta(days=7)
    end_date = now
    return start_date, end_date

def compute_delta(location, field, indoor_sensor_name, outdoor_sensor_name):
    indoor_channel_id = locations[location]['indoor'].get(indoor_sensor_name)
    if indoor_channel_id is None:
        raise ValueError(f"Indoor sensor {indoor_sensor_name} not found in location {location}")

    outdoor_channel_id = locations[location]['outdoor'].get(outdoor_sensor_name)
    if outdoor_channel_id is None:
        raise ValueError(f"Outdoor sensor {outdoor_sensor_name} not found in location {location}")

    indoor_data = fetch_data_from_thingspeak(indoor_channel_id, field)
    outdoor_data = fetch_data_from_thingspeak(outdoor_channel_id, field)
    print(indoor_data, outdoor_data)

    start_date = max(indoor_data['created_at'].min(), outdoor_data['created_at'].min())
    end_date = min(indoor_data['created_at'].max(), outdoor_data['created_at'].max())

    indoor_data = indoor_data[(indoor_data['created_at'] >= start_date) & (indoor_data['created_at'] <= end_date)]
    outdoor_data = outdoor_data[(outdoor_data['created_at'] >= start_date) & (outdoor_data['created_at'] <= end_date)]

    indoor_data_resampled = indoor_data.set_index('created_at').resample('1h').mean(numeric_only=True).interpolate().reset_index()
    outdoor_data_resampled = outdoor_data.set_index('created_at').resample('1h').mean(numeric_only=True).interpolate().reset_index()

    merged_data = pd.merge(indoor_data_resampled, outdoor_data_resampled, on='created_at', suffixes=('_indoor', '_outdoor'))
    # print( merged_data['value_indoor'], merged_data['value_outdoor'])
    merged_data['delta'] = merged_data['value_indoor'] - merged_data['value_outdoor']

    return merged_data

@app.route('/api/data/<string:location>/<string:sensor_type>/<string:indoor_or_outdoor>/<string:sensor_name>')
def get_single_sensor_data(location, sensor_type, indoor_or_outdoor, sensor_name):
    if location not in locations:
        return jsonify({'error': 'Invalid location'}), 400
    if sensor_type not in fields:
        return jsonify({'error': 'Invalid sensor type'}), 400
    if indoor_or_outdoor not in ['indoor', 'outdoor']:
        return jsonify({'error': 'Invalid sensor specifier, choose "indoor" or "outdoor"'}), 400

    channel_id = locations[location][indoor_or_outdoor].get(sensor_name)
    if channel_id is None:
        return jsonify({'error': f'Sensor {sensor_name} not found for {location} {indoor_or_outdoor}'}), 404

    field = fields[sensor_type]
    data = fetch_data_from_thingspeak(channel_id, field)

    # 解析range参数
    date_range = request.args.get('range', '7d')
    start_date, end_date = parse_date_range(date_range)

    # 因为data['created_at']为tz-aware且为UTC，而start_date/end_date也是UTC，因此可以直接比较
    data = data[(data['created_at'] >= start_date) & (data['created_at'] <= end_date)]

    return jsonify({
        'timestamps': data['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'values': data['value'].tolist()
    })

@app.route('/api/delta/<string:location>/<string:sensor_type>')
def get_delta(location, sensor_type):
    if location not in locations:
        return jsonify({'error': 'Invalid location'}), 400
    if sensor_type not in fields:
        return jsonify({'error': 'Invalid sensor type'}), 400

    indoor_sensor_name = request.args.get('indoor_sensor')
    outdoor_sensor_name = request.args.get('outdoor_sensor')

    if not indoor_sensor_name or not outdoor_sensor_name:
        return jsonify({'error': 'Please specify indoor_sensor and outdoor_sensor'}), 400

    field = fields[sensor_type]

    try:
        merged_data = compute_delta(location, field, indoor_sensor_name, outdoor_sensor_name)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

    # 时间范围过滤
    date_range = request.args.get('range', '7d')
    start_date, end_date = parse_date_range(date_range)

    merged_data = merged_data[(merged_data['created_at'] >= start_date) & (merged_data['created_at'] <= end_date)]

    return jsonify({
        'timestamps': merged_data['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'indoor_value': merged_data['value_indoor'].tolist(),
        'outdoor_value': merged_data['value_outdoor'].tolist(),
        'values': merged_data['delta'].tolist()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
