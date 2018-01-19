# Copyright 2017 Amazon.com, Inc. or its affiliates
# Modified by Alice Xue - January 2018

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import boto3
from xml.etree import ElementTree as ET
import datetime
import pandas as pd
import os
import sys

##### Example command line input: python create_hit.py None sandbox MDMMT

# Before connecting to MTurk, set up your AWS account and IAM settings as
# described here:
# https://blog.mturk.com/how-to-use-iam-to-control-api-access-to-your-mturk-account-76fe2c2e66e2
#
# Follow AWS best practices for setting up credentials here:
# http://boto3.readthedocs.io/en/latest/guide/configuration.html

# Use the Amazon Mechanical Turk Sandbox to publish test Human Intelligence
# Tasks (HITs) without paying any money.  Sign up for a Sandbox account at
# https://requestersandbox.mturk.com/ with the same credentials as your main
# MTurk account.

if(len(sys.argv) < 4):
    print("You must pass profile name as the second argument or None.")
    print("You must pass 'live' or 'sandbox' as the third argument.")
    print("You must pass the expId as the fourth argument.")
    sys.exit(-1)

if sys.argv[2] == 'sandbox':
    create_hits_in_live = False
elif sys.argv[2] == 'live':
    create_hits_in_live = True
else:
    print("You must pass 'live' or 'sandbox' as first argument")
    sys.exit(-1)

expId = sys.argv[3]

environments = {
        "live": {
            "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
            "preview": "https://www.mturk.com/mturk/preview",
            "manage": "https://requester.mturk.com/mturk/manageHITs",
            "reward": "0.00"
        },
        "sandbox": {
            "endpoint": "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
            "preview": "https://workersandbox.mturk.com/mturk/preview",
            "manage": "https://requestersandbox.mturk.com/mturk/manageHITs",
            "reward": "3.00"
        },
}
mturk_environment = environments["live"] if create_hits_in_live else environments["sandbox"]

# use profile if one was passed as an arg, otherwise
profile_name = sys.argv[1] if len(sys.argv) >= 2 and sys.argv[1] != 'None' else None
session = boto3.Session(profile_name=profile_name)
client = session.client(
    service_name='mturk',
    region_name='us-east-1',
    endpoint_url=mturk_environment['endpoint'],
)

# Test that you can connect to the API by checking your account balance
user_balance = client.get_account_balance()

# In Sandbox this always returns $10,000. In live, it will be your acutal balance.
print "Your account balance is {}".format(user_balance['AvailableBalance'])

# Generate URL for External Quesiton
# Format of URL: https://calkins.psych.columbia.edu/expId?live=False
# Write expId and live value to xml file first
tree = ET.parse("my_external_question.xml")
root = tree.getroot()
url = root.find('{http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd}ExternalURL')
url.text = "https://calkins.psych.columbia.edu/" + expId + "?" + "live=" + str(create_hits_in_live)
tree.write("my_external_question.xml")

# The question we ask the workers is contained in this file.
question_sample = open("my_external_question.xml", "r").read()

# Example of using qualification to restrict responses to Workers who have had
# at least 80% of their assignments approved. See:
# http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationRequirementDataStructureArticle.html#ApiReference_QualificationType-IDs

masters = {
    "live": {
            'QualificationTypeId': '2ARFPLSP75KLA8M8DH1HTEQVJT3SY6',
            'Comparator': 'Exists'
    },
    "sandbox": {
        'QualificationTypeId': '2F1QJWKUDD8XADTFD2Q0G6UTO95ALH',
        'Comparator': 'Exists'
    },   
}

'''
    # Masters

    {
    # Worker_NumberHITsApproved
    'QualificationTypeId': '00000000000000000040',
    'Comparator': 'GreaterThanOrEqualTo',
    'IntegerValues': [100],
    'RequiredToPreview': True,
    },
    '''

worker_requirements = [
    
    {
    # Worker_Locale
    'QualificationTypeId': '00000000000000000071',
    'Comparator': 'EqualTo',
    'LocaleValues': [{
        'Country':"US",
        }],
    'RequiredToPreview': True,
    }

]

# Create the HIT
response = client.create_hit(
    MaxAssignments=3,
    LifetimeInSeconds=331200,
    AssignmentDurationInSeconds=3600,
    Reward=mturk_environment['reward'],
    Title='What snack do you prefer?',
    Keywords='research,psych,psychology,food,preferences',
    Description='You will rate how much you like snack foods and which one you prefer. Although we have allocated an hour for you to complete this study, it should only take you about 30 minutes. This HIT cannot be completed on a mobile device. You need a mouse and a keyboard.',
    Question=question_sample,
    QualificationRequirements=worker_requirements,
)

# The response included several fields that will be helpful later
hit_type_id = response['HIT']['HITTypeId']
hit_id = response['HIT']['HITId']
print "\nCreated HIT: {}".format(hit_id)

print "\nYou can work the HIT here:"
print mturk_environment['preview'] + "?groupId={}".format(hit_type_id)

print "\nAnd see results here:"
print mturk_environment['manage']

info = response['HIT']
info.update(response['ResponseMetadata'])
df = pd.DataFrame(data=info, index=[0])
_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)
csvLocation = _thisDir + '/' + expId +'/HIT_' + str(hit_id) + '.csv'
df.to_csv(csvLocation,index=False)

