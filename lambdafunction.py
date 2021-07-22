#name: Boris Figeczky
#student no.: x15048179
#code reference 1: makerdemy https://www.udemy.com/course/introduction-to-aws-iot


#import AWS SDK for python
import boto3

#add credetntials 
access_key = "provide credentials"
access_secret = "provide credentials"
region ="eu-west-1"
queue_url = "https://sqs.eu-west-1.amazonaws.com/xxxxxxxxxxxx/MyRPi2_vision_Queue1"

# declering a function with three arguments 
def post_message(client, message_body, url):
    #send it to decleared queue_url with a message body
	response = client.send_message(QueueUrl = url, MessageBody= message_body)

def lambda_handler(event, context):
    #providing the credentials to boto3
    client = boto3.client('sqs', aws_access_key_id = access_key, aws_secret_access_key = access_secret, region_name = region)
    #if themperature is is higher then 25 ON message when it is eqal or bolow OFF message
    x = event['name']
    if x=='Charlize':
        post_message(client, 'on', queue_url)
        message = "on"
        print("its ON")
    else: 
        post_message(client, 'no access', queue_url)
        message = "no access"
        print("no access")
