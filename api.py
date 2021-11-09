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

# A route to return values for a particular building.
@app.route('/api/v1/buildings/', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = request.args['id']
    else:
        return "Error: No id field provided. Please specify an id."

    # Create an empty list for our results
    results = []

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    for building in buildings:
        if building['properties']['50A_UUID'] == id:
            results.append(building['properties'])

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)

app.run()