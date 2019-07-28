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
from datetime import datetime as dt
import os
from functools import wraps
import calendar
import paho.mqtt.client as paho
# import mysql.connector
# from gevent import pywsgi


app = Flask(__name__,)

CORS(app, resources={r"/*": {"origins": "*"}} )

app.config['MYSQL_DATABASE_USER'] = 'smart'
app.config['MYSQL_DATABASE_PASSWORD'] = 'P@ssword'
app.config['MYSQL_DATABASE_DB'] = 'cp_warehouse'
# app.config['MYSQL_DATABASE_HOST'] = '35.186.149.130'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'


mysql = MySQL()
mysql.init_app(app)


def on_connect(client, userdata, flags, rc):
    print "connected"
    # current_app.logger.info("CONNACK received with code %d." % (rc))


@app.route('/publish', methods=['POST'])
def public():

    try:
        data = request.json
        path = data['path']
        value = data['value']

        client = paho.Client()
        print "connecting....."
        client.on_connect = on_connect
        client.username_pw_set("smartautomation", "0000")
        client.connect("35.186.149.130")
        print "connected"
        client.publish(path,value)
        print "publish....."


        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})



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
        result_name = querySelect_DB("SELECT * FROM site_info WHERE SiteID = '"+str(result[0]['SiteID'])+"'")

        return jsonify({"status": "success","UPrivilege":result[0]['UPrivilege'],"SiteID":result[0]['SiteID'],"SiteName":result_name[0]['SiteName']})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})


@app.route('/datatable', methods=['POST'])
def datatable():
    try:
        data = request.json

        dateStart = data['dateStart']
        dateEnd = data['dateEnd']
        MeterID = data['MeterID']

        # dateEnd = str(dateEnd) + ' 00:00:00'
        # MeterID = str(MeterID) + ' 00:00:00'
        list_data = []
        result_meter = querySelect_DB("SELECT*FROM meter_log WHERE MeterID = '"+MeterID+"' AND Log_Date >= '"+str(dateStart)+"' AND Log_Date <= '"+str(dateEnd)+"'   ")
        # result = querySelect_DB("SELECT Log_Date,Log_PSum FROM meter_log WHERE MeterID = '"+MeterID+"' LIMIT 8")
        # return str(result_meter)
        if result_meter == [] or result_meter == False:
            return jsonify({"status": "fail","message":"not found"})
            # return jsonify({"status": "success","list_data":[]})

        # return str(result)
        for i in result_meter:
            list_data.append(
                {
                "Log_Date":str(i['Log_Date']),
                "Log_V1":str(i['Log_V1']),
                "Log_V2":str(i['Log_V2']),
                "Log_V3":str(i['Log_V3']),
                "Log_V12":str(i['Log_V12']),
                "Log_V23":str(i['Log_V23']),
                "Log_V31":str(i['Log_V31']),
                "Log_I1":str(i['Log_I1']),
                "Log_I2":str(i['Log_I2']),
                "Log_I3":str(i['Log_I3']),
                "Log_In":str(i['Log_In']),
                "Log_Pa":str(i['Log_Pa']),
                "Log_Pb":str(i['Log_Pb']),
                "Log_Pc":str(i['Log_Pc']),
                "Log_PSum":str(i['Log_PSum']),
                "Log_Qa":str(i['Log_Qa']),
                "Log_Qb":str(i['Log_Qb']),
                "Log_Qc":str(i['Log_Qc']),
                "Log_PFa":str(i['Log_PFa']),
                "Log_PFb":str(i['Log_PFb']),
                "Log_PFc":str(i['Log_PFc']),
                "Log_PFSum":str(i['Log_PFSum']),
                "Log_Sa":str(i['Log_Sa']),
                "Log_Sb":str(i['Log_Sb']),
                "Log_Sc":str(i['Log_Sc']),
                "Log_F":str(i['Log_F']),
                "Log_kWh":str(i['Log_kWh']),
                "Log_kWh_Diff":str(i['Log_kWh_Diff'])
                })
        # print str(list_data)
        return jsonify({"status": "success","list_data":list_data})

    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/getmeter', methods=['POST'])
