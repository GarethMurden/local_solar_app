from flask import Flask, render_template, request, jsonify
import json
import os

dirname, _ = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'

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
        message=message
    )

@app.route('/api/get_status', methods=['GET'])
def api_get_status():
    status = get_status()
    return jsonify(status)

def get_status():
    return load_json(f'{THIS_DIRECTORY}current_status.json')

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.loads(f.read())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    #get_status()
