import json
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
    try:
        return group_broker_dst.search(**{
            'GroupName': parent_group.GroupName
        })[0].GroupID
    except requests.exceptions.HTTPError as e:
        print(e.response.text)


def create_group_on_dst(group_dict, parent_group_id):
    try:
        group_broker_dst.create(**{
            'ARPCacheRefreshInd': group_dict['ARPCacheRefreshInd'],
            'AdvancedGroupInd': group_dict['AdvancedGroupInd'],
            'BlackoutDuration': group_dict['BlackoutDuration'],
            'CCSCollection': group_dict['CCSCollection'],
            'CLIPolling': group_dict['CLIPolling'],
            'ConfigLocked': group_dict['ConfigLocked'],
            'ConfigPolling': group_dict['ConfigPolling'],
            'CredentialGroupID': group_dict['CredentialGroupID'],
            'Criteria': group_dict['Criteria'],
            'FingerPrint': group_dict['FingerPrint'],
            'GroupName': group_dict['GroupName'],
            'IncludeEndHostsInd': group_dict['IncludeEndHostsInd'],
            'NetBIOSScanningInd': group_dict['NetBIOSScanningInd'],
            'ParentDeviceGroupID': parent_group_id,
            'PerfEnvPollingInd': group_dict['PerfEnvPollingInd'],
            'PolFreqModifier': group_dict['PolFreqModifier'],
            'PortControlBlackoutDuration': group_dict['PortControlBlackoutDuration'],
            'PortScanning': group_dict['PortScanning'],
            'PrivilegedPollingInd': group_dict['PrivilegedPollingInd'],
            'Rank': group_dict['Rank'],
            'SAMLicensedInd': group_dict['SAMLicensedInd'],
            'SNMPAnalysis': group_dict['SNMPAnalysis'],
            'SNMPPolling': group_dict['SNMPPolling'],
            'SPMCollectionInd': group_dict['SPMCollectionInd'],
            'StandardsCompliance': group_dict['StandardsCompliance'],
            'StartBlackoutSchedule': group_dict['StartBlackoutSchedule'],
            'StartPortControlBlackoutSchedule': group_dict['StartPortControlBlackoutSchedule'],
            'UseGlobalPolFreq': group_dict['UseGlobalPolFreq'],
            'VendorDefaultCollection': group_dict['VendorDefaultCollection'],
        })
    except requests.exceptions.HTTPError as e:
        print(e.response.text)


def create_group(group):
    print(
        f'Processing group {group.GroupName} with group id {group.GroupID}.  '
        f'Parent group id is {group.ParentDeviceGroupID}'
    )
    if group.ParentDeviceGroupID == 0 \
            or (group.ParentDeviceGroupID in created_groups and group.GroupID not in created_groups):
        print(f'Group {group.GroupName} is ready to be created.')
        parent_group_id = group.ParentDeviceGroupID
        if group.ParentDeviceGroupID != 0:
            parent_group = list(filter(lambda pgroup: pgroup.GroupID == group.ParentDeviceGroupID, group_list))[0]
            parent_group_id = fetch_new_parent_id(parent_group)
        group_dict = vars(group)
        del group_dict['broker']
        create_group_on_dst(group_dict, parent_group_id)
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
