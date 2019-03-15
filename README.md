Test assignment for Profitbricks (Ionos). (version for MacOS).

_Disclaimer: Before running the script, please, make sure that you have python3 and virtualenv installed on your machine.)
If you don't, then please install then with the following commands:_

`brew install python3`

`pip3 install virtualenv`

Use bash script 'run.sh' to prepare environment and run the test:
`./run.sh`


Some features of this solution:
- Trial test user is: `yuliasavkinainberlin@gmail.com`
- In order to not to invent bicycle again profitbricks python sdk is used for making API calls.
- Inside folder 'ssh' there are two files ('id_rsa' and 'id_rsa.pub') with private and public ssh keys.
Volumes for both Frontend and Backend will be initialised with that public key.

- Also, these keys will be used to authorise ssh calls from local machine to Frontend server's public IP.
- And those 2 keys will be later copied to the Frontend server in order to communicate with Backend server's 
private IP via ssh.

**Here is the algorithm for transfering file from Frontend to Backend:**
  - Establish ssh connection from local machine to Frontend, using ssh-keys from 'ssh' folder.
  - Create file `test.txt` on Frontned
  - Copy ssh-keys from 'ssh' folder to Frontend via SFTP.
  - Run `chmod 400 id_rsa` command to verify correct access rights for private key (without this step, ssh might not work)
  - Transfer it to Backend using `scp` command. Some additional options is used to prevent command from asking questions.
  - Check that file was successfully transferred to Backend by establish ssh connection from Frontend to Backend 
  and run command `ls`.