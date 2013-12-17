#!/usr/bin/env python

import csv
import datetime
import json

from flask import Flask
from pymongo import MongoClient
import requests

app = Flask("soundbites")

# Mongo connection objects.
client = MongoClient()
db = client.apps
scouting_reports = db.scouting_reports
wazer_wine = db.wazer_wine

@app.route('/wine/wazer.json')
def wazer_json():
    from flask import request
    q = request.args.get('q', None)

    query = wazer_wine.find()
    if q:
        query = wazer_wine.find(json.loads(q))

    response = {}
    response['items'] = []
    start = datetime.datetime.now()
    for item in query:
        del(item['_id'])
        response['items'].append(item)
    response['meta'] = {}
    response['meta']['count'] = len(response['items'])
    elapsed = datetime.datetime.now() - start
    response['meta']['time_elapsed'] = float('%s.%s' % (elapsed.seconds, elapsed.microseconds))
    return json.dumps(response)

@app.route('/scout/raw/')
def raw_find():
    from flask import request
    q = request.args.get('q', None)

    query = scouting_reports.find()
    if q:
        query = scouting_reports.find(json.loads(q))

    response = {}
    response['items'] = []
    start = datetime.datetime.now()
    for item in query:
        del(item['_id'])
        response['items'].append(item)
    response['meta'] = {}
    response['meta']['count'] = len(response['items'])
    elapsed = datetime.datetime.now() - start
    response['meta']['time_elapsed'] = float('%s.%s' % (elapsed.seconds, elapsed.microseconds))
    return json.dumps(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)