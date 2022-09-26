import os
import sys

import requests
from dotenv import load_dotenv
from infoblox_netmri import InfobloxNetMRI

load_dotenv()

try:
    net_mri_client_src = InfobloxNetMRI(
        host=os.getenv('NETMRI_HOST'),
        username=os.getenv('NETMRI_USER'),
        password=os.getenv('NETMRI_PASSWORD')
    )

    net_mri_client_dst = InfobloxNetMRI(
        host=os.getenv('NETMRI_HOST_DST'),
        username=os.getenv('NETMRI_USER_DST'),
        password=os.getenv('NETMRI_PASSWORD_DST')
    )

except requests.exceptions.ConnectionError as e:
    print('Could not connect to NetMRI')
    sys.exit()


group_broker_src = net_mri_client_src.get_broker('DeviceGroupDefn')
group_broker_dst = net_mri_client_dst.get_broker('DeviceGroupDefn')

group_list = []
created_groups = []

def create_group(group):
    print(f'Processing group {group.GroupName} with group id {group.GroupID} and parent group id {group.ParentDeviceGroupID}')
    if group.ParentDeviceGroupID == 0 or (group.ParentDeviceGroupID in created_groups and group.GroupID not in created_groups):
        print(f'Group either has parent id 0 or parent group was already created.  Creating this group now.')
        print(f'Appending to created_groups list')
        created_groups.append(group.GroupID)
        print(created_groups)

    else:
        print(f'Parent group {group.ParentDeviceGroupID} does not exist.  Creating now')
        parent_group = list(filter(lambda pgroup: pgroup.GroupID == group.ParentDeviceGroupID, group_list))[0]
        create_group(parent_group)


for group in group_broker_src.index():
    if not group.SystemGroupInd:
        group_list.append(group)

for group in group_list:
    create_group(group)
