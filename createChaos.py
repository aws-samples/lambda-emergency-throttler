# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import boto3


sessionName = str(input("Enter the name of the profile in your AWS Credentials File you would like use. If using the default, enter default\n"))

session = boto3.Session(profile_name=sessionName)

lambdaClient = session.client('lambda')
def invokeLambda(name):
    response = lambdaClient.invoke(FunctionName = name, InvocationType = "RequestResponse")
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
