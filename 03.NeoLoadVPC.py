import os, json, yaml
from py2neo import Graph

with open("./AWSNEoConfig.json") as c:
    conf = json.load(c)
    print(conf[0]["AccountsFilepath"])
    print(conf[0]["NeoParametes"][0]["Url"])
c.close

graph = Graph(conf[0]["NeoParametes"][0]["Url"], auth=(conf[0]["NeoParametes"][0]["Username"], conf[0]["NeoParametes"][0]["Password"]))
AccountsFilepath = conf[0]["AccountsFilepath"]
outputfiles = conf[0]["custodianFiles"]

def NeoLoadVPC(filepath,region):
# loads contents of Ec2 files
    try:
        with open(filepath) as f:
            data = json.load(f)
            for vpc in data:
                print(vpc["CidrBlock"])
                print(vpc["VpcId"])
                print(vpc["OwnerId"])
                try:
                    tags = vpc["Tags"]
                    for tag in tags:
                        if tag["Key"] == "Name":
                            vpcname = (tag["Value"])
                            NeoInsertVPC(vpc["CidrBlock"],vpc["VpcId"],vpc["OwnerId"],vpcname, region)
                except:
                    vpcname = "NoName"
                    NeoInsertVPC(vpc["CidrBlock"],vpc["VpcId"],vpc["OwnerId"],vpcname, region)        
        f.close()
    except Exception as inst:
        print(inst)



def NeoInsertVPC(CidrBlock, VpcId,OwnerId,Name , AwsRegion):#
    query = 'MERGE (v: AWSVpc { Name: "'+Name+'" , Id : "'+VpcId+'" , CidrBlock : "'+CidrBlock+'" })\n\
MERGE (r: AWSRegion { Id : "'+AwsRegion+'"})\n\
MERGE (l: LinkedAccount {Id : "'+OwnerId+'"})\n\
MERGE (l)-[:owner]->(v)\n\
MERGE (r)-[:geo]->(v)'
    print(query)
    result = graph.run(query).to_table()
    print(result)


def NeoLoadAccounts(filepath):
    with open(filepath) as f:
        accountList = yaml.load(f)
        for acc in accountList["accounts"]:
            print(acc['name'])
            for folder in os.listdir(outputfiles+acc['name'] ):
                Aregion = (folder)
                vpcfile = outputfiles+acc['name']+"/"+Aregion+"/vpcs/resources.json"
                print(vpcfile)
                NeoLoadVPC(vpcfile,Aregion)



NeoLoadAccounts(AccountsFilepath)


