USERNAME = "yuliasavkinainberlin@gmail.com"
PASSWORD = "Konst070589"
LOCATION = 'de/fkb'

PUBLIC_NIC_NAME = 'Public NIC'
PRIVATE_NIC_NAME = 'Private NIC'
UBUNTU_IMAGE_NAME = 'Ubuntu'
FRONTEND_NAME = 'Frontend'
BACKEND_NAME = 'Backend'
DATACENTER_NAME = 'Data center for Test'

DEFAULT_RAM_VALUE = 2048
DEFAULT_CORES_VALUES = 2

UPDATED_RAM_VALUE = 4096
UPDATED_CORES_VALUES = 4

FRONTEND_IS_UP_TIMEOUT_SECONDS = 60 * 30  # 30 minutes

PUBLIC_KEY_LOCAL_FILEPATH = './ssh/id_rsa.pub'
PRIVATE_KEY_LOCAL_FILEPATH = './ssh/id_rsa'

PUBLIC_KEY_REMOTE_FILEPATH = '/root/.ssh/id_rsa.pub'
PRIVATE_KEY_REMOTE_FILEPATH = '/root/.ssh/id_rsa'

TEST_FILE_NAME = 'test.txt'
SCP_COMMAND_TEMPLATE = "scp -o StrictHostKeyChecking=no " \
                           "-o UserKnownHostsFile=/dev/null {test_file} root@{private_ip}:/root/{test_file}"

SSH_LS = "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@{private_ip} ls"
