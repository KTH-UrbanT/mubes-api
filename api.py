import os
from subprocess import check_call


from flask import Flask, jsonify, request

# To support CORS (cross-origin-resource-sharing)
from flask_cors import CORS

from buildings import UUIDs
from config import load_config

app = Flask(__name__)

cors = CORS(app)

# cors = CORS(app, supports_credentials=True)
# cors = CORS(app, resources={r"/*": {"origins": "*"}})

# cors = CORS(app,
#             origins=["http://localhost:3000"],
#             headers=['Content-Type'],
#             expose_headers=['Access-Control-Allow-Origin'],
#             supports_credentials=True)

# CORS_ALLOW_ORIGIN = "*,*"
# CORS_EXPOSE_HEADERS = "*,*"
# CORS_ALLOW_HEADERS = "content-type,*"
            # origins = CORS_ALLOW_ORIGIN.split(","),
            # allow_headers = CORS_ALLOW_HEADERS.split(","),
            # expose_headers = CORS_EXPOSE_HEADERS.split(","))

app.config["DEBUG"] = True
# app.config['CORS_HEADERS'] = 'Content-Type'
app.config.update(load_config())

# @app.after_request
# def creds(response):
#     response.headers['Access-Control-Allow-Credentials'] = 'true'
#     return response

# A base route to return text message.
@app.route('/', methods=['GET'])
def home():
    return\
        "<link href = ""https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"" rel = ""stylesheet"" integrity = ""sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3"" crossorigin = ""anonymous"">" \
        "<body>" \
        "<h1>MUBES API</h1>" \
        "<p>This site is a prototype API for launching MUBES simulations.</p>" \
        "</body"


@app.route('/test', methods=['POST'])
def test():
    return jsonify({"respone": "Test has worked, " + request.json['name']})


# A route to return all possible buildings.
@app.route('/api/v1/buildings/all', methods=['GET'])
def api_all():
    response = jsonify(UUIDs)
    # response.headers.add('Access-Control-Allow-Origin', '*')
    # response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
    return response

# A route to return shortened ids for a list of building.
@app.route('/api/v1/buildings-test', methods=['POST'])
def queueSimulations():
    building_uuid = request.get_json()[0]['uuid']
    fake = True

    if (not fake):
        caseName = 'ForTest'
        api_run_cases(caseName, building_uuid)

        results = api_read_results(caseName, building_uuid)
        response = jsonify(results)

        return response

    fake_response = jsonify([
        "Results from the simulations are : [Building UUID, Space heating needs (MWh)]",
        "['UUID : ', '" + building_uuid + "']↵",
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

    return fake_response


# A route to return values for a list of building.
@app.route('/api/v1/buildings', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = request.args['id']
    else:
        return "Error: No id field provided. Please specify an id."

    CaseName = 'ForTest'
    api_run_cases(CaseName, id)

    results = api_read_results(CaseName, id)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)


def api_run_cases(CaseName, id):

    MUBES_Path = os.path.normcase(os.path.join(os.path.abspath(app.config['APP']['PATH_TO_MUBES_UBEM']), 'ModelerFolder'))
    # MUBES_Path = os.path.normcase(os.path.join(os.path.dirname(os.getcwd()), 'MUBES_UBEM','ModelerFolder'))
    #path t0 the python used including all the required packages
    # pythonpath = os.path.normcase(os.path.join(os.path.dirname(os.getcwd()),'venv','bin','python'))
    #path for the input Data
    # datapath = os.path.normcase(os.path.join(os.getcwd(),'sample_data','Sodermalmv4'))
    # EPlusPath =  os.path.normcase('/usr/local/EnergyPlus-9.1.0')
    # if platform.system() == "Windows":
    #     EPlusPath =  os.path.normcase('C:\EnergyPlusV9-1-0')
    #     pythonpath = os.path.normcase(os.path.join(os.path.dirname(os.getcwd()),'venv','Scripts','python.exe'))
    # cmdline = [pythonpath, os.path.join(MUBES_Path, 'SimLauncher4API_v1.py')]
    cmdline = [
        os.path.abspath(app.config['APP']['PATH_TO_MUBES_UBEM_PYTHON']),
        os.path.join(MUBES_Path, 'SimLauncher4API_v1.py')
    ]
    cmdline.append('-UUID')
    cmdline.append(str(id))
    cmdline.append('-CaseName')
    cmdline.append(CaseName)
    cmdline.append('-DataPath')
    cmdline.append(os.path.abspath(app.config['DATA']['PATH_TO_INPUT_DATA']))
    cmdline.append('-EPlusPath')
    cmdline.append(os.path.abspath(app.config['APP']['PATH_TO_ENERGYPLUS']))

    check_call(cmdline, cwd=MUBES_Path, stdout=open(os.devnull, "w"))


def api_read_results(CaseName, id):
    results = ['Results from the simulations are : [Building UUID, Space heating needs (MWh)]']
    results_path = os.path.normcase(os.path.join(os.path.dirname(os.getcwd()), 'MUBES_SimResults', CaseName, 'Sim_Results'))
    import re
    for i in re.findall("[^,]+", id):
        with open(os.path.join(results_path, i+'.txt')) as file:
            lines = file.readlines()
        [results.append(line) for line in lines]
    return results

if __name__ == '__main__' :
    app.run(debug=True)