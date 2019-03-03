import w3lib.html
import re
import os
import json


def convert_point(point):
    format_input = w3lib.html.replace_entities(point)
    parts = re.split(w3lib.html.replace_entities("[&deg;&#39;&quot;]+"), format_input)
    dd = abs(float(parts[0])) + float(parts[1])/60 + float(parts[2])/(60*60);
    if float(parts[0])<0:
        dd *= -1
    return dd;


def parse_files(directory, output_file):
    with open(output_file, 'w') as output:
        output.write("{\"type\":\"FeatureCollection\",\"crs\":{\"type\":\"name\",\"properties\":{\"name\":\"urn:ogc:def:crs:EPSG::4326\"}},\"features\":[")
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)
            results = json.load(open(path))
            for data in results['result']:
                if not 'latitude' in data or not data['latitude']:
                    continue
                feature = { "type" :  'Feature',
                    "properties" :  {
                        'nineFigureNumber': data['nine_fig'],
                        'name': data['mark_name'],
                        'status': data['status'],
                        'scn': data['scn_type'],
                        'easting': data['easting'],
                        'northing': data['northing'],
                        'zone': data['zonetxt'],
                        'latitude': convert_point(data['latitude']),
                        'longitude': convert_point(data['longitude']),
                        'ahdHeight': data['ahd_height'],
                        'ellipsoidHeight': data['ellipsoid_height'],
                        'hUncertainty': data['h_uncertaintly'],
                        'vUncertainty': data['v_uncertaintly'],
                        'hOrder': data['h_order'],
                        'vOrder': data['v_order'],
                        'gda94PublishedDate': data['gda_published_date'],
                        'gda94Technique': data['gda_technique'],
                        'gda94Measurements': data['msrType'],
                        'gda94Source': data['gda_source'],
                        'ahdLevelSection': data['level_section'],
                        'ahdPublishedDate': data['ahd_published_date'],
                        'ahdTechnique': data['ahd_technique'],
                        'ahdSource': data['ahd_source'],
                        'markPostExists': data['markerPost'],
                        'coverExists': data['coverExist'],
                        'markType': data['markType'],
                        'gnssSuitability': data['gnss'],
                        'groundToMarkOffset': data['groundToMark'],
                        'longitude_precision': data['longitude_precision'],
                        'posUncertainty': data['posUncertainty'],
                        'mark_id': data['mark_id'],
                        'verticalAdjId': data['verticalAdjId'],
                        'coordAdjId': data['coordAdjId'],
                        'symbol': data['symbol'],
                        'latitude_precision': data['latitude_precision'],
                        'markHeightAdjusted': data['markHeightAdjusted'],
                        'derivedFromJurisdictionGDAAdjustment': data['derivedFromJurisdictionGDAAdjustment'],
                        'verticalTechnique': data['verticalTechnique'],
                        'derivedFromAHDAdjustmentbyAHD': data['derivedFromAHDAdjustmentbyAHD']
                    },
                    "geometry" :  {
                        "type":  "Point",
                        "coordinates": [convert_point(data['longitude']), convert_point(data['latitude'])]
                    }
                }
                output.write(json.dumps(feature, sort_keys=True) + ',')
        output.write(']}')