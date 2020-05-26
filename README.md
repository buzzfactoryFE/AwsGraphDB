# AWS Infrastructure in Neo4j (AWSUCMDB) and Security Analisys

Generally, using AWS Cloud could not be easy to keep under control your objects like EC2, VPNs, Transit Gateway Attachments, VPC peering, Security Groups and so on;  this unwelcome issue could be amplified when you work with multiple accounts and VPCs spread across all over the world. The mistake is always behind the corner.  
Graph database is a very useful tool to keep relationships under control and identify what should considered as a security breach.  

From this premise I started to work on AWSGraphDB project; it uses:

* Cloud Custodian to collect your AWS Cloud infrastructure objects;
* Python scripts to load data gathered using Custodian into Neo4j database for analisys.
* Neo4j Desktop client to visualize, explore and deep dive into your infrastructure's configuration;

## Logical schema and preview

### Graph database logical flow and relationship

In the picture below you can approach to the DB schema and its internal object's relationships  
![GitHub Logo](/images/dbschema.png)  

### Example - How network topology can looks like  

![GitHub Logo](/images/NetworkTopology.png)  

### Example - Explore your infrastructure looking for mistakes: EC2 instances with port 22 open to any  

![GitHub Logo](/images/EC2With22OpentoAny.png)  

## Getting Started

These instructions will provide you a copy of the project up and running on your local machine for development and testing purposes.

### **Prerequisites**

**Neo4j Desktop** installed on your PC with some basic knowledge on how create a Project and how to write simple queries.  
Software can be downloaded from: [Neo4j Desktop](https://neo4j.com/download/)

**Cloud Custodian** installed and configured for your AWS Environment.  
You can find all the information required from: [Cloud Custodian](https://pypi.org/project/c7n/)

**Python 3.6 (or later)** Enviroment with the following extra modules: ```py2neo``` and ```untangle```  
You can download and install it following official [Python website](https://www.python.org/downloads/windows/)

**c7n-org** is a tool to run Custodian against multiple AWS accounts, Azure subscriptions, or GCP projects in parallel.  
You can download and install it following official [tool website](https://cloudcustodian.io/docs/tools/c7n-org.html)

### **Installation**

#### Cloud Custodian

* Install Cloud Custodian in your environment following [official documentation](https://cloudcustodian.io/docs/quickstart/index.html#install-cloud-custodian)

#### c7n-org

* Install c7n-org tool with 
```
pip install c7n-org
```

### **Configuration and extraction data**

#### c7n-org

* Generate the  _account.yml_ file which contains information about your AWS Organizations ID with  
```
python orgaccounts.py -f accounts.yml
```  
**Note:** script is provided via github [cloud-custodian project](https://github.com/cloud-custodian/cloud-custodian/issues/2420).  
Take a look to sample _account.yml_ contained in the repository

* Extract infrastructure's components with
```
c7n-org run -c accounts.yml -s output_folder -u custodian.yml --region all --dryrun
```
**Note:** We use ```--dryrun``` flag but I kindly suggest to run the command using a ```readall IAM``` credential to avoid mistakes.  
YAML _custodian.yml_ is already included in the repository.

At the end, _output_folder_ will contains several json files which describe your cloud resources.

### **Import data into Neo4j**

Now you are ready to load data into Neo4j.  
* Configure _AWSNEoConfig.json_ with the correct parameters:
  * **AccountsFilepath:** fullpath of your generated_accounts.yml_
  * **custodianFiles:** fullpath of _output_folder_ used in the step before (double escape path under Windows OS)
  * **Url/Username/Password:** connection string of Neo4j database

Here an example:
```
[
    {
      "AccountsFilepath": "yourpath/accounts.yml",
      "custodianFiles": "yourpath/output/",
      "NeoParametes": [
        {
          "Url": "bolt://localhost:7687",
          "Username": "neo4j",
          "Password": "awsucmdb"
        }
      ]
    }
]
```

* Load data into Neo4j using Python scripts provided within the project. To keep the things simple I prefered have dedicated script for each object import.

```
python .\01.NeoLoadsAccounts.py
python .\02.NeoRegionLoader.py
python .\03.NeoLoadVPC.py
python .\04.NeoLoadSubnetAndZones.py
python .\05.NeoLoadTransit.py
python .\06.NeoLoadVpns.py
python .\07.NeoLoadTgwAttachments.py
python .\08.NeoLoadPeering.py
python .\09.NeoLoadSecurityGroup.py
python .\10.NeoLoadEc2.py
```

Verify that everything went fine running neo4j call db.schema.validation and verify that the schema is the same of my picture.

## Running the tests

Enjoy your exploration!! 
My first exploration helped me to identify a lot of misconfiguration and to understand how my colleagues use the infrastructure.
The file [QueryExample](QueryExample.txt) contains some useful Cypher Query.

## Contributing
I am not a good developer so my code is horrible and i didn't get time to write comments into the code, in my mind steps are:

* add RDS data into database
* add Lambda data into database
* comment the code
* improve the code
* try to use AWS Neptune instead of Neo4j

## Authors

* **[BuzzFactory](https://github.com/buzzfactoryFE)**

## License

This project is licensed under the MIT License - see the [LICENSE.md](/LICENSE.md) file for details