from typing import List, Dict
from flask import Flask
from flask import render_template
from flask import request
import mysql.connector
from mysql.connector import Error
import time
import calendar
import json
import re
import os
import datetime

app = Flask(__name__, static_url_path='/static')

def get_last_events(num_event, mjpg_replay_url):
    ret_str = ''
    try:
        connection = mysql.connector.connect(host=str(os.environ['MYSQL_HOST']),
                                             user=str(os.environ['MYSQL_USER']),
                                             passwd=str(os.environ['MYSQL_PASSWORD']),
                                             db=str(os.environ['MYSQL_DATABASE']),
                                             port=int(os.environ['MYSQL_PORT']) )
        
        cursor = connection.cursor()
        cursor.execute('SELECT file_name, file_tb_name FROM metadata ORDER BY id DESC LIMIT ' + str(num_event))
        
        count = 1
        for (file_name, file_tb_name) in cursor:
            
            m = re.search(".*/(.*).jpg", file_name)
            if m:
                heading = m.group(1)
                
                ret_str += ''' 
                <div class="grid-item" style="width:266px;height:184px;">    
	          <div class="header"> 
                  (''' + str(count) + ''') ''' + heading + '''
                  </div>
	          <a target="_blank" rel="noopener noreferrer" href="''' + mjpg_replay_url + heading + '''.mjpg"> 
                  <img src="/static/''' + file_tb_name + '''" alt="/static/''' + file_name + '''"></a>
	        </div>'''
            count = count + 1   
        cursor.close()
    except Error as e :
        print ("Error while connecting to MySQL", e)
    finally:
        #closing database connection.
        if(connection.is_connected()):
            connection.close()

    return ret_str



def get_series_json(date_str):      

    try:
        connection = mysql.connector.connect(host=str(os.environ['MYSQL_HOST']),
                                             user=str(os.environ['MYSQL_USER']),
                                             passwd=str(os.environ['MYSQL_PASSWORD']),
                                             db=str(os.environ['MYSQL_DATABASE']),
                                             port=int(os.environ['MYSQL_PORT']) )
        
        cursor = connection.cursor()
        cursor.execute('SELECT date,time,frame_count,motion_count,objects FROM motion WHERE date="' + str(date_str) + '"')
        
        series_dict = dict()
        for [date,t,frame_count,motion_count,objects] in cursor:
            
            [Y, M, D] = re.split("-", str(date))
            [H, Min, S] = re.split(":",str(t))
            
            motion_percent = (float(motion_count) * 100) / float(frame_count)
            unix_time = calendar.timegm((int(Y),int(M),int(D),int(H),int(Min),int(S),0,0,0))
            unix_time_ms = int(unix_time) * 1000
            
            obj_list = []
            if len(objects) > 0: 
                obj_list = re.split(",", objects)
                
            #  They all have motion...
            obj_list.append('Motion')

            for obj in obj_list:
                series_dict.setdefault(obj, []).append([unix_time_ms,motion_percent])

        cursor.close()
    except Error as e :
        print ("Error while connecting to MySQL", e)
    finally:
        #closing database connection.
        if(connection.is_connected()):
            connection.close()


    ret_list = []
    index = 0
    for key in series_dict:

        series = dict()

        series['name'] = key
        series['color'] = get_color(index)
        series['data'] = series_dict.get(key)
        ret_list.append(series)
        index = index + 1
    return json.dumps(ret_list)


def get_color(index):
    table = [
        'rgba(255, 153, 0, .5)',
        'rgba(255, 0, 0, .5)',
        'rgba(153, 153, 0, .5)',
        'rgba(51, 255, 0, .5)',
        'rgba(51, 102, 0, .5)',
        'rgba(0, 153, 255, .5)',
        'rgba(0, 0, 255, .5)']

    return table[index % 7]
    

@app.route('/api_get_series_json')
def api_get_series_json():

    date = request.args.get('date')
    if date is None:
        date = datetime.datetime.today().strftime('%Y-%m-%d')
    data = get_series_json(date)
    
    return data


@app.route('/dashboard')
def dashboard():
    mjpg_replay_url = str(os.environ['MJPG_REPLAY_URL'])
    live_cam_1_url = str(os.environ['LIVE_CAM_1_URL'])
    live_cam_2_url = str(os.environ['LIVE_CAM_2_URL'])

    last_events = get_last_events(16, mjpg_replay_url)

    print(datetime.datetime.today().strftime('%Y-%m-%d_%H:%M:%s'))
    
    return render_template('dashboard.html',
                           title='My Sky Eye dashboard',
                           last_event_divs=str(last_events),
                           mjpg_replay_url=mjpg_replay_url,
                           live_cam_1_url=live_cam_1_url,
                           live_cam_2_url=live_cam_2_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0')


