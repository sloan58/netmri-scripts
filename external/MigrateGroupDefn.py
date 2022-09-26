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


def fetch_new_parent_id(parent_group):
    return group_broker_dst.search(**{
        'GroupName': parent_group.GroupName
    })[0].GroupID


def set_parent_group_id(group):
    parent_group_id = group.ParentDeviceGroupID
    if group.ParentDeviceGroupID != 0:
        parent_group = list(filter(lambda pgroup: pgroup.GroupID == group.ParentDeviceGroupID, group_list))[0]
        parent_group_id = fetch_new_parent_id(parent_group)
    return parent_group_id


def prepare_group_params(group):
    group.ParentDeviceGroupID = set_parent_group_id(group)
    group_dict = vars(group)
    del group_dict['broker']
    return group_dict


def create_group(group):
    print(
        f'Processing group {group.GroupName} with group id {group.GroupID}.  '
        f'Parent group id is {group.ParentDeviceGroupID}'
    )
    if group.ParentDeviceGroupID == 0 \
            or (group.ParentDeviceGroupID in created_groups and group.GroupID not in created_groups):
        print(f'Group {group.GroupName} is ready to be created.')
        group_dict = prepare_group_params(group)
        group_broker_dst.create(**group_dict)
        created_groups.append(group.GroupID)
        print(f'Created group {group.GroupName} and appended to created_groups list.')

    else:
        print(f'Group {group.GroupName} is NOT ready to be created.  Creating parent group first.')
        parent_group = list(filter(lambda pgroup: pgroup.GroupID == group.ParentDeviceGroupID, group_list))[0]
        print(f'Creating parent group {parent_group.GroupName}.')
        create_group(parent_group)


for group in group_broker_src.index():
    if not group.SystemGroupInd:
        group_list.append(group)

for group in group_list:
    create_group(group)