def getMeter():
    try:
        data = request.json
        ZoneID = data['ZoneID']
        # return password
        result = querySelect_DB("SELECT * FROM meter_info WHERE ZoneID = '"+ZoneID+"'")
        if result == [] or result == False:
            return jsonify({"status": "success","meter_data":[]})

        meter_data = []

        for i in result:
             meter_data.append({
                "id":str(i['MeterID']),
                "text": str(i['MeterName'])
             })

        return jsonify({"status": "success","meter_data":meter_data})
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
            zone_data.append({
                "id":str(i['ZoneID']),
                # "to": '/dashboard2',
                "to": '/dashboard'+str(i['ZoneID']),
                "icon": 'mdi-view-dashboard',
                "text": str(i['ZoneName'])
             })


        return jsonify({"status": "success","zone_data":zone_data})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})


@app.route('/getlistzone', methods=['POST'])
def getlistzone():
    try:
        data = request.json
        SiteID = data['SiteID']

        result = querySelect_DB("SELECT * FROM zone_info WHERE SiteID = '"+str(SiteID)+"' ")
        if result == [] or result == False:
            return jsonify({"status": "fail","message":"zone found"})
        list_zone = []
        for i in result:
            list_zone.append(i['ZoneID'])

        return jsonify({"status": "success","list_zone":list_zone})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/getnumzone', methods=['GET'])
def getnumzone():
    try:
        result = querySelect_DB("SELECT * FROM zone_info")

        return jsonify({"status": "success","num":len(result)})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/realtimeusage', methods=['POST'])
def realtimeusage():
    try:
        data = request.json
        ZoneID = data['ZoneID']
        result = querySelect_DB("SELECT ZoneID,RT_PSum, AVG((RT_V12+RT_V23+RT_V31)/3) as RT_VSum, AVG((RT_I1+RT_I2+RT_I3)/3) as RT_ISum FROM meter_info WHERE ZoneID = '"+ZoneID+"' AND MeterID = '"+ZoneID+"' GROUP BY ZoneID")
        # return str(result)
        if result == [] or result == False:
            RT_PSum = "0"
            RT_ISum = "0"
            RT_VSum = "0"

        else:
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
        result = querySelect_DB("SELECT RT_kWh_Today,RT_kWh_Daily_Avg,RT_kWh_Monthly,RT_kWh_Monthly_Avg FROM meter_info WHERE ZoneID = '"+ZoneID+"'  ")
        if result == [] or result == False:
            return jsonify({"status": "fail","message":"not found"})
        # return str(result)
        RT_kWh_Today = str(int(result[0]['RT_kWh_Today']))
        RT_kWh_Daily_Avg = str(int(result[0]['RT_kWh_Daily_Avg']))
        RT_kWh_Monthly = str(int(result[0]['RT_kWh_Monthly']))
        RT_kWh_Monthly_Avg = str(int(result[0]['RT_kWh_Monthly_Avg']))

        return jsonify({"status": "success","RT_kWh_Today":RT_kWh_Today,"RT_kWh_Daily_Avg":RT_kWh_Daily_Avg,"RT_kWh_Monthly":RT_kWh_Monthly,"RT_kWh_Monthly_Avg":RT_kWh_Monthly_Avg})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/getdatart2', methods=['POST'])
def getdatart2():
    try:
        data = request.json

        ZoneID = data['ZoneID']
        list_RT = []
        result_meter = querySelect_DB("SELECT MeterID,MeterName FROM meter_info WHERE ZoneID = '"+str(ZoneID)+"'")

        for i in result_meter:
            result = querySelect_DB("SELECT RT_kWh_Today,RT_kWh_Daily_Avg,RT_kWh_Monthly,RT_kWh_Monthly_Avg FROM meter_info WHERE ZoneID = '"+i['ZoneID']+"'  ")
            if result == [] or result == False:
                return jsonify({"status": "fail","message":"not found"})
            # return str(result)
            RT_kWh_Today = str(int(result[0]['RT_kWh_Today']))
            RT_kWh_Daily_Avg = str(int(result[0]['RT_kWh_Daily_Avg']))
            RT_kWh_Monthly = str(int(result[0]['RT_kWh_Monthly']))
            RT_kWh_Monthly_Avg = str(int(result[0]['RT_kWh_Monthly_Avg']))

            list_RT.append({"RT_kWh_Today":RT_kWh_Today,"RT_kWh_Daily_Avg":RT_kWh_Daily_Avg,"RT_kWh_Monthly":RT_kWh_Monthly,"RT_kWh_Monthly_Avg":RT_kWh_Monthly_Avg})

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

