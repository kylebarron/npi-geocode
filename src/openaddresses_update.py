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

import pandas as pd
import json
from os.path import expanduser

with open(expanduser('~/pelias.json')) as f:
    pelias_json = json.load(f)

df = pd.read_table('http://results.openaddresses.io/state.txt')
us_sources = [x for x in df['source'].values if x.startswith('us/')]
us_sources = [x[:-5] + '.csv' for x in us_sources if x.endswith('.json')]

pelias_json['imports']['openaddresses']['files'] = us_sources

with open(expanduser('~/pelias.json'), 'w') as f:
    json.dump(pelias_json, f, sort_keys=True, indent=4)

