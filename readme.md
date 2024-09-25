### front-end

npm run serve

port:8082

### backend

python app.py
port:5000

### data structure design

```python
locations = {
    'location_1': {
        'indoor': {'sensor_name': 'A', 'channel_id': 2580816},
        'outdoor': {'sensor_name': 'B', 'channel_id': 2099116}
    },
    'location_2': {
        'indoor': {'sensor_name': 'C', 'channel_id': 3078432},
        'outdoor': {'sensor_name': 'D', 'channel_id': 3099587}
    }
}

fields = {
    'co2': 4,
    'temperature': 5,
    'humidity': 6,
    'pressure': 7
}

```




### API design

```python
# API to get data for a single sensor (either indoor or outdoor)
@app.route('/api/data/<string:location>/<string:sensor_type>/<string:indoor_or_outdoor>')

# Compute delta between indoor and outdoor data for a given location
@app.route('/api/delta/<string:location>/<string:sensor_type>')
```