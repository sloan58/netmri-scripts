import os
import sys
from copy import copy
from pprint import pprint

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
    print(f"{new_group.GroupName}@sanitize_params: Sanitizing https params")
    cast_to_str = [
        'ARPCacheRefreshInd',
        'AdvancedGroupInd',
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
    print(f"{new_group.GroupName}@create_group_on_dst: Calling NetMRI API to create group")
    payload = sanitize_params(new_group)
    try:
        res = group_broker_dst.create(**payload)
        print(f"{new_group.GroupName}@create_group_on_dst: NetMRI API returned successful")
        return res['id']
    except requests.exceptions.HTTPError as e:
        print(e.response.text)


def process_group(group):
    print(f"{group.GroupName}@process_group: Creating new group on destination")
    new_parent_id = create_group_on_dst(group)
    print(f"{group.GroupName}@process_group: Created new group (new GroupID: {new_parent_id})")
    if len(group.Children):
        print(f"{group.GroupName}@process_group: Adding child groups")
        for child in group.Children:
            print(f"{child.GroupName}@process_group: Processing child group")
            child.ParentDeviceGroupID = new_parent_id
            process_group(child)


def get_children(group):
    print(f"{group.GroupName}@get_children: Checking for child groups")
    children = list(filter(lambda cgroup: cgroup.ParentDeviceGroupID == group.GroupID, group_list_src))
    group.Children = children
    if len(children):
        print(f"{group.GroupName}@get_children: Found attached child groups ({len(children)} children)")
        children.sort(key=lambda child: child.GroupName)
        for child in children:
            print(f"{child.GroupName}@get_children: Processing child group")
            get_children(child)

    print(f"{group.GroupName}@get_children: Finished processing")
    return group


'''
Main Application

1. Collect Source and Destination NetMRI groups.
2. Compare top-level GroupNames to see if there are any groups  
   on the source that already exist on the destination.
3. If no top-level groups from the source exist on the destination,
   create each group from the source on the destination while 
   maintaining proper parent/child relationships.
   If top-level groups from the source do exist on the destination,
   return a warning that lists those groups and exit the script.
   
The primary functions are get_children and process_group.
Each are recursive functions that first build out the parent/child
relationship tree and then process them top-down to create 
new groups with relationships on the destination.

'''

print(f"Populating source NetMRI group list")
group_list_src = []
for group in group_broker_src.index():
    if not group.SystemGroupInd:
        group_list_src.append(group)

print(f"Setting source NetMRI group names list")
src_group_names = list(map(lambda sgroup: sgroup.GroupName, list(filter(lambda sgroup: sgroup.ParentDeviceGroupID == 0, group_list_src))))

print(f"Populating destination NetMRI group list")
group_list_dst = []
for group in group_broker_dst.index():
    if not group.SystemGroupInd:
        group_list_dst.append(group)

print(f"Setting destination NetMRI group names list")
dst_group_names = list(map(lambda dgroup: dgroup.GroupName, list(filter(lambda dgroup: dgroup.ParentDeviceGroupID == 0, group_list_dst))))

print(f"Checking if there are any matching groups between source and destination systems")
matches = list(filter(lambda dgroup: dgroup in src_group_names, dst_group_names))

if len(matches) == 0:
    print(f"No matching groups found!  Processing migration....")
    for group in group_list_src:
        if group.ParentDeviceGroupID == 0:
            print(f"{group.GroupName}: Processing top-level group")
            process_group(get_children(group))
else:
    print(
'''
######################################################################
#####################         WARNING          #######################
######################################################################

The source NetMRI host contains top-level groups that exist on the destination.
This will likely cause group mapping issues on the destination system.
Please address these groups before running this script again.
The source NetMRI system should not have any top-level groups that exist on the destination.

Exists on NetMRI Source and Destination:

'''
    )
    pprint(matches)