# @app.route('/logpsum', methods=['POST'])
# def logpsum():
#     try:
#         data = request.json
#         MeterID = data['MeterID']

#         result = querySelect_DB("SELECT Log_Date,Log_PSum FROM meter_log WHERE MeterID = '"+MeterID+"' LIMIT 8")
#         # result = querySelect_DB("SELECT Log_Date,Log_PSum FROM meter_log WHERE MeterID = '"+MeterID+"' LIMIT 8")
#         # return str(result)
#         if result == [] or result == False:
#             return jsonify({"status": "fail","message":"not found"})
#         # return str(result)
#         date_Psum = []
#         Psum = []
#         for i in result:
#             date = str(i['Log_Date']).split()
#             date_Psum.append(date[1])
#             Psum.append(str(i['Log_PSum']))

#         return jsonify({"status": "success","date_Psum":date_Psum,"Psum":Psum})

#     except Exception as e:
#         return jsonify({"status": "fail","message":str(e)})

@app.route('/meterstatus', methods=['POST'])
def listmeterstatus():
    try:
        data = request.json
        # SiteID = data['SiteID']
        list_psum = []
        date_Psum = []
        Psum = []
        # result_site = querySelect_DB("SELECT * FROM zone_info WHERE SiteID = '"+str(SiteID)+"'")
        #
        list_meter = []
        # for r in result_site:

        result_meter = querySelect_DB("SELECT Meter_Status,MeterID FROM meter_info")
        for r in result_meter:
            if str(r['Meter_Status']) == '1':
                list_meter.append(True)
            else:
                list_meter.append(False)

        return jsonify({"status": "success","list_meter_status":list_meter})
    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/schedulestatus', methods=['POST'])
def listschedule():
    try:
        data = request.json
        # SiteID = data['SiteID']
        # list_psum = []
        # date_Psum = []
        # Psum = []
        # result_site = querySelect_DB("SELECT * FROM zone_info WHERE SiteID = '"+str(SiteID)+"'")
        #
        list_time = []
        # for r in result_site:

        result_schedule = querySelect_DB("SELECT*FROM schedule_data")

        # a = datetime.strptime(result_schedule[0]['d1_close_time'], "%m/%j/%y %H:%M")
        # a = t.strftime ('%H:%M:%S')
        # return str(a)
        for i in result_schedule:
            t = i['time']
            time = t.strftime ('%H:%M')
            list_time.append(time)
        return jsonify({"status": "success","list_time":list_time})

    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/setschedule', methods=['POST'])
