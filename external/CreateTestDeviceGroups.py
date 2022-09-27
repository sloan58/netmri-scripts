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

source_group = group_broker.index()[0]

parent_groups = ['Parent_Group_1', 'Parent Group 1', 'ParentGroup1']
child_groups = ['Child_Group_1', 'Child Group 1', 'ChildGroup1']

for parent in parent_groups:
    new_parent = copy(vars(source_group))
    del new_parent['broker']
    del new_parent['GroupID']
    new_parent['GroupName'] = parent
    parent_id = group_broker.create(**new_parent)['id']
    for child in child_groups:
        new_child = copy(vars(source_group))
        del new_child['broker']
        del new_child['GroupID']
        new_child['GroupName'] = child
        new_child['ParentDeviceGroupID'] = parent_id
        group_broker.create(**new_child)
