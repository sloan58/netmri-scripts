import sys

import requests
from infoblox_netmri.client import InfobloxNetMRI

save_local_copy = False

try:
    # Source NetMRI System
    net_mri_client_src = InfobloxNetMRI(host="",
                                        username="",
                                        password="",
                                        use_ssl=False)

    # Destination NetMRI System
    net_mri_client_dst = InfobloxNetMRI(host="",
                                        username="",
                                        password="",
                                        use_ssl=False)
except requests.exceptions.ConnectionError as e:
    print(e)
    sys.exit()


def get_script_export(script):
    try:
        response = net_mri_client_src.api_request('scripts/export_file', {
            'id': script['id']
        }, downloadable=True)
        print(f"({script['id']}) {script['name']}: Content downloaded")

        extension = get_script_language_ext(script['language'])
        print(f"({script['id']}) {script['name']}: Set extension '{extension}'")

        if save_local_copy:
            save_script_backup(f"{script['name']}.{extension}", response['content'])

        return response['content']

    except requests.exceptions.HTTPError as e:
        print(f"{script['id']}: Error deleting script")
        print(e.response.text)
        # sys.exit()


def save_script_backup(script_name, script_content):
    print(f"({script['id']}) {script['name']}: Creating local backup of script'")
    with open(f"./script_backups/{script_name}", 'w') as f:
        f.write(script_content)
    print(f"({script['id']}) {script['name']}: Wrote to disk")


def get_script_language_ext(language):
    if language == 'Python':
        return 'py'
    elif language == 'Perl':
        return 'pl'
    else:
        return 'ccs'


def delete_script(script_id):
    try:
        net_mri_client_src.api_request('scripts/destroy', {
            'id': script_id
        })
        print(f"{script['id']}: Deleted")
    except requests.exceptions.HTTPError as e:
        print(f"{script['id']}: Error deleting script")
        print(e.response.text)
        # sys.exit()


try:
    response = net_mri_client_src.api_request('scripts/index', {})
except requests.exceptions.HTTPError as e:
    sys.exit()

for script in response['scripts']:
    print(f"({script['id']}) {script['name']}: Processing")

    script_content = get_script_export(script)

    try:
        print(f"({script['id']}) {script['name']}: Attempting scripts/create on destination")
        try:
            response = net_mri_client_src.api_request('scripts/create', {
                'script_file': script_content,
                'language': script['language'],
            })
            print(f"({script['id']}) {script['name']}: Script added to destination")
        except requests.exceptions.HTTPError as e:
            print(f"({script['id']}) {script['name']}: Error adding script.")
            print(e.response.text)
            sys.exit()

        print(f"({script['id']}) {script['name']}: Done")
    except requests.exceptions.HTTPError as e:
        sys.exit()
