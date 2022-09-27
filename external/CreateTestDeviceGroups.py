import os
import sys
from copy import copy

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

source_group = group_broker.search(**{
    'GroupName': 'BasicGroup'
})[0]

parent_groups = [
    {
        'name': 'API_LAN_GROUP',
        'child': 'Child_Group_1'
    },
    {
        'name': 'API LAN GROUP',
        'child': 'Child Group 1'
    },
    {
        'name': 'APILANGroup',
        'child': 'ChildGroup1'
    },
]

for parent in parent_groups:
    new_parent = copy(vars(source_group))
    del new_parent['broker']
    del new_parent['GroupID']
    new_parent['GroupName'] = parent['name']
    parent_id = group_broker.create(**new_parent)['id']

    # new_child = copy(vars(source_group))
    # del new_child['broker']
    # del new_child['GroupID']
    # new_child['GroupName'] = parent['child']
    # new_child['ParentDeviceGroupID'] = parent_id
    # group_broker.create(**new_child)
