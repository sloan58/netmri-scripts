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

# Parent with space or underscore
# Child without space or underscore
parent_groups = ['Parent_Group_1', 'ParentGroup1']
child_groups = ['Child_Group_1', 'ChildGroup1']

# Parent without space or underscore
# Child with space or underscore
group_broker.create(**{
    'Criteria': '$Assurance < 20 and $Name eq "foobar2"',
    'GroupName': 'TestFromApi'
})