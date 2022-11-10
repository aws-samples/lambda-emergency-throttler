import boto3

lambdaClient = boto3.client("lambda")

def invokeLambda(name):
    response = lambdaClient.invoke(FunctionName = name, InvocationType = "Event")
    return response

def bulkInvokeLambda(name, count):
    for i in range(count):
        invokeLambda(name)
        print(i)
    return "Finished"
    
def getAllFunctionNames():
    results = []
    tempResults = lambdaClient.list_functions( MaxItems=50)
    for i in tempResults['Functions']:
        results.append(i["FunctionName"])
    hasMarker = False
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
    

    
def main():
    count = int(input("Enter an Integer for how many function invocations you'd like to trigger. I'd recommend under 20000\n"))
    
    functionNames = getAllFunctionNames()
    targetFunction = None
    while targetFunction is None:
        targetFunction = str(input("Enter the name of the function you would like to target. If the name is not found in your account, this will not work.\n"))
        if targetFunction not in functionNames:
            targetFunction = None
    confirmation = str(input(f"To confirm, you would like to send {count} request(s) to the function named {targetFunction}. To confirm, enter 'y'. Any other answer will end the script. If you would like to change your settings, press 'n' and restart the script\n"))
    if confirmation == "y":
        result = bulkInvokeLambda(targetFunction, count)
    else:
        result = 'Cancelled'

if __name__ == "__main__":
    main()