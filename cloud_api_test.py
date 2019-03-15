"""
Test Assignment.

Our Cloud API (https://devops.profitbricks.com/api/cloud/v4/) provides the customer service to
create Data Center(s), managing various resources (multiple Server with scalable Cores and
RAM, scalable Storage, various images to choose from, easy Networking as well as User
(Group) management).

Your task is to write a test (using any tools/frameworks of your choice) for our Cloud API (the
latest, not the legacy ones). You can complete the task in a language of your choice (our
preference is Python).

Precondition: For this purpose, please create a free trial user on your own (don’t worry, you will
not be charged!).

Note: Please share your login name with us.

Test should be able to check that it’s possible to do the following using our API:
1. Create the below mentioned Data Center.
Note: Please use an sshKey when creating the storages.
2. Check whether the ‘Frontend’ Server is up and running.
3. Change the Data Center by increasing the Cores/RAM being used.
4. Create a file on the ‘Frontend’ Server and transfer it to the ‘Backend’ Server.

The Data Center to create should consist of:
- At least two Serves (e.g. ‘Frontend’ and ‘Backend’)
- All Servers are connected per private LAN
- Only one Server (e.g. ‘Frontend’) is connected to a public LAN
"""
import logging
import unittest

from profitbricks.client import ProfitBricksService

from constants import DATACENTER_NAME, USERNAME, PASSWORD, LOCATION, PUBLIC_NIC_NAME, PRIVATE_NIC_NAME, BACKEND_NAME, \
    FRONTEND_NAME, DEFAULT_CORES_VALUES, DEFAULT_RAM_VALUE, UPDATED_CORES_VALUES, UPDATED_RAM_VALUE, TEST_FILE_NAME
from utils import describe_datacenter, find_server, find_nic, ssh_to_frontend, get_public_key

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)


class TestIonosCloudAPI(unittest.TestCase):

    def setUp(self):
        self.client = ProfitBricksService(username=USERNAME, password=PASSWORD)
        self.public_key = get_public_key()

    def test_profitbricks(self):
        """ This is the actual test. It will consist from 4 different subtests, which are dependent from each other"""
        self._create_datacenter_subtest()
        self._frontend_is_up_and_running_subtest()
        self._update_data_center_subtest()
        self._file_creation_and_transfer_via_ssh_subtest()

    def _create_datacenter_subtest(self):
        """ Creates datacenter with specified paramters and checks it's state, location and name"""
        logging.info("Start datacenter creation")
        # create datacenter
        datacenter = describe_datacenter(self.client)
        response = self.client.create_datacenter(datacenter)
        # Wait for the data center and nested resources to finish provisioning
        self.client.wait_for_completion(response)
        self.datacenter_id = response['id']
        logging.info("Datacenter creation finished")

        # Set the first LAN in datacenter to public
        logging.info("Start Lan update")
        response = self.client.update_lan(datacenter_id=self.datacenter_id, lan_id=1, name='Public LAN', public=True)
        self.client.wait_for_completion(response)
        logging.info("Lan update finished")

        # Check that datacenter was succesfully created
        response = self.client.get_datacenter(datacenter_id=self.datacenter_id)
        self.assertEqual(response['metadata']['state'], 'AVAILABLE', "Datacener's state is wrong")
        self.assertEqual(response['properties']['name'], DATACENTER_NAME, "Datacener's name is wrong")
        self.assertEqual(response['properties']['location'], LOCATION, "Datacener's location is wrong")

    def _frontend_is_up_and_running_subtest(self):
        """ Checks that Frontend server was up and is running after datacenter creation"""
        frontend = find_server(self.client, self.datacenter_id, FRONTEND_NAME)
        self.frontend_id = frontend['id']
        self.assertEqual(frontend['metadata']['state'], 'AVAILABLE', "Frontend's state is wrong")
        self.assertEqual(frontend['properties']['vmState'], 'RUNNING', "Frontend's vmState is wrong")

    def _update_data_center_subtest(self):
        """ Checks that server is running with proper new paramters (ram, cores) after update"""
        frontend = find_server(self.client, self.datacenter_id, FRONTEND_NAME)
        self.assertEqual(frontend['properties']['cores'], DEFAULT_CORES_VALUES, "Frontend's core amount is wrong")
        self.assertEqual(frontend['properties']['ram'], DEFAULT_RAM_VALUE, "Frontend's ram amount is wrong")

        logging.info('Server update started')
        # update server with bigger cores and ram arguments
        response = self.client.update_server(self.datacenter_id,
                                             self.frontend_id,
                                             cores=UPDATED_CORES_VALUES,
                                             ram=UPDATED_RAM_VALUE)
        self.client.wait_for_completion(response)
        logging.info('Server update finished')

        # refresh Frontend server
        frontend = find_server(self.client, self.datacenter_id, FRONTEND_NAME)

        # check that cores and ram updated succesfully
        self.assertEqual(frontend['metadata']['state'], 'AVAILABLE', "Frontend's state is wrong")
        self.assertEqual(frontend['properties']['vmState'], 'RUNNING', "Frontend's vmState is wrong")
        self.assertEqual(frontend['properties']['cores'], UPDATED_CORES_VALUES, "Frontend's core amount is wrong")
        self.assertEqual(frontend['properties']['ram'], UPDATED_RAM_VALUE, "Frontend's ram amount is wrong")

    def _file_creation_and_transfer_via_ssh_subtest(self):
        """ Establishes connection via ssh to Frontend and creates file there. Than transfer this file to Backend via
        scp command. Checks that file was successfully transfered."""
        # get public IP - to connect to it via ssh
        public_nic = find_nic(self.client, self.datacenter_id, self.frontend_id, PUBLIC_NIC_NAME)
        public_nic_ip = public_nic['properties']['ips'][0]

        # get backend's IP - to send file from Frontend here thorough local network.
        backend = find_server(self.client, self.datacenter_id, BACKEND_NAME)
        self.backend_id = backend['id']
        backend_private_nic = find_nic(self.client, self.datacenter_id, self.backend_id, PRIVATE_NIC_NAME)
        private_nic_ip = backend_private_nic['properties']['ips'][0]

        # do ssh stuff
        result = ssh_to_frontend(public_nic_ip, private_nic_ip)
        self.assertIn(TEST_FILE_NAME, result)


if __name__ == '__main__':
    unittest.main()
