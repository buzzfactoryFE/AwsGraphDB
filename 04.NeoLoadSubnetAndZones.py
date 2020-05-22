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

def NeoLoadSubnetes(filepath,region):
# loads contents of Ec2 files
    try:
        with open(filepath) as f:
            data = json.load(f)
            for subnet in data:
                print(subnet["CidrBlock"])
                print(subnet["VpcId"])
                print(subnet["AvailabilityZone"])
                print(subnet["AvailabilityZoneId"])
                print(subnet["SubnetId"])
                try:
                    tags = subnet["Tags"]
                    for tag in tags:
                        if tag["Key"] == "Name":
                            sunbnetName = (tag["Value"])
                            print(sunbnetName)
                            NeoInsertSubnetsAndZones(subnet["CidrBlock"],subnet["VpcId"],subnet["AvailabilityZone"],subnet["AvailabilityZoneId"],sunbnetName, subnet["SubnetId"], region)
                except:
                    sunbnetName = "NoName"
                    print(sunbnetName)
                    NeoInsertSubnetsAndZones(subnet["CidrBlock"],subnet["VpcId"],subnet["AvailabilityZone"],subnet["AvailabilityZoneId"],sunbnetName, subnet["SubnetId"] ,region)      

        f.close()
    except Exception as inst:
        print(inst) 


def NeoInsertSubnetsAndZones(CidrBlock, VpcId,SubnetZone,ZoneId,Name , SubnetId, AwsRegion):#
    query = 'MERGE (v: AWSVpc { Id : "'+VpcId+'" })\n\
MERGE (z: AWSZone { Name : "'+ZoneId+'", Id: "'+ZoneId+'" })\n\
MERGE (r: AWSRegion { Id : "'+AwsRegion+'"})\n\
MERGE (s: Subnet {Name : "'+Name+'" , Id : "'+SubnetId+'" , CidrBlock : "'+CidrBlock+'" })\n\
MERGE (s)-[:InZone]->(z)\n\
MERGE (s)-[:InVpc]->(v)\n\
MERGE (z)-[:INRegion]->(r)'
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
                SubenetFilepath = outputfiles+acc['name']+"/"+Aregion+"/subnets/resources.json"
                print(SubenetFilepath)
                NeoLoadSubnetes(SubenetFilepath,Aregion)




NeoLoadAccounts(AccountsFilepath)


