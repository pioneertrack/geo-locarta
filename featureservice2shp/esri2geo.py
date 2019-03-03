# pertinent schema for GeoJSON format https://en.wikipedia.org/wiki/GeoJSON
# esri schema http://resources.esri.com/help/9.3/arcgisengine/ArcObjects/esriGeometry/esriGeometryType.htm
import os
import json
import glob
import pprint
import re
def batchConvert(inputFolder, outputFolder, printJSON = False, indent = 2, depth = 4):
	if os.path.exists(inputFolder):
		for file in glob.glob(inputFolder + "/*.json"):# find all .json files in specified inputFolder
			geojson(file, outputFolder, printJSON=printJSON, indent=indent, depth=depth)#nested call to geojson with kwargs
			print(file + " converted to geojson.")
	else:
		print('folder' + inputFolder +' does not exist.')

def geojson(input, output, **kwargs):
	data = json.load(open(input, 'r'))
	inputFile = re.search('\w+(?=\.json)', input) #strip input filepath of directory and file extension
	pp = pprint.PrettyPrinter(indent=kwargs['indent'], depth=kwargs['depth'])#pull user defined parameters for printing
	temp_dict = {}
	try:
		data['geometryType']
	except KeyError:
		print(inputFile.group(0) + ' is not the right json format')
	else:
		# please refer to this list of constants at top for stripping of esriGeometry
		geometryType = re.search( "(?<=esriGeometry)\w+", data['geometryType'])#regex to strip esriGeometry to keep geometry type
		geometryIs = geometryType.group(0)
		print geometryIs
		temp_dict['type'] = 'FeatureCollection'
		for key, value in data.iteritems():
			if (key == 'features'):
				temp_dict[key] = value
				for d in temp_dict['features']: #d used as contrace form of nested data
					if 'type' not in d:
						d['type'] = 'Feature'
					for k, v in d.iteritems():# k for nested key and v for nested value
						if 'attributes' in k:
							d['properties'] = d.pop('attributes')
						if 'geometry' in k:
							if geometryIs == 'Polygon':
								if k == 'geometry' and 'rings' in v:
									v['type'] = geometryIs
									v['coordinates'] = v.pop('rings')
							elif geometryIs == 'Point':
								if k == 'geometry' and 'x' in v: #refactor keys x & y into a single array
									v['coordinates'] = [v['x'], v['y']]
									del v['x']
									del v['y']
		#join ouptput folder path & filename + GeoJSON file extentsion
		gRename = os.path.join(output, inputFile.group(0) + '.geojson')
		json.dump(temp_dict, open(gRename, 'w+'))
		if kwargs.get('printJSON') == True:
			pp.pprint(temp_dict)