def set_schedule():
    try:
        data = request.json
        d1_open_time = data['d1_open_time']
        d1_close_time = data['d1_close_time']
        d2_open_time = data['d2_open_time']
        d2_close_time = data['d2_close_time']
        d3_open_time = data['d3_open_time']
        d3_close_time = data['d3_close_time']
        d4_open_time = data['d4_open_time']
        d4_close_time = data['d4_close_time']
        d5_open_time = data['d5_open_time']
        d5_close_time = data['d5_close_time']
        d6_open_time = data['d6_open_time']
        d6_close_time = data['d6_close_time']
        d7_open_time = data['d7_open_time']
        d7_close_time = data['d7_close_time']

        d1_open_time = "2001-01-01 "+d1_open_time+":00"
        d1_close_time = "2001-01-01 "+d1_close_time+":00"
        d2_open_time = "2001-01-01 "+d2_open_time+":00"
        d2_close_time = "2001-01-01 "+d2_close_time+":00"
        d3_open_time = "2001-01-01 "+d3_open_time+":00"
        d3_close_time = "2001-01-01 "+d3_close_time+":00"
        d4_open_time = "2001-01-01 "+d4_open_time+":00"
        d4_close_time = "2001-01-01 "+d4_close_time+":00"
        d5_open_time = "2001-01-01 "+d5_open_time+":00"
        d5_close_time = "2001-01-01 "+d5_close_time+":00"
        d6_open_time = "2001-01-01 "+d6_open_time+":00"
        d6_close_time = "2001-01-01 "+d6_close_time+":00"
        d7_open_time = "2001-01-01 "+d7_open_time+":00"
        d7_close_time = "2001-01-01 "+d7_close_time+":00"

        list_time = []
        # for r in result_site:

        result_schedule = update_DB("UPDATE schedule_data SET time = CASE WHEN date = 'd1_open_time' THEN '"+str(d1_open_time)+"' WHEN date = 'd1_close_time' THEN '"+str(d1_close_time)+"' WHEN date = 'd2_open_time' THEN '"+str(d2_open_time)+"' WHEN date = 'd2_close_time' THEN '"+str(d2_close_time)+"' WHEN date = 'd3_open_time' THEN '"+str(d3_open_time)+"' WHEN date = 'd3_close_time' THEN '"+str(d3_close_time)+"' WHEN date = 'd4_open_time' THEN '"+str(d4_open_time)+"' WHEN date = 'd4_close_time' THEN '"+str(d4_close_time)+"' WHEN date = 'd5_open_time' THEN '"+str(d5_open_time)+"' WHEN date = 'd5_close_time' THEN '"+str(d5_close_time)+"' WHEN date = 'd6_open_time' THEN '"+str(d6_open_time)+"' WHEN date = 'd6_close_time' THEN '"+str(d6_close_time)+"' WHEN date = 'd7_open_time' THEN '"+str(d7_open_time)+"' WHEN date = 'd7_close_time' THEN '"+str(d7_close_time)+"' ELSE time END")
        # return str(result_schedule)
        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/logpsumavg', methods=['POST'])
def logpsumavg():
    try:
        data = request.json
        SiteID = data['SiteID']
        list_psum = []
        date_Psum = []
        Psum = []
        result_site = querySelect_DB("SELECT * FROM zone_info WHERE SiteID = '"+str(SiteID)+"'")

        list_meter = []
        for r in result_site:

            result_meter = querySelect_DB("SELECT MeterID,MeterName FROM meter_info WHERE ZoneID = '"+str(r['ZoneID'])+"'")
            list_meter.append(result_meter[0]['MeterID'])

        # return str(list_meter)

        #result = querySelect_DB("SELECT Log_Date,sum(Log_PSum) as Log_PSum,baseLine FROM cp_warehouse.meter_log left join cp_warehouse.meter_Info on cp_warehouse.meter_log.meterID = cp_warehouse.meter_Info.meterID left join cp_warehouse.zone_info on cp_warehouse.meter_Info.ZoneID = cp_warehouse.zone_Info.ZoneID left join cp_warehouse.site_info on cp_warehouse.zone_Info.SiteID = cp_warehouse.site_info.siteID WHERE log_date >= SUBDATE( CURRENT_TIMESTAMP, INTERVAL 2 HOUR) and (meter_log.meterID = '"+str(list_meter[0])+"' or meter_log.meterID = '"+str(list_meter[1])+"' or meter_log.meterID = '"+str(list_meter[2])+"') group by log_date order by log_date DESC")
        result = querySelect_DB("SELECT Log_Date,sum(Log_PSum) as Log_PSum,baseLine FROM cp_warehouse.meter_log left join cp_warehouse.meter_Info on cp_warehouse.meter_log.meterID = cp_warehouse.meter_Info.meterID left join cp_warehouse.zone_info on cp_warehouse.meter_Info.ZoneID = cp_warehouse.zone_Info.ZoneID left join cp_warehouse.site_info on cp_warehouse.zone_Info.SiteID = cp_warehouse.site_info.siteID WHERE day(log_date) = day(curdate()) and month(log_date) = month(curdate()) and year(log_date) = year(curdate()) and (meter_log.meterID = '"+str(list_meter[0])+"' or meter_log.meterID = '"+str(list_meter[1])+"' or meter_log.meterID = '"+str(list_meter[2])+"') group by log_date order by log_date DESC")
        # result = querySelect_DB("SELECT Log_Date,Log_PSum FROM meter_log WHERE MeterID = '"+MeterID+"' LIMIT 8")
        # print str(result)

        if result == [] or result == False:
            return jsonify({"status": "fail","message":"not found"})
        # return str(result)
        date_Psum = []
        Psum = []
        baseLine = []



        # a = ['0.00','1.00','2.00','3.00','4.00','5.00','6.00']

        # for i in a:
        checktimenew = ''
        checktimeold = ''

        if date_Psum == []:
            # n = 0
            # for k in result:
            i = 0
            # i = 134
            numtime = 0
            while i < 144:

                # date = str(k['Log_Date']).split()

                # time = date[1]
                # checktimenew = time[1]

                # print str(time)
                # print str(checktimenew)


                # if time[3] == '0':
                # # if checktimenew != checktimeold:
                #     date_Psum.append(date[1])

                #     # checktimeold = checktimenew
                # else:
                #     date_Psum.append('')
                # # n=n+1

                s = ":00:00"

                if i%6 == 0:
                # if checktimenew != checktimeold:
                    time = str(numtime).zfill(2)
                    # time = str(numtime).zfill(2)+s
                    date_Psum.append(time)
                    numtime = numtime +1
                    # checktimeold = checktimenew
                else:
                    date_Psum.append('')
                # n=n+1

                Psum.append('')
                i=i+1


        numj = len(result)-1
        # sss = len(date_Psum)-1
        # return str(sss)
        # return str(numj)

        for j in result:
            # print str(j['Log_PSum'])

            Psum[numj] = str(j['Log_PSum'])
            # Psum.append(str(j['Log_PSum']))
            numj = numj-1

        # for j in result:
        #     print str(j['baseLine'])
        #     baseLine.append(str(j['baseLine']))

        for j in Psum:
            # print str(j['baseLine'])
            baseLine.append(str(result[0]['baseLine']))

        name = 'Meter'            # num = num+1



        # return 'ok'
        # result.append({"name":str(name),"data":Psum })
        list_psum.append({"name":'Meter',"data":Psum })
        list_psum.append({"name":'Base Line',"data":baseLine })
        # return str(Reverse(date_Psum))
        # re_date_Psum = date_Psum.reverse()
        # return str(re_date_Psum)
        return jsonify({"status": "success","list_psum":list_psum,"date_Psum":date_Psum})

    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

