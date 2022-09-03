# Air-Pressure-Failure-Detection
This is end to end machine learning system for predicting the failure of air pressure components, in critical industrial applications/tools and many more, based on the training data which is given to us. The system is built using Multi Cloud Architecture, where we are using AWS cloud and Azure Cloud for our requirement.

### Overview and Aim of the Project
The overall goal of the project is to build a system which will automatically be able to detect failure of air pressure in certain industrial components, and when failure is
detected the end user should be notified about the end results.

Since we mentioned multi cloud architecture, we are going to use AWS and Azure

The entire solution is built by using cloud services like AWS and Azure, for data storage like AWS S3 buckets, Azure Container Registry for container images.Apart from AWS services and Azure services, MLFlow is used for experiment tracking and model versioning,etc. CI- CD deployment is done using Github Actions which will deploy the container image to Azure Container Instances. Coming to the infrastrucuture provisioning we are using Terraform as IAC tool. FastAPI is used as a webserver for user interaction. From the database point of view, we are using MongoDB for good data storage.


### Data Description


### Setup of the project
In order to setup the project, they are some prerequisites like in terms of installing and setting up our credentials for the cloud services.

Step -`1 Installing terraform in the local machine
Depending the type of system which are using like Windows, Linux and Mac, terraform installation might be different.

## Terraform installation in Windows
Before we run the script for installing the terraform, we need to install Chocolatey

Run this command in powershell with admin access, to install chocolatey

```bash
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

On running this command, chocolatey will be installed in windows system and to check whether the installation is successfull or not, we can run the following command to get chocolatey version. If the version is returned correctly that means chocolatey is installed without any issues.

```bash
choco --version
```
Once the installation of chocolatey is done, we can use that to install terraform in the windows system. Run the command to install terraform

```bash
choco install terraform
```

Once the installation of terraform is done, we get install awscli and configure our AWS creds.

To install awscli in windows system, run the following commands in powershell terminal

```bash
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

To check whether awscli is installed correctly or not, run the following command
```bash
aws --version
```
On successfull execution, we can see that awscli is properly installed and ready to use. 

Now we have to create aws credentials for authentication, 
- Go to AWS IAM console 
- Click on Users button
- Click on Add users
- Select username and select aws credential type to be programmatic access, and click next permissions
- Under the set permissions, click on attach existing policies and select "AdministratorAccess" policy
- Click on next tags and the click on next review
- Click on create user and you shall see that access key id and secret access key and shown to you, keep these credentials safe and secure in one place.
- Next click on close

Once the credentials are generated, configure them using awscli

```bash
aws configure
```
Use default region as us-east-1 and default output format as json

Now that we have created and configured our aws credentials, we can now provision infrastructure from terraform. Before we provision our AWS infrastructure, terraform needs a backend to store the terraform state file in a secure location, like s3 buckets, blob storages, etc. We are using s3 backend for terraform configuration.

Creating CosmosDB MongoDB instance, go to the azure console, 

- Click on create a resource and click on the Azure Cosmos DB link
- Select the Azure Cosmos DB API for MongoDB
- Create a new resource group with any name of your choice
- Create a account name with any name of your choice
- Click on global distribution, click next on networking, click on next encryption, click on next tags, and finally click on review and create.
- Click on create, after validation, deployment for the resources will start and after sometime azure cosmos db api will be avaiable for testing and usage.

Once the deployment is done, go to resource group and under setting click on connection string, copy the primary connection string and save it somewhere safe. To test whether the connection string is working, go to MongoDB compass and paste the connection string and click on connect. You shall see that the connection string, we will used to connect to Azure Cosmos MongoDB API.

Make sure that you have cloned the repo from github, commands to do so are

```bash
git clone https://github.com/sethusaim/Air-Pressure-Failure-Detection.git
```

Once the repo is cloned to local system, go to the infrastructure folder and open vscode in it. Once vscode is open with infrastructure folder, we have to make some changes in module.tf file

Once all these neccesssary changes are done, make sure to create s3 bucket with (yourname-air-pressure-tf-state) from the console,
- Go to the S3 management console, and click on create bucket 
- select bucket name as (yourname-air-pressure-tf-state).
- on scrollling down we shall see that bucket versioning option, is set to disabled. Do enable it.
- Click on create bucket
- Change the bucket name to bucket name which was previously created (yourname-air-pressure-tf-state)
- Make similar changes in bucket name in variables.tf files of respective bucket folder
- Make sure to change the account id also


At first we shall provision the s3 buckets, in order to do so comment all the modules in module.tf except s3 bucket modules and then run 

```bash
terraform init
```

This command will initialize the terraform modules, and to provision the s3 buckets, run the following commands
```bash
terraform apply --auto-approve
```

After few seconds the s3 buckets will be provisioned in AWS cloud. Now that s3 buckets are created, we shall provision ansible instance and mlflow instance. First we shall setup the ansible instance and configure ansible data to deploy our softwares.

Before launching the instance, in ansible instance folder, locate the ansible.tf file and change the location of pem file, from connection private key to your pem file location.

To setup the ansible instance, uncomment ansible instance module from module.tf file and then run the following commands

```bash
terraform init
```

```bash
terraform apply --auto-approve
```

On successful execution of the module, we shall see that ec2 instance is running with ansible server tag. Now that server is running, connect via ssh and configure your aws creds and ansible hosts to make ansible setup mlflow in other ec2 instance

First, let us configure aws credentials to ansible server, run the following command and put your aws creds

```bash
aws configure
```

You shall notice that infrastructure, playbooks and vars folder are already present in ec2 instance, it is because we have run post launch script from terraform to do important installations before hand.

Now provision the mlflow instance, in order to do so uncomment the mlflow instance module from the module.tf file and run the following commands

```bash
terraform init
```

```bash
terraform apply --auto-approve
```



But the ansible server does not have the pem file, to make ssh connection. So there are different ways in which the pem file can be transferred to ansible server, one is via filezilla way

other way is by manually copy the contents of pem file from local and the pasting it the file and saving it.

Either way works fine, but once the pem file is avaiable in ansible server, make sure to change the permissions for pem file by running the commands.

```bash
sudo chmod 400 sethusaim.pem
```

On successful execution, we shall see an ec2 instance is running with tag name as a mlflow server. Once it reaches the running state, grab the private ip of the instance and keep it safe in one place.

Now in the terminal ssh connection, run the following commands,

```bash
sudo nano /etc/ansible/hosts
```

In the project directory, go to others folder and locate the ansible_hosts.txt file, and make the following changes in the file, in place of MLFLOW_PRIVATE_IP put the mlflow server private ip, and in place of YOUR_PEM_FILE replace it with yourpemfile name, used to launch the instance.

Copy the contents of the file and then paste the /etc/ansible/hosts file and save the file

Now that the ansible hosts are configured, we have to make changes in the mlflow nginx config file and mlflow0-tracking.service file. In the others folder, locate the mlflow file and make changes accordingly and copy them the ansible server using filezilla or any other method of your choice.

Once that is done, in the ansible server run the following commands

```bash
sudo nano vars/variables.yml
```
Change the env_name to mlflow, username - sethusaim (example only), password - sethusai (example only) and save the file.

Now that aws creds, ansible hosts, variables are all configured, we can run the playbook, to setup mlflow in ec2 instance, run the following commands

```bash
sudo ansible-playbook playbooks/mlflow.yml
```

These steps will take some time to run and setup mlflow in the ec2 instance. Once the mlflow playbook run successfully, to the ec2 console, and grab the mlflow public ip and paste it the browser with port 8080, you shall prompted to give username and password, do remember it is same which we have in variables.yml file


Now grab these mlflow creds as env variables

MLFLOW_TRACKING_URI - http://MLFLOW_PUBLIC_IP:8080

MLFLOW_TRACKING_USERNAME - sethusaim ( example only )

MLFLOW_TRACKING_PASSWORD - sethusai ( example only )

MONGODB_URL - the connection string from azure cosmos db

Secure these important details in a file or something. Once that is done, we shall store all our credentials in github secrets. Important details like AWS_SECRET_ACCESS_KEY,AWS_DEFAULT_REGIONMLFLOW_TRACKING_URI,MONGODB_URL,MLFLOW_TRACKING_USERNAME,MLFLOW_TRACKING_PASSWORD, etc. 

Now coming to azure part for the deployment, we have to install azurecli locally. In order to do so use link below to download azurecli and complete the installation steps.

```bash
https://aka.ms/installazurecliwindows

