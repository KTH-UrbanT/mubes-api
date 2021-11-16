import sys,os,platform
from subprocess import check_call

import flask
from buildings import buildings, UUIDs
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# A base route to return text message.
@app.route('/', methods=['GET'])
def home():
    return\
        "<link href = ""https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"" rel = ""stylesheet"" integrity = ""sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3"" crossorigin = ""anonymous"">" \
        "<body>" \
        "<h1>MUBES API</h1>" \
        "<p>This site is a prototype API for launching MUBES simulations.</p>" \
        "</body"

# A route to return all possible buildings.
@app.route('/api/v1/buildings/all', methods=['GET'])
def api_all():
    return jsonify(UUIDs)

# A route to return values for a list of building.
@app.route('/api/v1/buildings/', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = request.args['id']
    else:
        return "Error: No id field provided. Please specify an id."

    CaseName = 'APIRuns'
    api_runCases(CaseName,id)

    results = api_readRes(CaseName,id)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)

def api_runCases(CaseName,id):

    MUBES_Paths = os.path.normcase(os.path.join(os.path.dirname(os.getcwd()), 'MUBES_UBEM','ModelerFolder'))
    #path t0 the python used including all the required packages
    pythonpath = os.path.normcase(os.path.join(os.getcwd(),'venv','bin','python'))
    #path for the input Data
    datapath = os.path.normcase(os.path.join(os.getcwd(),'sample_data','Sodermalmv4'))
    if platform.system() == "Windows":
        MUBES_Paths = os.path.normcase(
            os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'MUBES_UBEM', 'ModelerFolder'))
        pythonpath = os.path.normcase(os.path.join(os.path.dirname(os.getcwd()),'venv','Scripts','python.exe'))
    cmdline = [pythonpath, os.path.join(MUBES_Paths, 'SimLauncher4API_v1.py')]
    cmdline.append('-UUID')
    cmdline.append(str(id))
    cmdline.append('-CaseName')
    cmdline.append(CaseName)
    cmdline.append('-DataPath')
    cmdline.append(datapath)
    check_call(cmdline, cwd=MUBES_Paths, stdout=open(os.devnull, "w"))

def api_readRes(CaseName,id):
    results =['Results from the simulations are : [Building UUID, Space Heating needs (MWh)]']
    Res_Paths = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'MUBES_SimResults', CaseName,'Sim_Results')
    import re
    for i in re.findall("[^,]+", id):
        with open(os.path.join(Res_Paths,i+'.txt')) as file:
            Lines = file.readlines()
        [results.append(line) for line in Lines]
    return results

if __name__ == '__main__' :
    app.run()