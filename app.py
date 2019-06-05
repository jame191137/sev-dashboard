#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from header import *
# from backup_sql.backup_sql import *
# from backup_mongo.backup_mongo import *
from flask import Flask, request, jsonify, current_app, abort
from flask_cors import CORS, cross_origin
import requests
from flaskext.mysql import MySQL
# from flask import Flask, current_app
import os
from functools import wraps
# import mysql.connector
# from gevent import pywsgi

app = Flask(__name__,)

CORS(app, resources={r"/*": {"origins": "*"}} )

app.config['MYSQL_DATABASE_USER'] = 'smart'
app.config['MYSQL_DATABASE_PASSWORD'] = 'P@ssword'
app.config['MYSQL_DATABASE_DB'] = 'cp_warehouse'
app.config['MYSQL_DATABASE_HOST'] = '35.186.149.130'
# db.config['MYSQL_DATABASE_USER'] = os.environ['MYSQL_DATABASE_USER']
# db.config['MYSQL_DATABASE_PASSWORD'] = os.environ['MYSQL_DATABASE_PASSWORD']
# db.config['MYSQL_DATABASE_DB'] = os.environ['MYSQL_DATABASE_DB']
# db.config['MYSQL_DATABASE_HOST'] = os.environ['MYSQL_DATABASE_HOST']

mysql = MySQL()
mysql.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data['username']
        password = data['password']
        print str(username)
        print str(password)
        # return password
        result = querySelect_DB("SELECT * FROM users WHERE UName = '"+username+"' AND UPass = '"+password+"'")
        if result == [] or result == False:
            return jsonify({"status": "fail","message":"not found"})
        return jsonify({"status": "success","UPrivilege":result[0]['UPrivilege']})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/realtimeusage', methods=['GET'])
def realtimeusage():

    result = querySelect_DB("SELECT * FROM meter_info")
    RT_PSum = result[0]['RT_PSum']

    RT_I1 = result[0]['RT_I1']
    RT_I2 = result[0]['RT_I2']
    RT_I3 = result[0]['RT_I3']
    RT_ISum = (RT_I1+RT_I2+RT_I3)/3

    RT_V12 = result[0]['RT_V12']
    RT_V23 = result[0]['RT_V23']
    RT_V31 = result[0]['RT_V31']
    RT_VSum = (RT_V12+RT_V23+RT_V31)/3
    RT_VSum = "%.2f" % RT_VSum
    # RT_Sum = (RT_I1+RT_I2+RT_I3)/3
    # return str(RT_ISum)
    return jsonify({"status": "success","RT_PSum":str(RT_PSum),"RT_ISum":str(RT_ISum),"RT_VSum":str(RT_VSum)})

def connect_sql():
    def wrap(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Setup connection
                connection = mysql.connect()
                cursor = connection.cursor()
                return_val = fn(cursor, *args, **kwargs)
            finally:
                # Close connection
                connection.commit()
                connection.close()
            return return_val
        return wrapper
    return wrap

def querySelect_DB(strQuery):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(strQuery)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        return result
    except Exception as e:
    # except:
        print '--------------------query not success -------------'
        print str(e)
        current_app.logger.info(str(e))
        return e
    # return result


# insert database
def insert_DB(strInsert):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(strInsert)
        conn.commit()
        conn.close()
        return True
    # except
    except Exception as e:
        print '--------------------insert not success -------------'
        print str(e)
        return False


# delete database
def delete_DB(strDelete):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = strDelete
        cursor.execute(sql)
        conn.commit()
        return True
    # except:
    except Exception as e:
        print '--------------------delete not success -------------'
        print str(e)
        return False

# update database
def update_DB(strUpdate):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = strUpdate
        cursor.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        print '--------------------update not success -------------'
        print str(e)
        return False

# change to Json
def toJson(data,columns):
    results = []
    for row in data:
        results.append(dict(zip(columns, row)))
    return results




if __name__ == '__main__':
	# from db import db
	# db.init_app(app)
	app.run(debug=True, host='0.0.0.0',threaded=True,port=8997)
# if __name__ == '__main__':
#     server = pywsgi.WSGIServer(('0.0.0.0', 8997), app)
#     server.serve_forever()
