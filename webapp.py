from datetime import datetime
from flask import Flask, render_template, request, jsonify
import json
import platform
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def root():
    message = None
    status = get_status()
    if request.method == 'POST':
        # TODO: Set inverter time
        message = "This button will eventually let you synchronise the inverter time with the server time, but I've not yet implemented it."
    return render_template(
        'dashboard.html',
        status=status,
        server={'time':datetime.now().strftime('%H:%M')},
        message=message
    )

@app.route('/api/get_status', methods=['GET'])
def api_get_status():
    status = get_status()
    status['server'] = {'time':datetime.now().strftime('%H:%M')}
    return jsonify(status)


def get_battery_mode(power):
    if power < 0:
        return 'Charging'
    else:
        return 'Discharging'

def get_grid_mode(power):
    if power > 0:
        return 'Exporting'
    else:
        return 'Importing'

def correct_load(data):
    if data['p_load_w'] == 0:
        return data['p_pv1_w'] - (data['p_grid_w'] + data['p_battery_w'])
    else:
        return data['p_load_w']

def get_status():
    if platform.system() == 'Linux':
        proc = subprocess.Popen(['/home/pi/givlocally/venv/bin/givlocally', 'read', '--output', 'json'], stdout=subprocess.PIPE)
        data = proc.stdout.read().decode('utf-8')
        data = json.loads(data)
    else:
        data = load_json('data.json')
 
    return {
        'solar':{'power':round(data['p_pv1_w'] / 1000, 2)},
        'load':{'power':round(correct_load(data) / 1000, 2)},
        'grid':{'power':round(data['p_grid_w'] / 1000, 2), 'mode':get_grid_mode(data['p_grid_w'])},
        'battery':{'power':round(data['p_battery_w'] / 1000, 2), 'charge':data['battery_soc_pct'], 'mode':get_battery_mode(data['p_battery_w'])},
        'inverter':{'time':datetime.strptime(data['system_time'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')}
    }


def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.loads(f.read())


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    #get_status()