def Reverse(lst):
    return [ele for ele in reversed(lst)]

@app.route('/logpsum', methods=['POST'])
def logpsumnew():
    try:
        data = request.json
        MeterID = data['MeterID']
        list_psum = []
        date_Psum = []
        Psum = []
        result_meter = querySelect_DB("SELECT MeterID,MeterName FROM meter_info WHERE MeterID = '"+str(MeterID)+"'")
        # return  str(result_meter)
        for i in result_meter:
            result = querySelect_DB("SELECT Log_Date,Log_PSum FROM meter_log WHERE log_date >= SUBDATE( CURRENT_TIMESTAMP, INTERVAL 2 HOUR) and MeterID = '"+str(MeterID)+"' ORDER BY Log_Date DESC")
            # result = querySelect_DB("SELECT Log_Date,Log_PSum FROM meter_log WHERE MeterID = '"+MeterID+"' LIMIT 8")
            print str(result)
            if result == [] or result == False:
                return jsonify({"status": "fail","message":"not found"})
            # return str(result)
            date_Psum = []
            Psum = []


            if date_Psum == []:
                for k in result:
                    date = str(k['Log_Date']).split()
                    date_Psum.append(date[1])


            for j in result:
                print str(j['Log_PSum'])
                Psum.append(str(j['Log_PSum']))
            name = i['MeterName']            # num = num+1



            # return 'ok'
            # result.append({"name":str(name),"data":Psum })
            list_psum.append({"name":str(name),"data":Reverse(Psum) })
            # return str(Reverse(date_Psum))
            # re_date_Psum = date_Psum.reverse()
            # return str(re_date_Psum)
        return jsonify({"status": "success","list_psum":list_psum,"date_Psum":Reverse(date_Psum)})

    except Exception as e:
        return jsonify({"status": "fail"})

