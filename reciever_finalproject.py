#!/usr/bin/env python

# Student: Boris Figeczky x15048179
# Date: 10/05/2020
# Resource1: https://www.udemy.com/course/introduction-to-aws-iot
# Resource2: https://docs.aws.amazon.com/iot/latest/developerguide/iot-moisture-tutorial.html

import boto3
import os
import time
from grovepi import *

# Connect the Grove LED to digital port D4
led = 4
pinMode(led,"OUTPUT")
time.sleep(1)
# provide credetials 
access_key = "provide credetials"
access_secret = "provide credetials"
region ="eu-west-1"
queue_url = "https://sqs.eu-west-1.amazonaws.com/535587243099/MyRPi2_vision_Queue1"

# max number of messages from the aws queue
def pop_message(client, url):
    response = client.receive_message(QueueUrl = url, MaxNumberOfMessages = 10)

    #last message posted becomes messages
    message = response['Messages'][0]['Body'] # create body of the message
    receipt = response['Messages'][0]['ReceiptHandle'] # create the receipt
    # delete the message from the queue
    client.delete_message(QueueUrl = url, ReceiptHandle = receipt)
    return message
# secure access using the certs 
client = boto3.client('sqs', aws_access_key_id = access_key, aws_secret_access_key = access_secret, region_name = region)

waittime = 20
client.set_queue_attributes(QueueUrl = queue_url, Attributes = {'ReceiveMessageWaitTimeSeconds': str(waittime)})
# declearing start time of exectution
time_start = time.time()
while (time.time() - time_start <60):
    print("Checking...")
    try:
        message = pop_message(client, queue_url)
        print(message)
        if message:
            #Blink the LED
            digitalWrite(led,1)     # Send HIGH to switch on LED
            print ("LED ON!")
            time.sleep(5)
            digitalWrite(led,0)     # Send LOW to switch off LED
            print ("LED OFF!")
    except:
            pass
        
            
        
        
        

