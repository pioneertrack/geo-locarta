import requests
import urlparse
import json
import os
import pebble
import utils
import functools
import convert


#__output_path = 'files/'
#__output_file = 'output.geojson'
__url = 'https://maps.land.vic.gov.au/lassi/retrieveDataForSelectedMarks.json'
__page = 1000
__limit = 300000


@utils.retry(Exception, tries=3, delay=1, backoff=2)
def get_marks(mark_ids,output_path):
    mark_id = ','.join(mark_ids)
    data = {
        'selectedMarkIDS': mark_id
    }
    response = requests.post(__url, data=data)
    file_path = os.path.join(output_path, str(mark_ids[0]) + '.json')
    utils.write_file(file_path, response.content)
def downloadData(path,outputfile):

    if not os.path.exists(path):
        os.makedirs(path)
    
    i = 0
    while True:
        ids = list(str(x) for x in range(i, i+__page-1))
        if ids:
            future = get_marks(ids,path)
        if i>= __limit:
            break
        i += __page
    convert.parse_files(path, outputfile)
def downloadData_old(path,outputfile):

    if not os.path.exists(path):
        os.makedirs(path)
    with pebble.ProcessPool(max_workers=1, max_tasks=2) as pool:
        i = 0
        while True:
            ids = list(str(x) for x in range(i, i+__page-1))
            if ids:
                future = pool.schedule(get_marks, args=[ids,path], timeout=100)
            if i>= __limit:
                break
            i += __page
    convert.parse_files(path, outputfile)
'''
if __name__ == '__main__':
    if not os.path.exists(__output_path):
        os.makedirs(__output_path)
    with pebble.ProcessPool(max_workers=1, max_tasks=2) as pool:
        i = 0
        while True:
            ids = list(str(x) for x in range(i, i+__page-1))
            if ids:
                future = pool.schedule(get_marks, args=[ids], timeout=100)
            if i>= __limit:
                break
            i += __page
    convert.parse_files(__output_path, __output_file)
    print 'Done'
'''