@app.route('/logpsum2', methods=['POST'])
def logpsum2():
    try:
        data = request.json
        ZoneID = data['ZoneID']
        list_psum = []
        date_Psum = []
        Psum = []
        result_meter = querySelect_DB("SELECT MeterID,MeterName FROM meter_info WHERE ZoneID = '"+str(ZoneID)+"'")
        # return  str(result_meter)
        for i in result_meter:
            result = querySelect_DB("SELECT Log_Date,Log_PSum FROM meter_log WHERE MeterID = '"+str(i['MeterID'])+"' LIMIT 8")
            # result = querySelect_DB("SELECT Log_Date,Log_PSum FROM meter_log WHERE MeterID = '"+MeterID+"' LIMIT 8")
            print str(result)
            if result == [] or result == False:
                return jsonify({"status": "fail","message":"not found"})
            # return str(result)
            date_Psum = []
            Psum = []


            if date_Psum == []:
                for k in result:
                    date = str(k['Log_Date']).split()
                    date_Psum.append(date[1])


            for j in result:
                print str(j['Log_PSum'])
                Psum.append(str(j['Log_PSum']))
            name = i['MeterName']            # num = num+1



            # return 'ok'
            # result.append({"name":str(name),"data":Psum })
            list_psum.append({"name":str(name),"data":Psum })

        return jsonify({"status": "success","list_psum":list_psum,"date_Psum":date_Psum})

    except Exception as e:
        return jsonify({"status": "fail"})


@app.route('/logpsum3', methods=['POST'])
def logpsum3():
    try:
        data = request.json
        SiteID = data['SiteID']
        list_psum = []
        result_site = querySelect_DB("SELECT * FROM zone_info WHERE SiteID = '"+str(SiteID)+"'")


        for r in result_site:

            result_meter = querySelect_DB("SELECT MeterID,MeterName FROM meter_info WHERE ZoneID = '"+str(r['ZoneID'])+"'")
            # return  str(result_meter)
            for i in result_meter:
                result = querySelect_DB("SELECT Log_Date,Log_PSum FROM meter_log WHERE MeterID = '"+str(i['MeterID'])+"' LIMIT 8")
                # result = querySelect_DB("SELECT Log_Date,Log_PSum FROM meter_log WHERE MeterID = '"+MeterID+"' LIMIT 8")
                print str(result)
                if result == [] or result == False:
                    return jsonify({"status": "fail","message":"not found"})
                # return str(result)
                date_Psum = []
                Psum = []


                if date_Psum == []:
                    for k in result:
                        date = str(k['Log_Date']).split()
                        date_Psum.append(date[1])


                for j in result:
                    print str(j['Log_PSum'])
                    Psum.append(str(j['Log_PSum']))
                name = i['MeterName']            # num = num+1



            # return 'ok'
            # result.append({"name":str(name),"data":Psum })
                list_psum.append({"name":str(name),"data":Psum })

        return jsonify({"status": "success","list_psum":list_psum,"date_Psum":date_Psum})

    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/datameter', methods=['POST'])
def datameter():
    try:
        data = request.json

        SiteID = data['SiteID']
        list_data = []
        result_zone = querySelect_DB("SELECT * FROM zone_info WHERE SiteID = '"+SiteID+"'")

        for r in result_zone:
            result_meter = querySelect_DB("SELECT * FROM meter_info WHERE ZoneID = '"+str(r['ZoneID'])+"'")
            if result_meter == [] or result_meter == False:
                return jsonify({"status": "fail","message":"not found"})
            # result_meter = result_meter[0]


            for i in result_meter:
                list_data.append(
                    {
                    "ZoneName":str(r['ZoneName']),
                    "MeterName":str(i['MeterName']),
                    "RT_V1":str(i['RT_V1']),
                    "RT_V2":str(i['RT_V2']),
                    "RT_V3":str(i['RT_V3']),
                    "RT_V12":str(i['RT_V12']),
                    "RT_V23":str(i['RT_V23']),
                    "RT_V31":str(i['RT_V31']),
                    "RT_I1":str(i['RT_I1']),
                    "RT_I2":str(i['RT_I2']),
                    "RT_I3":str(i['RT_I3']),
                    "RT_In":str(i['RT_In']),
                    "RT_Pa":str(i['RT_Pa']),
                    "RT_Pb":str(i['RT_Pb']),
                    "RT_Pc":str(i['RT_Pc']),
                    "RT_PSum":str(i['RT_PSum']),
                    "RT_Qa":str(i['RT_Qa']),
                    "RT_Qb":str(i['RT_Qb']),
                    "RT_Qc":str(i['RT_Qc']),
                    "RT_PFa":str(i['RT_PFa']),
                    "RT_PFb":str(i['RT_PFb']),
                    "RT_PFc":str(i['RT_PFc']),
                    "RT_PFSum":str(i['RT_PFSum']),
                    "RT_Sa":str(i['RT_Sa']),
                    "RT_Sb":str(i['RT_Sb']),
                    "RT_Sc":str(i['RT_Sc']),
                    "RT_F":str(i['RT_F']),
                    "RT_kWh":str(i['RT_kWh']),
                    })


        return jsonify({"status": "success","datameter":list_data})

    except Exception as e:
        return jsonify({"status": "fail","messgae":str(e)})

