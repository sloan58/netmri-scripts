import os
import sys

import requests
from dotenv import load_dotenv
from infoblox_netmri import InfobloxNetMRI

load_dotenv()


try:
    net_mri_client = InfobloxNetMRI(
        host=os.getenv('NETMRI_HOST'),
        username=os.getenv('NETMRI_USER'),
        password=os.getenv('NETMRI_PASSWORD')
    )
except requests.exceptions.ConnectionError as e:
    print('Could not connect to NetMRI')
    sys.exit()


group_broker = net_mri_client.get_broker('DeviceGroupDefn')

group_broker.create(**{
    'Criteria': '$Assurance < 20 and $Name eq "foobar2"',
    'GroupName': 'TestFromApi'
})