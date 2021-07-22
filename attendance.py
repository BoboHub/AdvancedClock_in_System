# USAGE
# python attendance.py --conf config/config.json
# Student: Boris Figeczky x15048179
# Date: 10/05/2020
# Resource2: https://www.pyimagesearch.com/raspberry-pi-for-computer-vision/ (Hacker Bundle, by Adrian Rosebrock, PHd)
# Resource2: https://www.udemy.com/course/introduction-to-aws-iot
# Resource3: https://docs.aws.amazon.com/iot/latest/developerguide/iot-moisture-tutorial.html

# import the necessary packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from pyimagesearch.utils import Conf
from imutils.video import VideoStream
from datetime import datetime
from datetime import date
from tinydb import TinyDB
from tinydb import where
import face_recognition
import numpy as np
import argparse
import imutils
import pyttsx3
import pickle
import time
import cv2
import json


# AWS IoT certificate based connection
myMQTTClient = AWSIoTMQTTClient("myClientID")
# myMQTTClient.configureEndpoint("YOUR.ENDPOINT", 8883)
# add certs 
myMQTTClient.configureEndpoint("xxxxxxxxx-ats.iot.eu-west-1.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/pi/Desktop/cert/Amazon_Root_CA_1.pem", "/home/pi/Desktop/cert/xxxxxxxxxx-private.pem.key", "/home/pi/Desktop/cert/xxxxxxxxxx-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

#connect and publish
myMQTTClient.connect()
myMQTTClient.publish("vision/info", "connected", 0)

############convert seconds to h/m/s
def convert(seconds): 
    return time.strftime("%H:%M:%S", time.gmtime(timeRemainingSeconds))

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True, 
    help="Path to the input configuration file")
args = vars(ap.parse_args())

# load the configuration file
conf = Conf(args["conf"])

# initialize the database, employee table, and attendance table
# objects
db = TinyDB(conf["db_path"])
employeeTable = db.table("employee")
attendanceTable = db.table("attendance")

# load the actual face recognition model along with the label encoder
recognizer = pickle.loads(open(conf["recognizer_path"], "rb").read())
le = pickle.loads(open(conf["le_path"], "rb").read())

# initialize the video stream and allow the camera sensor to warmup
print("[INFO] warming up camera...")
# vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# initialize previous and current person to None
prevPerson = None
curPerson = None

# initialize consecutive recognition count to 0
consecCount = 0

# using speakers 
# initialize the text-to-speech engine, set the speech language, and
# the speech rate
print("[INFO] taking attendance...")
ttsEngine = pyttsx3.init()
ttsEngine.setProperty("voice", conf["language"])
ttsEngine.setProperty("rate", conf["rate"])

# initialize a dictionary to store the employee ID and the time at
# which their attendance was taken
employeeDict = {}