@app.route('/logpsumall', methods=['POST'])
def logpsumall():
    try:
        data = request.json

        SiteID = data['SiteID']
        list_psum = []
        date_Psum = ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23"]
        Psum = []
        # return password
        diff = []
        now = datetime.datetime.now()
        time_start = str(now.date())+ " 00:00:00"
        time_stop = str(now.date())+ " 23:59:59"

        result_site = querySelect_DB("SELECT * FROM zone_info WHERE SiteID = '"+str(SiteID)+"'")
        # return 's'
        for s in result_site:

            result_meter = querySelect_DB("SELECT MeterID,MeterName FROM meter_info WHERE ZoneID = '"+str(s['ZoneID'])+"'")
            # return  str(result_meter)
            for i in result_meter:
                result_log = querySelect_DB("SELECT Hour(log_Date) HourInDay,sum(Log_kWh_Diff) as diff FROM cp_warehouse.meter_log where day(log_Date) = day(CURDATE())  and MeterID = '"+str(i['MeterID'])+"' group by HourInDay order by HourInDay")
                # result = querySelect_DB("SELECT Log_Date,Log_PSum FROM meter_log WHERE MeterID = '"+MeterID+"' LIMIT 8")
                # return str(result_log)
                if result_log == False:
                    return jsonify({"status": "fail","message":"query fail"})
                    # return str(result)
                Psum = []
                for d in date_Psum:
                    Psum.append("")

                if result_log != [] :

                    for j in result_log:
                         Psum[j['HourInDay']] = str(j['diff'])



                name = "ZoneID " +str(s['ZoneID'])+" ("+i['MeterName']+")"

                list_psum.append({"name":str(name),"data":Psum })

        return jsonify({"status": "success","list_psum":list_psum,"hour_Psum":date_Psum})

    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})



@app.route('/sumdayavg', methods=['POST'])
def sumdayavg():
    try:
        data = request.json

        SiteID = data['SiteID']
        list_psum = []
        date_Psum = []
        Psum = []
        result_site = querySelect_DB("SELECT * FROM zone_info WHERE SiteID = '"+str(SiteID)+"'")

        list_meter = []
        for r in result_site:

            result_meter = querySelect_DB("SELECT MeterID,MeterName FROM meter_info WHERE ZoneID = '"+str(r['ZoneID'])+"'")
            list_meter.append(result_meter[0]['MeterID'])

        result = querySelect_DB("SELECT month(log_Date) monthInYear,Day(log_Date) dayInMonth,sum(Log_kWh_Diff) as diff FROM cp_warehouse.meter_log where Month(log_Date) = MONTH(CURDATE()) And Year(log_date) = Year(CURDATE()) and (MeterID = '"+str(list_meter[0])+"' Or  MeterID = '"+str(list_meter[1])+"' Or MeterID = '"+str(list_meter[2])+"') group by dayInMonth order by dayInMonth")
        if result == [] or result == False:
            return jsonify({"status": "fail","message":"not found"})
        # return str(result[0]['monthInYear'])
        dayInMonth = []
        diff = []
        now = datetime.datetime.now()
        month_range = calendar.monthrange(now.year, now.month)[1]
        # return str(int(month_range)-1)


        month = calendar.month_name[result[0]['monthInYear']]

        for x in range(1, int(month_range)+1):
            date = str(month)+' '+str(x)
            dayInMonth.append(str(date))
            diff.append('0')
            # print str(x)


        for i in result:
            # print str(i['dayInMonth'])
            date = str(month)+' '+str(i['dayInMonth'])
            dayInMonth[i['dayInMonth']] = str(date)
            diff2 = int(i['diff'])
            # diff2 = float(i['diff'])/1000

            # diff2 = "%.1f" % diff2
            if str(diff2) == '0.00':
                diff2 = 0
            # return str(diff)
            diff[i['dayInMonth']] = str(diff2)
        month
        return jsonify({"status": "success","dayInMonth":dayInMonth,"diff":diff})

    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/sumday', methods=['POST'])
