# API is based on Python Flask
from flask import Flask, jsonify, request

# To support CORS (cross-origin-resource-sharing)
from flask_cors import CORS

# Command-line related imports
import os, json
from subprocess import check_call

# Sample data & config
from buildings import UUIDs
from config import load_config

##### API SETUP #####
app = Flask(__name__)
cors = CORS(app)

app.config["DEBUG"] = False  # If in debug, requests will be duplicated due to https://stackoverflow.com/questions/25504149/why-does-running-the-flask-dev-server-run-itself-twice
app.config.update(load_config())
#####################

# A base route to return text message.
@app.route('/', methods=['GET'])
def home():
    return \
        "<link href = ""https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"" rel = ""stylesheet"" integrity = ""sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3"" crossorigin = ""anonymous"">" \
        "<body>" \
        "<h1>MUBES API</h1>" \
        "<p>This site is a prototype API for launching MUBES simulations.</p>" \
        "</body"

# A test route for POST requests with JSON {"name": name} that returns a message
@app.route('/test', methods=['POST'])
def test():
    return jsonify({"response": "Test has worked, " + request.json['name']})


# A route that provides all buildings available for simulations
@app.route('/api/v1/buildings/all', methods=['GET'])
def api_all():
    response = jsonify(UUIDs)
    return response


# A route provides simulation results for a list of building UUIDs provided via POST request
@app.route('/api/v1/buildings', methods=['POST'])
def queueSimulations():
    buildingsRequested = request.get_json()
    listOfUUIDs = [building['uuid'] for building in buildingsRequested]
    fake_response = False

    if (fake_response):
        response = jsonify([
            "Results from the simulations are : [Building UUID, Space heating needs (MWh)]",
            "['UUID : ', '" + simulationRequest[0]['uuid'] + "']↵",
            "['Total Space Heating Energy Needs (MWh) : ', 7.371]↵",
            "['Total Space Cooling Energy Needs (MWh) : ', 0.0]↵",
            "['Total Space Heating Energy Needs (MWh) : ', 1.581]↵",
            "['Total Space Cooling Energy Needs (MWh) : ', 0.0]↵",
            "['ATemp (m2),EP_Heated_Area (m2) : ', 5368, 4663.4]↵",
            "['Total computational time : ', 40.1, ' seconds']↵",
            "['Total results reporting : ', 0.1, ' seconds']↵"
        ])

        # response.headers.add('Access-Control-Allow-Origin', '*')
        # response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')

        return response

    CaseName = 'ForTest'
    print('Running simulations for these buildings:')
    print(listOfUUIDs)

    simulationRequest = '''
        {
            "DATA": {
                "Buildingsfile": "$DATA_FILE$"
            },
            "SIM": {
                "CaseChoices": {
                    "FloorZoning": true,
                    "DebugMode": false,
                    "CaseName": "$CASE_NAME$",
                    "RefreshFolder": false,
                    "NbRuns": 1,
                    "UUID": $UUIDS$
                }
            }
        }
    '''\
        .replace("\n","")\
        .replace("$DATA_FILE$",app.config['DATA']['PATH_TO_INPUT_DATA'])\
        .replace("$CASE_NAME$",CaseName)\
        .replace("$UUIDS$",json.dumps(listOfUUIDs))

    api_run_simulations(simulationRequest)

    results = api_read_results(json.loads(simulationRequest))
    response = jsonify(results)

    return response


# A route provides simulation results for a list of building UUIDs provided via GET request (not working now)
@app.route('/api/v1/buildings-get', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = request.args['id']
    else:
        return "Error: No id field provided. Please specify an id."

    api_run_simulations(simulationRequest)

    results = api_read_results(simulationRequest)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)


def api_run_simulations(simulationRequest):
    MUBES_Path = os.path.normcase(
        os.path.join(os.path.abspath(app.config['APP']['PATH_TO_MUBES_UBEM']), 'ModelerFolder'))
    cmdline = [
        os.path.abspath(app.config['APP']['PATH_TO_MUBES_UBEM_PYTHON']),
        os.path.join(MUBES_Path, 'SimLauncher4API_v1.py')
    ]

    cmdline.append('-CONFIG')
    cmdline.append(simulationRequest)

    check_call(cmdline, cwd=MUBES_Path, stdout=open(os.devnull, "w"))


def api_read_results(simulationRequest):
    results = ['Results from the simulations are : [Building UUID, Space heating needs (MWh)]\r\n']
    results_path = os.path.normcase(
        os.path.join(os.path.dirname(os.getcwd()), 'MUBES_SimResults', simulationRequest['SIM']['CaseChoices']['CaseName'],
                     'Sim_Results'))

    for building in simulationRequest['SIM']['CaseChoices']['UUID']:
        with open(os.path.join(results_path, building + '.txt')) as file:
            lines = file.readlines()
        [results.append(line) for line in lines]
    return results


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"])