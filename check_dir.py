import urllib.request
import re

import json

import urllib.request
import urllib.parse
import json

url = 'https://cdaweb.gsfc.nasa.gov/WS/cdasr/1/dataviews/sp_phys/datasets/STA_L2_MAGPLASMA_1M/orig_data/20100829T000000Z,20100903T235959Z'
try:
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    data = json.loads(html)
    print("Files found:")
    for f in data.get('FileDescription', []):
        print(f.get('Name'))
except Exception as e:
    print(f"Error: {e}")
