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
import datetime
import os
from functools import wraps
import calendar
# import mysql.connector
# from gevent import pywsgi

app = Flask(__name__,)

CORS(app, resources={r"/*": {"origins": "*"}} )

app.config['MYSQL_DATABASE_USER'] = 'smart'
app.config['MYSQL_DATABASE_PASSWORD'] = 'P@ssword'
app.config['MYSQL_DATABASE_DB'] = 'cp_warehouse'
app.config['MYSQL_DATABASE_HOST'] = '35.186.149.130'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'


mysql = MySQL()
mysql.init_app(app)

@app.route('/', methods=['GET'])
def ok():
    return 'ok'

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

        return jsonify({"status": "success","UPrivilege":result[0]['UPrivilege'],"SiteID":result[0]['SiteID']})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/getzone', methods=['POST'])
def getZone():
    try:
        data = request.json
        SiteID = data['SiteID']
        # return password
        result = querySelect_DB("SELECT * FROM zone_info WHERE SiteID = '"+SiteID+"'")
        if result == [] or result == False:
            return jsonify({"status": "fail","message":"not found"})        


       
        zone_data = []
        # num = 1
        for i in result:
            # meter_data = []

            # #result_meter = querySelect_DB("SELECT * FROM meter_info WHERE ZoneID = '"+i+"' ")
            # result_meter = querySelect_DB("SELECT * FROM meter_info WHERE ZoneID = '"+str(i['ZoneID'])+"' ")
            # # result = querySelect_DB("SELECT * FROM meter_info WHERE '1' ")
            # if result_meter == [] or result_meter == False:
            #     return jsonify({"status": "fail","message":"not found"})
            # # return 'ok'
            # for j in result_meter:
            #     meter_data.append({"MeterID":str(j['MeterID'])})

            #result_zone = querySelect_DB("SELECT * FROM zone_info WHERE SiteID = '"+i['ZoneID']+"'")
            # zone_data.append({"ZoneID":str(i['ZoneID']),"meter_data":meter_data})
            zone_data.append({
            "id":str(i['ZoneID']),
            "to": '/dashboard'+str(i['ZoneID']),
            "icon": 'mdi-view-dashboard',
            "text": 'Zone'+str(i['ZoneID'])
             })
            # str(i['ZoneID']))
            # num = num+1

        return jsonify({"status": "success","zone_data":zone_data})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/realtimeusage', methods=['POST'])
def realtimeusage():
    try:
        data = request.json
        ZoneID = data['ZoneID']
        result = querySelect_DB("SELECT ZoneID,RT_PSum, AVG((RT_V12+RT_V23+RT_V31)/3) as RT_VSum, AVG((RT_I1+RT_I2+RT_I3)/3) as RT_ISum FROM meter_info WHERE ZoneID = '"+ZoneID+"' GROUP BY ZoneID")
       
        RT_PSum = result[0]['RT_PSum']
        RT_ISum = result[0]['RT_ISum']
        RT_VSum = result[0]['RT_VSum']

        if str(RT_ISum) != 'None':
            RT_ISum = "%.2f" % RT_ISum

        if str(RT_ISum) != 'None':
            RT_VSum = "%.2f" % RT_VSum

        return jsonify({"status": "success","RT_PSum":str(RT_PSum),"RT_ISum":str(RT_ISum),"RT_VSum":str(RT_VSum)})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/getdatart', methods=['POST'])
def getdatart():
    try:
        data = request.json
        ZoneID = data['ZoneID']
        # ZoneID = '1'
        result = querySelect_DB("SELECT RT_kWh_Today,RT_kWh_Daily_Avg,RT_kWh_Monthly,RT_kWh_Monthly_Avg FROM meter_info WHERE ZoneID = '"+ZoneID+"' ")
        if result == [] or result == False:
            return jsonify({"status": "fail","message":"not found"})
        # return str(result)
        RT_kWh_Today = str(result[0]['RT_kWh_Today'])
        RT_kWh_Daily_Avg = str(result[0]['RT_kWh_Daily_Avg'])
        RT_kWh_Monthly = str(result[0]['RT_kWh_Monthly'])
        RT_kWh_Monthly_Avg = str(result[0]['RT_kWh_Monthly_Avg'])

        return jsonify({"status": "success","RT_kWh_Today":RT_kWh_Today,"RT_kWh_Daily_Avg":RT_kWh_Daily_Avg,"RT_kWh_Monthly":RT_kWh_Monthly,"RT_kWh_Monthly_Avg":RT_kWh_Monthly_Avg})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/cbuptime', methods=['POST'])
def cb_uptime():
    try:
        data = request.json
        ZoneID = data['ZoneID']
        # ZoneID = '1'
        result = querySelect_DB("SELECT*FROM cb_info WHERE ZoneID = '"+ZoneID+"' ")
        if result == [] or result == False:
            return jsonify({"status": "fail","message":"not found"})
        # return str(result)
        CB_01_Uptime = result[0]['CB_01_Uptime']
        CB_02_Uptime = result[0]['CB_02_Uptime']
        CB_Uptime = []
        # CB_Uptime.append({"CB_01_Uptime":str(CB_01_Uptime)})
        # num = 0
        # for i in result:
           
        CB_Uptime.append(
            {
                "id": "1",
                "name":'Uptime 1',
                "value":str(CB_01_Uptime)
            })
        CB_Uptime.append({
                "id": "2",
                "name":'Uptime 2',
                "value":str(CB_02_Uptime)
            })
        
        # CB_Uptime.append({"CB_02_Uptime":CB_02_Uptime})
        # CB_Uptime.append({"CB_01_Uptime":"0"})

        return jsonify({"status": "success","CB_Uptime":CB_Uptime})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/logpsum', methods=['POST'])
