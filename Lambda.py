####serializeImageData(Lambda 1)
import json
import boto3
import base64

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']

    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    try:
        s3_client.download_file(bucket, key, '/tmp/image.png')
    except Exception as ex:
        print(ex)
        return {'statusCode':500,
                'body':str(ex)}


    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }


##scoresInference(Lambda 2)
import json
import sys
import boto3
import base64


# # Fill this in with the name of your deployed model
ENDPOINT = "sconesEndpoint-1"

def lambda_handler(event, context):
    print(event)
    # Decode the image data
    image = base64.b64decode(event['body']['image_data'])

    # Instantiate a Predictor
    predictor= boto3.client('runtime.sagemaker')

    # For this model the IdentitySerializer needs to be "image/png"
  

    # Make a prediction:
    inferences = predictor.invoke_endpoint(EndpointName=ENDPOINT,
                                ContentType='image/png',
                                       Body=image)

    # We return the data back to the Step Function    
    event["inferences"] = inferences['Body'].read().decode('utf-8')
    return {
        'statusCode': 200,
        'body': {"inferences":event["inferences"]}
    }


##scoresThreshold (Lambda 3)
import json
import ast
import boto3

THRESHOLD = .80


def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event['body']['inferences']

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold=False
    print(type(inferences))
    for i in ast.literal_eval(inferences):
        if(float(i)>THRESHOLD):
            meets_threshold=True
            break
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        print("Entered error")
        client = boto3.client(
            "sns",
        )
        
        # Send your sms message.
        response = client.publish(
           
            TopicArn="arn:aws:sns:us-east-1:866595538391:topic1",
            Message="Hello, this is the test message AWS SNS! The classification model has not met the threshold.",
            Subject="SNS Test"
        ) 
      
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
