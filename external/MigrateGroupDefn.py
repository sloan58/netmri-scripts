import os
import sys
from copy import copy

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


def sanitize_params(new_group):
    cast_to_str = [
        'ARPCacheRefreshInd',
        'AdvancedGroupInd',
        # 'ConfigLocked',
        'IncludeEndHostsInd',
        'NetBIOSScanningInd',
        'PerfEnvPollingInd',
        'PrivilegedPollingInd',
        'SAMLicensedInd',
        'SPMCollectionInd',
        'SystemGroupInd',
        'UseGlobalPolFreq',
    ]
    group_dict = copy(vars(new_group))
    del group_dict['broker']
    del group_dict['GroupID']
    del group_dict['Children']
    for cast in cast_to_str:
        group_dict[cast] = 'True' if group_dict[cast] else 'False'
    return group_dict


def create_group_on_dst(new_group):
    payload = sanitize_params(new_group)
    try:
        res = group_broker_dst.create(**payload)
        return res['id']
    except requests.exceptions.HTTPError as e:
        print(e.response.text)


def process_group(group):
    new_parent_id = create_group_on_dst(group)
    if len(group.Children):
        for child in group.Children:
            child.ParentDeviceGroupID = new_parent_id
            process_group(child)


def get_children(group):
    children = list(filter(lambda cgroup: cgroup.ParentDeviceGroupID == group.GroupID, group_list))
    group.Children = children
    if len(children):
        children.sort(key=lambda child: child.GroupName)
        for child in children:
            get_children(child)
    return group


group_list = []
for group in group_broker_src.index():
    if not group.SystemGroupInd:
        group_list.append(group)


for group in group_list:
    if group.ParentDeviceGroupID == 0:
        process_group(get_children(group))