def logpsum():
    try:
        data = request.json
        MeterID = data['MeterID']

        result = querySelect_DB("SELECT Log_Date,Log_PSum FROM meter_log WHERE MeterID = '"+MeterID+"' LIMIT 8")
        if result == [] or result == False:
            return jsonify({"status": "fail","message":"not found"})
        # return str(result)
        date_Psum = []
        Psum = []
        for i in result:
            date = str(i['Log_Date']).split()
            date_Psum.append(date[1])
            Psum.append(str(i['Log_PSum']))

        return jsonify({"status": "success","date_Psum":date_Psum,"Psum":Psum})
    
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/sumday', methods=['POST'])
def sumday():
    try:
        result = querySelect_DB("SELECT month(log_Date) monthInYear,Day(log_Date) dayInMonth,sum(Log_kWh_Diff) as diff FROM cp_warehouse.meter_log where Month(log_Date) = MONTH(CURDATE()) group by dayInMonth order by dayInMonth limit 30")
        if result == [] or result == False:
            return jsonify({"status": "fail","message":"not found"})
        # return str(result[0]['monthInYear'])
        dayInMonth = []
        diff = []
        now = datetime.datetime.now()
        month_range = calendar.monthrange(now.year, now.month)[1]
        # return str(int(month_range)-1)
        

        month = calendar.month_name[result[0]['monthInYear']]
        
        for x in range(0, int(month_range)+1):
            date = str(month)+' '+str(x)
            dayInMonth.append(str(date))
            diff.append('0')
            # print str(x)
            
        for i in result:
            # print str(i['dayInMonth'])
            date = str(month)+' '+str(i['dayInMonth'])
            dayInMonth[i['dayInMonth']] = str(date)
            diff[i['dayInMonth']] = str(i['diff'])

        # dayInMonth =[
        #     "Jun 4",
        #     "Jun 5",
        #     "Jun 6",
        #     "Jun 7",
        #     "Jun 8",
        #     "Jun 9",
        #     "Jun 10",
        #     "Jun 11",
        #     "Jun 12",
        #     "Jun 13",
        #     "Jun 14",
        #     "Jun 15",
        #     "Jun 16",
        #     "Jun 17",
        #     "Jun 18",
        #     "Jun 19",
        #     "Jun 20",
        #     "Jun 21",
        #     "Jun 22",
        #     "Jun 23",
        #     "Jun 24",
        #     "Jun 25",
        #     "Jun 26",
        #     "Jun 27",
        #     "Jun 28",
        #     "Jun 29",
        #     "Jun 30"
        # ]
        # diff = [
        #     "1.00",
        #     "1.00",
        #     "1.00",
        #     "22.00",
        #     "22.00",
        #     "22.00",
        #     "22.00",
        #     "22.00",
        #     "22.00",
        #     "22.00",
        #     "25.00",
        #     "1.00",
        #     "1.00",
        #     "1.00",
        #     "22.00",
        #     "22.00",
        #     "22.00",
        #     "22.00",
        #     "22.00",
        #     "22.00",
        #     "22.00",
        #     "25.00",
        #     "1.00",
        #     "1.00",
        #     "1.00",
        #     "22.00",
        #     "22.00",
        #     "22.00",
        #     "22.00",
        #     "22.00"
        # ]
        return jsonify({"status": "success","dayInMonth":dayInMonth,"diff":diff})

    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/sumyear', methods=['POST'])
def sumyear():
    try:
        result = querySelect_DB("SELECT month(log_Date) monthInYear,sum(Log_kWh_Diff) as diff FROM cp_warehouse.meter_log where year(log_Date) = year(CURDATE()) group by monthInYear order by monthInYear;")
        if result == [] or result == False:
            return jsonify({"status": "fail","message":"not found"})
        # return str(result)
        monthInYear = []
        diff = []

        for x in range(1, 13):
            # date = str(month)+' '+str(x)
            monthInYear.append(str(calendar.month_name[x]))
            diff.append('0')
            # print str(x)
            
        for i in result:
            # print str(i['dayInMonth'])
            # date = str(month)+' '+str(result[0]['dayInMonth'])
            monthInYear[i['monthInYear']-1] = str(calendar.month_name[i['monthInYear']])
            diff[i['monthInYear']-1] = str(i['diff'])

        # for i in result:
        #     # date = str(i['Log_Date']).split()
        #     # date_Psum.append(date[dayInMonth])
        #     month = calendar.month_name[i['monthInYear']]
        #     monthInYear.append(str(month))
        #     diff.append(str(i['diff']))
            # diff = [
            #     "1.00",
            #     "1.00",
            #     "1.00",
            #     "22.00",
            #     "1.00",
            #     "1.00",
            #     "22.00",
            #     "1.00",
            #     "1.00",
            #     "22.00"
            #     ]
            # monthInYear = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

        return jsonify({"status": "success","monthInYear":monthInYear,"diff":diff})

    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

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