# loop over the frames from the video stream
while True:
    # store the current time and calculate the time difference
    # between the current time and the time for the class
    currentTime = datetime.now()
    timeDiff = (currentTime - datetime.strptime(conf["timing"],
        "%H:%M")).seconds

    # grab the next frame from the stream, resize it and flip it
    # horizontally
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
    frame = cv2.flip(frame, 1)

    # if the maximum time limit to record attendance has been crossed
    # then skip the attendance taking procedure
    if timeDiff > conf["max_time_limit"]:
        # check if the employee dictionary is not empty
        if len(employeeDict) != 0:
            # insert the attendance into the database and reset the
            # employee dictionary
            attendanceTable.insert({str(date.today()): employeeDict})
            employeeDict = {}

        # draw info such as class, class timing, and current time on
        # the frame
        cv2.putText(frame, "Class: {}".format(conf["class"]),
            (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.putText(frame, "Work timing: {}".format(conf["timing"]),
            (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.putText(frame, "Current time: {}".format(
            currentTime.strftime("%H:%M:%S")), (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # show the frame
        cv2.imshow("Attendance System", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

        # skip the remaining steps since the time to take the
        # attendance has ended
        continue

    # convert the frame from RGB (OpenCV ordering) to dlib 
    # ordering (RGB)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # detect the (x, y)-coordinates of the bounding boxes
    # corresponding to each face in the input image
    boxes = face_recognition.face_locations(rgb,
        model=conf["detection_method"])

    # loop over the face detections
    for (top, right, bottom, left) in boxes:
        # draw the face detections on the frame
        cv2.rectangle(frame, (left, top), (right, bottom),
            (0, 255, 0), 2)

    # calculate the time remaining for attendance to be taken
    timeRemainingSeconds = conf["max_time_limit"] - timeDiff
    ############# convert to string
    timeRemaining = str(convert(timeRemainingSeconds))
    
    
    # draw info such as class, class timing, current time, and
    # remaining attendance time on the frame
    cv2.putText(frame, "Class: {}".format(conf["class"]), (10, 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv2.putText(frame, "Work begins: {}".format(conf["timing"]),
        (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv2.putText(frame, "Current time: {}".format(
        currentTime.strftime("%H:%M:%S")), (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv2.putText(frame, "Time remaining: {}s".format(timeRemaining),
        (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # check if atleast one face has been detected   
    if len(boxes) > 0:
        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)
                
        # perform classification to recognize the face
        preds = recognizer.predict_proba(encodings)[0]
        j = np.argmax(preds)
        curPerson = le.classes_[j]

        # if the person recognized is the same as in the previous
        # frame then increment the consecutive count
        if prevPerson == curPerson:
            consecCount += 1

        # otherwise, these are two different people so reset the 
        # consecutive count 
        else:
            consecCount = 0

        # set current person to previous person for the next
        # iteration
        prevPerson = curPerson
                
        # if a particular person is recognized for a given
        # number of consecutive frames, we have reached a 
        # positive recognition and alert/greet the person accordingly
        if consecCount >= conf["consec_count"]:
            # check if the employee's attendance has been already
            # taken, if not, record the employee's attendance
            if curPerson not in employeeDict.keys():
                employeeDict[curPerson] = datetime.now().strftime("%H:%M:%S")
            
                # get the employee's name from the database and let them
                # know that their attendance has been taken
                name = employeeTable.search(where(
                    curPerson))[0][curPerson][0]
                ttsEngine.say("{} your attendance has been taken.".format(
                    name))
                ttsEngine.runAndWait()
 ######################### ---Amazon AWS--- ###########################################            
                
            # construct a label saying the employee has their attendance
            # taken and draw it on to the frame
            label = "{}, you are now marked as present in {}".format(
                name, conf["class"])
            
            # testing output 
            #convert to JSON object
            date_time_now = datetime.now()
            #dt = str(date_time_now.strftime("%Y-%m-%d %H:%M:%S"))
            #split the date and time or else the AWS will not recognize it
            d = str(date_time_now.strftime("%Y-%m-%d"))
            t = str(date_time_now.strftime("%H:%M:%S"))
            data_dict = {'timestamp': d+" "+t, 'name': name}
            data_json = json.dumps(data_dict)
            print(data_dict)
            payload = data_json
            # send the pyload to vision/data topic on AWS IoT MQTT
            myMQTTClient.publish("vision/data",payload, 0)
            
            
            
            cv2.putText(frame, label, (5, 175),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # otherwise, we have not reached a positive recognition and
        # ask the employee to stand in front of the camera
        else:
            # construct a label asking the employee to stand in fron
            # to the camera and draw it on to the frame
            label = "Please stand in front of the camera"
            cv2.putText(frame, label, (5, 175),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            # testing output 
            print ("Dont move")

    # show the frame
    cv2.imshow("Attendance System", frame)
    key = cv2.waitKey(1) & 0xFF

    # check if the `q` key was pressed
    if key == ord("q"):
        # check if the employee dictionary is not empty, and if so,
        # insert the attendance into the database
        if len(employeeDict) != 0:
            attendanceTable.insert({str(date.today()): employeeDict})
            
        # break from the loop
        break

# clean up
print("[INFO] cleaning up...")
vs.stop()
db.close()
