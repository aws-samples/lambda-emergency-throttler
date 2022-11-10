import json
import boto3
import os
# import requests

lambdaClient = boto3.client("lambda")
snsClient = boto3.client("sns")
def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    print("event: {}".format(event)) 
    print("context: {}".format(context))
    totalNumberOfFunctions = 0
    try:
        totalNumberOfFunctions = killAllConcurrency(context)
        response = snsClient.publish(TopicArn=os.environ["targetSNSArn"], Message = "LambdaKiller has successfully executed. The concurrency of all other Lambda functions is now 0")
        statusCode = 200
        
    except:
        print("An error has occured")
        statusCode = 500
        response = snsClient.publish(TopicArn=os.environ["targetSNSArn"], Message = "LambdaKiller has triggered by not successfully executed. Check your functions, as one may be running at a high concurrency")
    lambdaReturn = {
        "statusCode": statusCode,
        "body": json.dumps({
            "functionsStopped": str(totalNumberOfFunctions),
            # "location": ip.text.replace("\n", "")
        }),
    }
    return lambdaReturn
def getAllFunctionNames():
    #retrives the names of all the functions in the account
    results = []
    tempResults = lambdaClient.list_functions( MaxItems=50)
    for i in tempResults['Functions']:
        results.append(i["FunctionName"])
    hasMarker = False
    #executes if there are more than 50 functions
    if 'NextMarker' in tempResults.keys():
        hasMarker = tempResults['NextMarker']
    while hasMarker:
        tempResults = lambdaClient.list_functions(Marker = hasMarker,  MaxItems=50)

        for i in tempResults['Functions']:
            results.append(i["FunctionName"])
        if "NextMarker" not in tempResults.keys():
            hasMarker = False
        else:
            hasMarker = tempResults['NextMarker']
    
    return results

def killAllConcurrency(context):
    #gets all the function names and then sets their concurrency to zero to stop execution
    functionNames = set(getAllFunctionNames())
    #uses the context object to exclude itself
    functionNames.remove(context.function_name)
    for i in functionNames:
        lambdaClient.put_function_concurrency(FunctionName = i, ReservedConcurrentExecutions=0)
    return len(functionNames)