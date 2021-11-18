import json

sampleFile = open('../data/Minneberg_Buildings_v1.geojson', )
buildings = json.load(sampleFile)['features']
sampleFile.close()

UUIDs = []
for building in buildings:
    UUIDs.append(building['properties']['50A_UUID'])