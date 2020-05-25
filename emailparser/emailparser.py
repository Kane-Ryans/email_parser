# python core library
import os
import re
import time
import json
import email
import sys
import asyncio
import aiofiles
from _collections import deque
# import 3rd party virustotal library
from virus_total_apis import PublicApi as VirusTotalPublicApi
# local helpers and class definitions
from emailparser.email_body import email_body
from emailparser import helpers
from emailparser import secrets


email_store = []
artifact_queue = deque()


def virustotal_queues():
    """Virustotal API timer queue - only allows 4 requests per minute"""
    print('\n - Starting reputation checks')
    while 0 < len(artifact_queue):
        artifact = artifact_queue.popleft()
        name = artifact.filename if isinstance(artifact, email_body.EmailFile.Attachment) else artifact.url
        print(f"  - checking {name}")
        call_virustotal(artifact)
        time.sleep(25) if len(artifact_queue) > 4 else ''


# Read Functions
def read_stdin():
    # read from stdin as binary
    stdin_binary = sys.stdin.detach()
    email_in = stdin_binary.read()
    msg_in = email.message_from_bytes(email_in)
    assert isinstance(msg_in, email.message.Message)
    return msg_in


def requirement_check(file_name: str) -> bool:
    acceptable_file_extensions = re.compile(r'(\.msg|\.eml)$')
    result = re.search(acceptable_file_extensions, file_name) and os.path.getsize(file_name) < 26214400
    return result


async def process_file_async(file_path):
    file_name = os.path.basename(file_path)
    if requirement_check(file_path):
        async with aiofiles.open(file_path, mode='rb') as f:
            email_raw = await f.read()
            print(f'PROCESSING: {file_name}')
            msg_in = email.message_from_bytes(email_raw)
            assert isinstance(msg_in, email.message.Message)
            email_instance = email_body.EmailFile(msg=msg_in, eml_filename=file_name)
            [artifact_queue.append(artifact) for artifact in email_instance.artifacts if email_instance.artifacts]
            return email_instance
    else:
        print(f'ERROR: {file_name} does not meet the requirements')


async def read_async(input):
    global email_store
    if os.path.isdir(input):
        for file in os.listdir(input):
            file_path = os.path.join(input, file)
            email_instance = process_file_async(file_path)
            email_store.append(email_instance)
    else:
        email_instance = process_file_async(input)
        email_store.append(email_instance)
    return await asyncio.gather(*email_store)


# Write Functions
def write_stdout(links=None, attachments=None):
    """Serialize list of local class objects for JSON output"""
    json_links = json.dumps([link.__dict__ for link in links])
    json_attachments = json.dumps([attachment.__dict__ for attachment in attachments])
    results = {
        'links': json_links if links else [],
        'attachments': json_attachments if attachments else []
    }
    print(json.dumps(results))


def prepare_results_directory(dir_name: str = None):
    """Create a folder for the results of the emails being parsed,
    defaults to 'email_parser_results' if no output provided
    """
    dir_name = dir_name if dir_name else 'email_parser_results'
    os.chdir('../')
    if os.path.exists(os.getcwd() + f'/{dir_name}'):
        os.chdir(f'./{dir_name}')
    else:
        os.mkdir(f'{dir_name}')
        os.chdir(f'./{dir_name}')


def write_results_folder(emails, write_attachments: bool = False):
    print(f'OUTPUTTING results in {os.getcwd()}')
    for eml in emails:
        folder_name = eml.eml_filename[:-4]
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
            os.chdir(f'./{folder_name}')
        else:
            os.chdir(f'./{folder_name}')

        if write_attachments:
            [artifact.write_attachment() for artifact in eml.artifacts if isinstance(artifact, email_body.EmailFile.Attachment)]
        write_results_file(eml)

        os.chdir('../')
        print(f'    Output completed for {eml.eml_filename}')


def write_results_file(obj):
    links = []
    attachments = []

    for artifact in obj.artifacts:
        if isinstance(artifact, email_body.EmailFile.Link):
            links.append(artifact.__dict__)
        if isinstance(artifact, email_body.EmailFile.Attachment):
            tmp_artifact = artifact.__dict__
            del tmp_artifact['bytes']
            attachments.append(tmp_artifact)

    result_dict = {
        'filename': obj.eml_filename,
        'links': links,
        'attachments': attachments
    }

    with open('analysis_results.json', "w") as f:
        json.dump(result_dict, f, indent=2)


# Virustotal Functions
def call_virustotal(obj):
    vt = VirusTotalPublicApi(secrets.VIRUSTOTAL_API_KEY)
    if isinstance(obj, email_body.EmailFile.Attachment):
        response = vt.get_file_report(obj.hash, timeout=10)
    elif isinstance(obj, email_body.EmailFile.Link):
        response = vt.get_url_report(obj.url, timeout=10)

    if response['response_code'] == 200:
        stats = parse_vt_stats(response)
        obj.vt_stats = stats
    elif response['response_code'] == 204:
        print('Request rate limit exceeded. You are making more requests than allowed.')
    elif response['response_code'] == 400:
        print('Bad request. This can be caused by missing arguments or arguments with wrong values.')
    elif response['response_code'] == 403:
        print('Forbidden. You don\'t have enough privileges to make the request.')
    else:
        print('Problem communicating with Virustotal - please check manually')


def parse_vt_stats(response):
    if 'scans' not in response['results'].keys():
        return {}
    positive_scans = {key: value for key, value in response['results']['scans'].items() if value['detected']}
    return {
        'total_positives': response['results']['positives'],
        'total': response['results']['total'],
        'positive_scan_engines': positive_scans
    }


def virustotal_api_key_check(key: str = None):
    key_found_msg = '\nVirustotal API key found - reputation checks will be conducted automatically\n'
    key_not_found_msg = '\nVirustotal API key not found - no reputation checks will be executed\n'
    if key:
        secrets.VIRUSTOTAL_API_KEY = key
        print(key_found_msg)
    elif secrets.VIRUSTOTAL_API_KEY:
        print(key_found_msg)
    else:
        print(key_not_found_msg)


# Main function
@helpers.cli_args
def main(args):
    virustotal_api_key_check(args.vt_api)
    if args.file:
        email_store = asyncio.run(read_async(args.file))
    if args.stdin:
        # TODO: finish functions for the stdin/out option
        print('This functionality is still under development')
        pass
    if secrets.VIRUSTOTAL_API_KEY:
        virustotal_queues()
    if args.file:
        prepare_results_directory(dir_name=args.out_file)
        write_results_folder(email_store, write_attachments=args.write_attachments)
    print("Email parsing completed. Exiting program.")
    sys.exit()
