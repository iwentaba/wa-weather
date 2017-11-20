from flask import Flask, render_template, request, jsonify
from config import create_rain_day

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/getRain', methods=['GET'])
def get_rain():
    date = request.args.get('date')  # expects date in YYYY-MM-DD format
    lat = request.args.get('lat')  # expects signed lat decimal
    lon = request.args.get('lon')  # expects signed lon decimal

    split_date = list(map(lambda x: int(x), date.split('-')))
    rain_day = create_rain_day(*split_date)

    time, rain = rain_day.get_rain_at(float(lat), float(lon))
    max_rain = max(rain)
    if max_rain > 100:
        max_val = max_rain
    elif max_rain > 20:
        max_val = 100
    elif max_rain > 2:
        max_val = 21
    else:
        max_val = 3

    rain_data_map = [{"t": t, "r": r} for t, r in zip(time, rain)]
    lat_b, lon_b = rain_day.get_bounds()
    bounds_geojson = {"type": "Polygon", "coordinates": [[[lon_b[0], lat_b[0]],
                                                          [lon_b[0], lat_b[1]],
                                                          [lon_b[1], lat_b[1]],
                                                          [lon_b[1], lat_b[0]],
                                                          [lon_b[0], lat_b[0]]]]}
    response = {"max_rain": max_val,
                "data": rain_data_map,
                "bounds": bounds_geojson,
                "last_updated": rain_day.time_updated.timestamp()}

    return jsonify(response)
