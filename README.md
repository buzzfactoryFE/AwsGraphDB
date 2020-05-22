# AWS Objects in Neo4j

In the AWS Cloud often is not easy keep under control your objects like EC2, VPNs, Transiti Gateway Attachments, vpc peering, security groups and so on, especially
when you are working with multiple accounts and vpcs spread across all over the world. the mistake is always behind the corner.
Graph databases are the best tool to use to keep relationships under control and identify relationships that shouldn' exist and can compromize your security.
This project uses Neo4j Desktop , Cloud Custodian and pyhton scripts to load data gathered using Custodian into Neo4j database for analisys.
In the picture below DB schema
![GitHub Logo](/images/dbschema.png)
here an example on how network topology can looks like
![GitHub Logo](/images/NetworkTopology.png)
here an example on explore your date looking for mistakes: EC2 instances with port 22 open to any
![GitHub Logo](/images/EC2With22OpentoAny.png)


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

**Neo4j Desktop** installed on your pc and some basic knowledge on how create a Project and how to write simple queries.
Software can be downloaded here:
[Neo4j Desktop](https://neo4j.com/download/)

**Python 3.6** Enviroment 

**Cloud Custodion** installed and configured for your AWS Environment. At the link below you can find all the info required.
[Cloud Custodian](https://pypi.org/project/c7n/)

### Installing

First of all install Cloud Custodian and following the documentation here https://cloudcustodian.io/docs/index.html create accounts.yml file ( in the repository you have an example how yml file should looks like )
If you have AWS Organizatin follow the link below
https://cloudcustodian.io/docs/tools/c7n-org.html
for generating the file

When ready using the command below you should able to get everythig needed from your aws infrastructure. We use --dryrun but **i kindly suggest to run the command using a readall IAM credential to avoid mistakes**

```
c7n-org run -c accounts.yml -s output -u custodian.yml --region all --dryrun
```
custodian.yml is in the repository

when completed your output folder should full of json files describing your resources. Now you are ready to load data into Neo4j, configure AWSNEoConfig.json with the correct parameters 
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
and run the python scripts from the first to the tenth.

```
01.NeoLoadsAccounts.py
02.NeoRegionLoader.py
03.NeoLoadVPC.py
04.NeoLoadSubnetAndZones.py
05.NeoLoadTransit.py
06.NeoLoadVpns.py
07.NeoLoadTgwAttachments.py
08.NeoLoadPeering.py
09.NeoLoadSecurityGroup.py
10.NeoLoadEc2.py

```

Verify that everything went well running neo4j call db.schema.validation and verify that the schema is the same of my picture.

## Running the tests

Enjoy your exploration!! looking for mistake. The file QueryExample.txt contains some Cypher Query useful.

## Contributing


## Authors

* **BuzzFactory** 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

