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


def create_group_on_dst(group):
    try:
        res = group_broker_dst.create(**{
            'ARPCacheRefreshInd': group.ARPCacheRefreshInd,
            'AdvancedGroupInd': group.AdvancedGroupInd,
            'BlackoutDuration': group.BlackoutDuration,
            'CCSCollection': group.CCSCollection,
            'CLIPolling': group.CLIPolling,
            'ConfigLocked': group.ConfigLocked,
            'ConfigPolling': group.ConfigPolling,
            'CredentialGroupID': group.CredentialGroupID,
            'Criteria': group.Criteria,
            'FingerPrint': group.FingerPrint,
            'GroupName': group.GroupName,
            'IncludeEndHostsInd': group.IncludeEndHostsInd,
            'NetBIOSScanningInd': group.NetBIOSScanningInd,
            'ParentDeviceGroupID': group.ParentDeviceGroupID,
            'PerfEnvPollingInd': group.PerfEnvPollingInd,
            'PolFreqModifier': group.PolFreqModifier,
            'PortControlBlackoutDuration': group.PortControlBlackoutDuration,
            'PortScanning': group.PortScanning,
            'PrivilegedPollingInd': group.PrivilegedPollingInd,
            'Rank': group.Rank,
            'SAMLicensedInd': group.SAMLicensedInd,
            'SNMPAnalysis': group.SNMPAnalysis,
            'SNMPPolling': group.SNMPPolling,
            'SPMCollectionInd': group.SPMCollectionInd,
            'StandardsCompliance': group.StandardsCompliance,
            'StartBlackoutSchedule': group.StartBlackoutSchedule,
            'StartPortControlBlackoutSchedule': group.StartPortControlBlackoutSchedule,
            'UseGlobalPolFreq': group.UseGlobalPolFreq,
            'VendorDefaultCollection': group.VendorDefaultCollection,
        })
        return res['id']
    except requests.exceptions.HTTPError as e:
        print(e.response.text)


def get_children(group):
    children = list(filter(lambda cgroup: cgroup.ParentDeviceGroupID == group.GroupID, group_list))
    group.Children = children
    if len(children):
        for child in children:
            get_children(child)
    return group


def create_new_group(group):
    new_parent_id = create_group_on_dst(group)
    if len(group.Children):
        for child in group.Children:
            child.ParentDeviceGroupID = new_parent_id
            create_new_group(child)


group_list = []
for group in group_broker_src.index():
    if not group.SystemGroupInd:
        group_list.append(group)


group_tree = []
for group in group_list:
    if not group.SystemGroupInd and group.ParentDeviceGroupID == 0:
        group_tree.append(get_children(group))

for group in group_tree:
    create_new_group(group)
