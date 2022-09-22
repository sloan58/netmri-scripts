# BEGIN-SCRIPT-BLOCK
#
# Script-Filter:
#     $ipaddress == <OC_IP>
#
# Script-Timeout: 600
# END-SCRIPT-BLOCK

from infoblox_netmri.easy import NetMRIEasy

defaults = {
    "api_url": api_url,
    "http_username": http_username,
    "http_password": http_password,
    "job_id": job_id,
    "device_id": device_id,
    "batch_id": batch_id
}

oc_commands = [
    'show disk',
    'show io',
    'show memory',
    'show virtual'
]

collectors = ["1", "2", "3", "4", "5", "6"]

collector_commands = [
    f'show collectors {collector} {command.split(" ")[1]}' for collector in collectors for command in oc_commands
]

command_list = oc_commands + collector_commands

with NetMRIEasy(**defaults) as easy:

    logger = easy.broker('Job')

    log_meta = {
        'id': easy.batch_id,
        'jobdetailid': easy.job_id,
        'severity': 'INFO'
    }

    for command in command_list:
        logger.log_custom_message(
            **log_meta,
            message=f'######## Begin {command} ########\n'
        )
        output = easy.send_command(command)
        logger.log_custom_message(**log_meta, message=output)

        logger.log_custom_message(
            **log_meta,
            message=f'\n######## End {command} ########\n'
        )

