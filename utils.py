import time
from time import sleep

import paramiko

from paramiko import AutoAddPolicy
from profitbricks.client import NIC, Volume, Server, Datacenter

from constants import DATACENTER_NAME, PUBLIC_NIC_NAME, PRIVATE_NIC_NAME, UBUNTU_IMAGE_NAME, LOCATION, BACKEND_NAME, \
    FRONTEND_NAME, DEFAULT_RAM_VALUE, DEFAULT_CORES_VALUES, FRONTEND_IS_UP_TIMEOUT_SECONDS, PUBLIC_KEY_LOCAL_FILEPATH, \
    PRIVATE_KEY_LOCAL_FILEPATH, PRIVATE_KEY_REMOTE_FILEPATH, PUBLIC_KEY_REMOTE_FILEPATH, \
    TEST_FILE_NAME, SCP_COMMAND_TEMPLATE, SSH_LS


def find_images(client, name, location):
    """ Find image by partial name and location """
    images = []
    for item in client.list_images()['items']:
        if (item['properties']['location'] == location and
                item['properties']['imageType'] == 'HDD' and
                name.lower() in item['properties']['name'].lower()):
            images.append(item)
    return images


def find_nic(client, datacenter_id, server_id, name):
    """ Finds NIC among datacenter's server's NICS by nic name"""
    for item in client.list_nics(datacenter_id=datacenter_id, server_id=server_id)['items']:
        if item['properties']['name'] == name:
            return item


def find_server(client, datacenter_id, name):
    """ Finds server among datacenter's servers by name"""
    for item in client.list_servers(datacenter_id=datacenter_id)['items']:
        if item['properties']['name'] == name:
            return item


def describe_datacenter(client):
    """ Creates a detailed description of the Datacenter according to the requirements"""
    # Define a public NIC
    public_nic = NIC(name=PUBLIC_NIC_NAME, dhcp=True, lan=1, nat=False)

    # Define a private NIC
    private_nic = NIC(name=PRIVATE_NIC_NAME, dhcp=True, lan=2)

    # get existing image with specific name
    images = find_images(client=client, name=UBUNTU_IMAGE_NAME, location=LOCATION)
    if images:
        ubuntu_image = images[0]
    else:
        raise Exception("There are no existing Ubuntu images")

    # Define a volume for backend
    backend_volume = Volume(
        name='Backend Volume',
        size=20,
        image=ubuntu_image['id'],
        image_password='123123123',
        ssh_keys=[get_public_key()],
        availability_zone='ZONE_3')

    # Define volume for frontend
    frontend_volume = Volume(
        name='Data Volume 1',
        size=20,
        image=ubuntu_image['id'],
        image_password='123123123',
        ssh_keys=[get_public_key()],
        availability_zone='ZONE_3')

    # Define a server with associated NICs and volumes
    backend_server = Server(
        name=BACKEND_NAME,
        ram=DEFAULT_RAM_VALUE,
        cores=DEFAULT_CORES_VALUES,
        cpu_family='INTEL_XEON',
        nics=[private_nic],
        create_volumes=[backend_volume])

    # Define a server with associated NICs and volumes
    frontend_server = Server(
        name=FRONTEND_NAME,
        ram=DEFAULT_RAM_VALUE,
        cores=DEFAULT_CORES_VALUES,
        cpu_family='INTEL_XEON',
        nics=[public_nic, private_nic],
        create_volumes=[frontend_volume])

    # Define a data center with the server
    datacenter = Datacenter(
        name=DATACENTER_NAME,
        description="Yulia's test assignment datacenter",
        location=LOCATION,
        servers=[frontend_server, backend_server])

    return datacenter


def wait_until_server_is_up_for_ssh_call(ssh_client, ip, username='root'):
    """ Waits for 30 minutes and check once in 60 seconds readiness of the host. Raises exception if server is still
    unavailable after 30 minutes"""
    start_time = time.time()
    while time.time() - start_time < FRONTEND_IS_UP_TIMEOUT_SECONDS:
        try:
            return ssh_client.connect(hostname=ip, username=username, timeout=60)
        except OSError as e:
            pass

    raise Exception("Remote host is off longer than {} seconds.".format(FRONTEND_IS_UP_TIMEOUT_SECONDS))


def ssh_to_frontend(public_ip, private_ip):
    """ 1. Connect to publicly available host in datacenter via SSH
        2. Transfer ssh-keys files to this host (will be used to transfer file to Backend - since backend was created
        with exactly this SSH-key assigned).
        3. Apply strict owning rules to private key - otherwise ssh won't work
        4. Create test file with simple 'Test message' text inside.
        5. Transfer this file to Backend server via private lan using scp command.
        6. Save result of the 'ls' command - in order to check whether file actually transferred to Backend."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    # Although status of Frontend is Available and running - it's impossible to connect to the server during first 10-15
    # minutes after it's creation. We have to wait until is finally up.
    wait_until_server_is_up_for_ssh_call(client, public_ip)

    # transfer ssh-keys to Frontend
    sftp = client.open_sftp()
    sftp.put(PRIVATE_KEY_LOCAL_FILEPATH, PRIVATE_KEY_REMOTE_FILEPATH)
    sftp.put(PUBLIC_KEY_LOCAL_FILEPATH, PUBLIC_KEY_REMOTE_FILEPATH)
    sftp.close()

    # set correct mask for private key
    client.exec_command('chmod 400 {}'.format(PRIVATE_KEY_REMOTE_FILEPATH))
    # create test file
    client.exec_command("echo 'Test message' > {}".format(TEST_FILE_NAME))
    # transfer it to Backend
    client.exec_command(SCP_COMMAND_TEMPLATE.format(test_file=TEST_FILE_NAME, private_ip=private_ip))

    # run 'ls' command on Backend through ssh
    _, stdout, _ = client.exec_command(SSH_LS.format(private_ip=private_ip))
    ls_result = stdout.read().decode('utf-8')
    client.close()
    return ls_result


def get_public_key():
    """ Reads public key value from the file"""
    with open(PUBLIC_KEY_LOCAL_FILEPATH, encoding='utf-8') as key_file:
        return key_file.read()
