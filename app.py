#!/usr/bin/env python
# -*- coding: utf-8 -*-
from header import *
from backup_sql.backup_sql import *
from backup_mongo.backup_mongo import *

@app.route('/', methods=['GET'])
def hello():
    return 'Hello'

if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 8997), app)
    server.serve_forever()