def sumday():
    try:
        data = request.json

        MeterID = data['MeterID']

        result = querySelect_DB("SELECT month(log_Date) monthInYear,Day(log_Date) dayInMonth,sum(Log_kWh_Diff) as diff FROM cp_warehouse.meter_log where Month(log_Date) = MONTH(CURDATE()) and MeterID = '"+str(MeterID)+"' group by dayInMonth order by dayInMonth limit 30")
        if result == [] or result == False:
            return jsonify({"status": "fail","message":"not found"})
        # return str(result[0]['monthInYear'])
        dayInMonth = []
        diff = []
        now = datetime.datetime.now()
        month_range = calendar.monthrange(now.year, now.month)[1]
        # return str(int(month_range)-1)


        month = calendar.month_name[result[0]['monthInYear']]

        for x in range(1, int(month_range)+1):
            date = str(month)+' '+str(x)
            dayInMonth.append(str(date))
            diff.append('0')
            # print str(x)


        for i in result:
            # print str(i['dayInMonth'])
            date = str(month)+' '+str(i['dayInMonth'])
            dayInMonth[i['dayInMonth']] = str(date)
            diff2 = int(i['diff'])
            # diff2 = float(i['diff'])/1000

            diff2 = "%.1f" % diff2
            if str(diff2) == '0.00':
                diff2 = 0
            # return str(diff)
            diff[i['dayInMonth']] = str(diff2)
        month
        return jsonify({"status": "success","dayInMonth":dayInMonth,"diff":diff})

    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/sumyearavg', methods=['POST'])
def sumyearavg():
    try:
        data = request.json

        SiteID = data['SiteID']
        list_psum = []
        date_Psum = []
        Psum = []
        result_site = querySelect_DB("SELECT * FROM zone_info WHERE SiteID = '"+str(SiteID)+"'")

        list_meter = []
        for r in result_site:

            result_meter = querySelect_DB("SELECT MeterID,MeterName FROM meter_info WHERE ZoneID = '"+str(r['ZoneID'])+"'")
            list_meter.append(result_meter[0]['MeterID'])

        result = querySelect_DB("SELECT month(log_Date) monthInYear,sum(Log_kWh_Diff) as diff FROM cp_warehouse.meter_log where year(log_Date) = year(CURDATE()) AND (MeterID = '"+str(list_meter[0])+"' Or  MeterID = '"+str(list_meter[0])+"' Or MeterID = '"+str(list_meter[0])+"' )group by monthInYear order by monthInYear;")
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
            diff2 = int(i['diff'])

            # diff2 = "%.1f" % diff2
            if str(diff2) == '0.00':
                diff2 = 0
            diff[i['monthInYear']-1] = str(diff2)

        return jsonify({"status": "success","monthInYear":monthInYear,"diff":diff})

    except Exception as e:
        return jsonify({"status": "fail","message":str(e)})

@app.route('/sumyear', methods=['POST'])
def sumyear():
    try:
        data = request.json

        MeterID = data['MeterID']
        result = querySelect_DB("SELECT month(log_Date) monthInYear,sum(Log_kWh_Diff) as diff FROM cp_warehouse.meter_log where year(log_Date) = year(CURDATE()) AND MeterID = '"+MeterID+"'group by monthInYear order by monthInYear;")
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
            diff2 = int(i['diff'])
            # diff2 = float(i['diff'])/1000

            diff2 = "%.1f" % diff2
            if str(diff2) == '0.00':
                diff2 = 0
            diff[i['monthInYear']-1] = str(diff2)

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
