from flask import Flask, jsonify
import requests
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# ThingSpeak API配置
channel_id = '2027273'
indoor_channel_id = '2580816'
outdoor_channel_id = '2099116'
read_api_key = 'XHA11H2XAGGWMDY1'
num_results = 8000

# 从ThingSpeak获取数据
def fetch_data_from_thingspeak(channel_id, field):
    url = f"https://api.thingspeak.com/channels/{channel_id}/fields/{field}.json?results={num_results}&api_key={read_api_key}"
    response = requests.get(url)
    data = response.json()
    feeds = data['feeds']
    
    # 将数据转换为DataFrame
    df = pd.DataFrame(feeds)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['value'] = pd.to_numeric(df[f'field{field}'], errors='coerce')
    df = df.dropna()
    
    return df

@app.route('/api/data/<string:chart_type>')
def get_data(chart_type):
    if chart_type == 'co2':
        field = 4
    elif chart_type == 'temperature':
        field = 1
    elif chart_type == 'humidity':
        field = 6
    elif chart_type == 'pressure':
        field = 7
    else:
        return jsonify({'error': 'Invalid chart type'}), 400

    # 从 ThingSpeak 获取数据
    df = fetch_data_from_thingspeak(channel_id, field)
    
    # 提取时间戳和数值
    timestamps = df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
    values = df['value'].tolist()
    
    return jsonify({'timestamps': timestamps, 'values': values})

@app.route('/api/delta-co2')
def get_delta_co2():
    # 获取室内和室外CO2数据
    indoor_data = fetch_data_from_thingspeak(indoor_channel_id, 4)
    outdoor_data = fetch_data_from_thingspeak(outdoor_channel_id, 4)

    # 找到共同的日期范围
    start_date = max(indoor_data['created_at'].min(), outdoor_data['created_at'].min())
    end_date = min(indoor_data['created_at'].max(), outdoor_data['created_at'].max())

    # 修剪数据到共同的日期范围
    indoor_data = indoor_data[(indoor_data['created_at'] >= start_date) & (indoor_data['created_at'] <= end_date)]
    outdoor_data = outdoor_data[(outdoor_data['created_at'] >= start_date) & (outdoor_data['created_at'] <= end_date)]

    # 按小时采样并插值处理
    indoor_data_resampled = indoor_data.set_index('created_at').resample('1h').mean(numeric_only=True).interpolate().reset_index()
    outdoor_data_resampled = outdoor_data.set_index('created_at').resample('1h').mean(numeric_only=True).interpolate().reset_index()

    # 合并室内和室外数据并计算差值
    merged_data = pd.merge(indoor_data_resampled, outdoor_data_resampled, on='created_at', suffixes=('_indoor', '_outdoor'))
    merged_data['delta'] = merged_data['value_indoor'] - merged_data['value_outdoor']

    # 返回时间戳、室内CO2、室外CO2和Delta数据
    return jsonify({
        'timestamps': merged_data['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'indoor_co2': merged_data['value_indoor'].tolist(),
        'outdoor_co2': merged_data['value_outdoor'].tolist(),
        'delta_co2': merged_data['delta'].tolist()
    })

if __name__ == '__main__':
    app.run(debug=True)
