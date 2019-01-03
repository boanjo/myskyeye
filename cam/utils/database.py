import cv2
import os
import time
import MySQLdb
import threading
import imutils
import logging

def upload_to_entry_db(date, time, duration, frames, motion_frames, path, file_name, objects):

    row_id = None
    
    # Open database connection
    db = MySQLdb.connect(host=str(os.environ['MYSQL_HOST']),
                         user=str(os.environ['MYSQL_USER']),
                         passwd=str(os.environ['MYSQL_PASSWORD']),
                         db=str(os.environ['MYSQL_DATABASE']),
                         port=int(os.environ['MYSQL_PORT']) )
    
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
        
    # Prepare SQL query to INSERT a record into the database.
    sql = "INSERT INTO motion(date, \
    time, duration, frame_count, motion_count, path, file_name, objects) \
    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' )" % \
    (date, time, duration, frames, motion_frames, path, file_name, objects)
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
        row_id = cursor.lastrowid
    except:
        # Rollback in case there is any error
        db.rollback()
        
        # disconnect from server
    db.close()
    return row_id

def upload_to_metadata_db(file_name, file_tb_name, weight):

    # Open database connection
    db = MySQLdb.connect(host=str(os.environ['MYSQL_HOST']),
                         user=str(os.environ['MYSQL_USER']),
                         passwd=str(os.environ['MYSQL_PASSWORD']),
                         db=str(os.environ['MYSQL_DATABASE']),
                         port=int(os.environ['MYSQL_PORT']) )
        
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = "INSERT INTO metadata(file_name, \
    file_tb_name, weight) \
    VALUES ('%s', '%s', '%s')" % \
    (file_name, file_tb_name, weight)
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
        row_id = cursor.lastrowid
    except:
        # Rollback in case there is any error
        db.rollback()
        
        # disconnect from server
    db.close()
    return row_id


def upload_to_db_task(best_frame, best_weight, time_str, start_time, frame_count, movement_count, acc_objects):
    if best_frame is not None:
        #print "Weight " + time_str + " = " + str(round(best_weight, 2)) 
        path = ""
        file_name = "images/" + time_str + ".jpg"
        file_tb_name = "images/" + time_str + "_tb.jpg"
        cv2.imwrite(path + file_name, best_frame)
        thumbnail = imutils.resize(best_frame, width=256)
        cv2.imwrite(path + file_tb_name, thumbnail)
        upload_to_metadata_db(file_name, file_tb_name, round(best_weight, 2))
                            
    duration = round((time.time() - start_time), 2)
    movie_date, movie_time = time_str.split('_')
    movie_time = movie_time.replace('.',':')
    input_file = time_str + ".avi"
    
    upload_to_entry_db(movie_date, movie_time, duration, frame_count,
                       movement_count, "input/", input_file, ','.join(acc_objects))
    
    logging.info("Uploaded " + time_str + " Weight " + str(round(best_weight, 2)))
    


def upload_to_db(best_frame, best_weight, time_str, start_time, frame_count, movement_count, acc_objects):
    t = threading.Thread(target=upload_to_db_task, args=(best_frame, best_weight, time_str, start_time, frame_count, movement_count, acc_objects,))
    t.start()
