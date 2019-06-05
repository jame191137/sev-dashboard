#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, current_app, abort
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
import requests
# from gevent import pywsgi
import os
# import time
# import datetime
# import pipes

app = Flask(__name__)
CORS(app)

app.config['MYSQL_DATABASE_USER'] = os.environ['SQL_USERNAME']
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ['SQL_PASSWORD']
app.config['MYSQL_DATABASE_DB'] = os.environ['SQL_DB']
app.config['MYSQL_DATABASE_HOST'] = os.environ['SQL_IP']
mysql = MySQL()
mysql.init_app(app)


def echo(txt):
    echo_txt = 'echo ' + txt
    os.system(echo_txt)


def toJson(data,columns):
    results = []
    for row in data:
        results.append(dict(zip(columns, row)))
    return results