```
On successful installation of azure cli, go to the terminal and run the command
```bash
az login
```

You will be redirected to login page in the browser,authorize the login and proceeed. Once the authentication is done. Go to the azure console and create a resource group with 
pressure as the name. Now we need to create credentials for github actions to connect to azure and deploy our application docker image. In order to do so run the following commands from the powershell terminal

groupId=$(az group show --name pressure --query id --output tsv)

az ad sp create-for-rbac --scope $groupId --role Contributor --sdk-auth

On running the second commands, we will output similar to this 

```bash
{
  "clientId": "xxxx6ddc-xxxx-xxxx-xxx-ef78a99dxxxx",
  "clientSecret": "xxxx79dc-xxxx-xxxx-xxxx-aaaaaec5xxxx",
  "subscriptionId": "xxxx251c-xxxx-xxxx-xxxx-bf99a306xxxx",
  "tenantId": "xxxx88bf-xxxx-xxxx-xxxx-2d7cd011xxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```
Grab this json data, and secure it a file.

Now go to pressure resource group, and create a container registry and any proper name, and then click on create. Once the deployment is done go to the resource group and grab the login server and save it in github secrets as REGISTRY_LOGIN_SERVER. 
If we see the github actions workflows, there are two still two more azure creds needed, these are REGISTRY_USERNAME and REGISTRY_PASSWORD. These are nothing but clientId and clientSecret from the generated json data.

In github actions, store extra secrets in the name 

REGISTRY_LOGIN_SERVER - avaiable from container registry resource

REGISTRY_USERNAME - clientId from the json data while running "az ad sp create-for-rbac --scope $groupId --role Contributor --sdk-auth" command

REGISTRY_PASSWORD- clientSecret from the json data while runinig "az ad sp create-for-rbac --scope $groupId --role Contributor --sdk-auth" command

AZURE_CREDENTIALS - the entire jsond data returned while runinig "az ad sp create-for-rbac --scope $groupId --role Contributor --sdk-auth" command

This is all for setting up the project.


### Running the project 

### Outcomes