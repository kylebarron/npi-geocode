#! /usr/bin/env python3
"""
---------------------------------------------------------------------
Project: npi-geocode
Program: openaddresses_update.py
Author:  Kyle Barron <barronk@mit.edu>
Created: 3/20/2018, 4:07:03 PM
Updated: 3/20/2018, 4:07:03 PM
Purpose: Update pelias.json with current list of openaddresses files
Depends: ~/pelias.json
Outputs: ~/pelias.json
"""

import json
import glob
from os.path import expanduser

with open(expanduser('~/pelias.json')) as f:
    pelias_json = json.load(f)

pelias_json['imports']['openaddresses'].keys()
oa_data_folder = pelias_json['imports']['openaddresses']['datapath']
files = glob.glob(oa_data_folder + '/us/**/*.csv')
files = ['/'.join(x.split('/')[-3:]) for x in files]
files = sorted(files)
pelias_json['imports']['openaddresses']['files'] = files

with open(expanduser('~/pelias.json'), 'w') as f:
    json.dump(pelias_json, f, sort_keys=True, indent=4)

