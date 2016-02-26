# Prince-Amagi
##Requirements to get started.
  1. Install any version of python2.7 . 
  2. Install ansible.
  3. Install boto package for Python preferably v2.39 .
  4. Install git .
  5. Create an aws account .
  6. Create an IAM user for the account and get the aws_access_key_id and aws_secret_access_key, save them in file ~/.boto in the format given below:
    ```
    [Credentials]
    aws_access_key_id=<your access key id>
    aws_secret_access_key=<your secret access key>
    
    ```
Boto reads credentials from file ~/.boto in unix platform and from C:\Users\<username>\boto.config in windows platform

##Steps to get started:
 1. clone the repo in a directory of your choice in your system.
  `git clone https://github.com/Prince88/Prince-Amagi.git` - this will create a folder Prince-Amagi in the path you cloned the repo
 2. cd Prince-Amagi
 3. python LaunchEC2instance.py
 This will start creation/launch of an EC2 instance.

once everything goes well and instance is created, script will print the public dns name of the instance and further would try to setup the server and deploy the app using ansible-playbooks.

#Under folder devops, you can find two yml files:
 1. setup_server.yml - It is responsible for setting up the server with all the necessary installations like, git, python, ngnix,  supervisord etc.
 2. deploy.yml - It is responsible for deploying the app by cloning the repo from git, creating virtual env for python and install depencecies in the invornment by reading requirements.txt etc.

If everything goes right, you will see your app hosted on the ec2 instance created earlier.
in case you see something like:
  ```
  FAILED! => {"changed": false, "failed": true, "msg": "ERROR (no such process)", "name": "hello_flask"}
  Login into your ec2 instance and run following commands:
  supervisorctl
  supervisor>update
  supervisor>avail
  
  ```
  At this point you will see your app running on the server.

##Code Explained:

1. Function `def _runLocalCommand(cmd)`
This function runs any command locally and waits for the command to complete, returns a tuple carrying output and exit code for the command

2. Function `def _check_key_name_exists(_conn,key_name)`
This function looks for the key, if its already created then it expects it to be saved on the machine under directory `~/.ssh`, other wise if the key is not present, then it creates the key and saves it under the mentioned folder.

3. Function `def _check_security_group_exists(_conn, group_name)`
This function looks for the security group, assigns inbound rules for allowing only ssh,http and https traffic if security group is already present. otherwise creates the security group and does the same job.

4. Function `def create_instance(ami='ami-9abea4fb')`
This function creates and launches an t2.micro instances of ubuntu(ami-9abea4fb) image under oregon region, prints the public dns name of the recently created instance. To create instance under any other region, you need to modify function. Also, the function expects that IAM user has a default VPC available, otherwise it will fail.

5. Function `def server_setup_deploy()`
This function updates the hosts file under devops folder with the public dns name of the newly created instance, further it uses anisble-playbook to execute commands based on the file setup_server.yml and setups the server with initial requirements. It also reads deploy.yml under devops folder and deploys the flask app on the server using supervisorctl module.


##References:
 1. http://boto.cloudhackers.com/en/latest/
 2. http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html
 3. http://docs.ansible.com/ansible/playbooks_intro.html
 4. http://mattupstate.com/python/devops/2012/08/07/flask-wsgi-application-deployment-with-ubuntu-ansible-nginx-supervisor-and-uwsgi.html


