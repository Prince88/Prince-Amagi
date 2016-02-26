# Prince-Amagi
Requirements to get started.
 1) Install any version of python2.7 
 2) Install ansible
 3) Install boto package for Python preferably v2.39
 4) Install git
 5) Create an aws account
 6) Create an IAM user for the account and get the aws_access_key_id and aws_secret_access_key, save them in file ~/.boto in the format given below:
  [Credentials]
  aws_access_key_id=<your access key id>
  aws_secret_access_key=<your secret access key>

Boto reads credentials from file ~/.boto in unix platform and from C:\Users\<username>\boto.config in windows platform

Steps to get started:
 1) clone the repo in a directory of your choice in your system.
  git clone https://github.com/Prince88/Prince-Amagi.git - this will create a folder Prince-Amagi in the path you cloned the repo
 2) cd Prince-Amagi
 3) python LaunchEC2instance.py
  This will start creation/launch of an EC2 instance.

once everything goes well http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html
and instance is created, script will print the public dns name of the instance and further would try to setup the server and deploy the app using ansible-playbooks.

Under folder devops, you can find two yml files:
 1) setup_server.yml - It is responsible for setting up the server with all the necessary installations like, git, python, ngnix,  supervisord etc.
 2) deploy.yml - It is responsible for deploying the app by cloning the repo from git, creating virtual env for python and install depencecies in the invornment by reading requirements.txt etc.

If everything goes right, you will see your app hosted on the ec2 instance created earlier.
in case you see something like:
  FAILED! => {"changed": false, "failed": true, "msg": "ERROR (no such process)", "name": "hello_flask"}
  Login into your ec2 instance and run following commands:
   supervisorctl
   supervisor>update
   supervisor>avail
   at this point you will see your app running on the server.
 P.S I am still working on getting these commands together in the yml.
 
 References:
  http://boto.cloudhackers.com/en/latest/
  http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html
  http://docs.ansible.com/ansible/playbooks_intro.html
  http://mattupstate.com/python/devops/2012/08/07/flask-wsgi-application-deployment-with-ubuntu-ansible-nginx-supervisor-and-uwsgi.html


