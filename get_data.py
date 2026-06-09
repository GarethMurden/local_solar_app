from datetime import datetime
import json
import os
import platform
import subprocess

dirname, _ = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'

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

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.loads(f.read())

def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4))

def main():
    status = get_status()
    status['server'] = {'time':datetime.now().strftime('%Y-%m-%d %H:%M')}
    save_json(status, f'{THIS_DIRECTORY}current_status.json')
    history_file = f'{THIS_DIRECTORY}historic_status.json'
    if os.path.exists(history_file):
        history = load_json(history_file)
    else:
        history = []
    history.append(status)
    save_json(history, history_file)

if __name__ == '__main__':
    main()
