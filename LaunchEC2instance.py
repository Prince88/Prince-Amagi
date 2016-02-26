# !/usr/bin/python

import boto, boto.ec2
import time
import os
from subprocess import PIPE,Popen

ec2region='us-west-2'
ec2key_name='prince-key-pair-uswest2'
ec2security_groups=['Prince-Amagi']
ec2instance_type='t2.micro'
key_dir='~/.ssh'

def _runLocalCommand(cmd):

	"""
	Runs command locally and returns tuple of command exit code and output
	"""

	proc = Popen(cmd,stdout=PIPE,shell=True)
	output = proc.communicate()[0]
	status = proc.returncode
	return (output,status)
	

def _check_key_name_exists(_conn,key_name):

	"""
	Checks if key_name exists, if not then creates the key and save it
	"""
	
	global key_dir
	# Check to see if specified keypair already exists.
    	# If we get an InvalidKeyPair.NotFound error back from EC2,
    	# it means that it doesn't exist and we need to create it.
    	try:
		print "Looking for key-pair : %s " % key_name
        	key = _conn.get_all_key_pairs(keynames=[key_name])[0]
		if key:
			print "Found Key - Expect the key is saved under ~/.ssh folder for seamless ssh access!"
    	except _conn.ResponseError, e:
        	if e.code == 'InvalidKeyPair.NotFound':
            		print 'Key Not Found...!\nCreating keypair: %s' % key_name
            		# Create an SSH key to use when logging into instances.
            		key = _conn.create_key_pair(key_name)
            		if key:
				print "Successfully created key-pair : %s \nAttempting to save the key in : %s " % (key_name,key_dir)
            		# AWS will store the public key but the private key is
            		# generated and returned and needs to be stored locally.
            		# The save method will also chmod the file to protect
            		# your private key.
			# because of the security architecture of Amazon EC2: you can only retrieve a complete key pair 
			# (i.e. including the private key) during the initial creation of a key pair, 
			# the private key is never stored by EC2 and cannot be recovered.
			try:
				os.remove(key_dir + os.sep + key_name + '.pem') #Failover incase key.pem already exists in ssh dir with same name 
			except:
				pass
            		key.save(key_dir)
			print "Successfully saved key-pair"
		else:
			raise
		

def _check_security_group_exists(_conn,group_name):

	# Check to see if specified security group already exists.
	# If we get an InvalidGroup.NotFound error back from EC2,
	# it means that it doesn't exist and we need to create it.
	
	# Local varibale to authorize security group inbound rules
	ssh_port = 22
	cidr = '0.0.0.0/0'
	http_port = 80
	https_port = 443
	try:
		print "Looking for security group : %s " % group_name
		group = _conn.get_all_security_groups(groupnames=[group_name])[0]
		print "%s security group exists" % group_name
	except _conn.ResponseError, e:
		if e.code == 'InvalidGroup.NotFound':
			print 'Not Found...! \nCreating Security Group: %s' % group_name
			# Create a security group to control access to instance via SSH.
			group = _conn.create_security_group(group_name,
                                              'A group that allows SSH,HTTP,HTTPS allows')
			print "Successfully created security group!"
		else:
			raise

	# Add a rule to the security group to authorize SSH,HTTP,HTTPS traffic
	# on the specified port.
	try:
		print "Authorizing SSH inbound traffic"
		group.authorize('tcp', ssh_port, ssh_port, cidr) #Allowing inbound traffic for 0.0.0.0/0 could be dangerous
		print "Successfull...!"
		print "Authorizing HTTP inbound traffic"
		group.authorize('tcp', http_port, http_port, cidr)
		print "Successfull...!"
		print "Authorizing HTTPS inbound traffic"
		group.authorize('tcp', https_port, https_port, cidr)
		print "Successfull...!"
	except _conn.ResponseError, e:
		if e.code == 'InvalidPermission.Duplicate':
			print 'Security Group: %s already authorized' % group_name
		try:
			print "Authorizing HTTP inbound traffic"
			group.authorize('tcp', http_port, http_port, cidr)
		except _conn.ResponseError, e:
			if e.code == 'InvalidPermission.Duplicate':
				print 'Security Group: %s already authorized' % group_name
			else:
				raise
		try:
			print "Authorizing HTTPS inbound traffic"
			group.authorize('tcp', https_port, https_port, cidr)
		except _conn.ResponseError, e:
			if e.code == 'InvalidPermission.Duplicate':
				print 'Security Group: %s already authorized' % group_name
			else:
				raise
		else:
			raise

def create_instance(ami='ami-9abea4fb'):

	"""
	Creates EC2 instance and returns the public dns name
	"""

	global ec2region,ec2key_name,ec2security_groups,ec2instance_type
	print "Starting creation....!"
	try:
		#connect to region where you want to host the instance
		conn = boto.ec2.connect_to_region(ec2region)
		#check for key-pair
		_check_key_name_exists(conn,ec2key_name)
		#cehck for security group
		_check_security_group_exists(conn,ec2security_groups[0])
		reservation = conn.run_instances(ami,key_name=ec2key_name,instance_type=ec2instance_type,security_groups=ec2security_groups)
		instance = reservation.instances[0]
		while instance.update() == 'pending':
			print "Instance status is %s " % instance.update()
			time.sleep(10) 	
			if instance.update() == 'running':
				break

		print "\nInstance is up and running and can be reached @ %s \n\n " % instance.public_dns_name
		return instance.public_dns_name
	except Exception as e:
		raise Exception("Instance Creation Failed For - %s " %str(e))

	

def server_setup_deploy():
	
	"""
	Prepares setup based on setup_server.yml
	"""
	global key_dir,ec2key_name	
	try:
		#create hosts file 
		val = _runLocalCommand('echo "[webservers]" > devops/hosts')
		if val[1]:
			raise Exception("Failed to create hosts file : %s " %val[0])
		hostname = create_instance()
		#Sleep for sometime be it 120 secs, time for status check to be successfull
		#TBD - Need a better way to check the reachability of ec2 instance
		print "\n\nNEXT: Waiting for SSHD service on the server to be active\n\n"
		time.sleep(120)
		#add hostname of the instance created in hosts file, we will use this hosts file to configure server
		val = _runLocalCommand('echo %s >> devops/hosts' % hostname)
		if val[1]:
			raise Exception("Failed to add instance hostname into hosts file : %s " %val[0])
		print "\n\nNEXT: Running Commands to install necessary modules on server -- It will take some time!\n\n"
		val = _runLocalCommand("ansible-playbook devops/setup_server.yml -i devops/hosts --private-key=%s " % (key_dir+os.sep+ec2key_name+'.pem'))
		if val[1]:
			raise Exception("Failed to setup_server : %s " % val[0])
		else:
			print val[0]
			print "\n\nDone with Setting up Server\n\n"
		print "\n\nNEXT: Deploying App -- Will take some time\n\n"
		val = _runLocalCommand("ansible-playbook devops/deploy.yml -i devops/hosts --private-key=%s " % (key_dir+os.sep+ec2key_name+'.pem'))
		if val[1]:
			raise Exception("Failed to deploy App : %s " % val[0])
		else:
			print val[0]
			print "\n\nApp Deployment Successfull\n\n"
	except:
		raise

if __name__ == '__main__':
	server_setup_deploy()
