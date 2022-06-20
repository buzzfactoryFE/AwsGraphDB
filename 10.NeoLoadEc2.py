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


def NeoLoadEC2(filepath,region, account_id):
# loads contents of Ec2 files
    try:
        with open(filepath) as f:
            data = json.load(f)
            for ec2 in data:
                print(ec2["InstanceId"])
                print(ec2["InstanceType"])
                print(ec2["PrivateIpAddress"])
                print(ec2["SubnetId"])
                try:
                    tags = ec2["Tags"]
                    for tag in tags:
                        if tag["Key"] == "Name":
                            print("Name: " , tag['Value'])
                            nametag = tag['Value']
                        if tag["Key"] == "Backup":
                            backuptag = tag['Value']
                            print("Backup: " , tag['Value'])
                        
                    #se nametag e backuptag sono vuoti li valorizzo no tag
                    if nametag == "":
                        nametag = "no tag"
                    if backuptag == "":
                        backuptag = "no tag"
                except:
                    print('NO TAGS')
                    backuptag = "no tag"
                    nametag = "no tag"
                # creo il nodo EC2 con relazione in Subnet
                NeoCreateEC2(ec2["InstanceId"], nametag, ec2["InstanceType"],ec2["PrivateIpAddress"],ec2["SubnetId"],backuptag)
                for sg in (ec2['SecurityGroups']):
                    print(sg['GroupName'])
                    print(ec2['InstanceId'])
                    NeoCreateSGAttachemnt(ec2['InstanceId'], sg['GroupId'])
                
            
        f.close()
    except Exception as inst:
        print(inst)
        print("ROTTTTTTOOOOOO")





def NeoCreateEC2(InstanceId, name,InstanceType,PrivateIpAddress,subnet,backuptag):
    #
    querysg = 'MATCH (s:Subnet) where s.Id = "'+subnet+'"\n\
MERGE (a:AWSEC2 { InstanceId: "'+InstanceId+'", Name: "'+name+'", InstanceType: "'+InstanceType+'", PrivateIpAddress:"'+PrivateIpAddress+'", Backup: "'+backuptag+'"})\n\
MERGE (a)-[:Ec2Subnet]->(s)'
    print(querysg)
    resultsg = graph.run(querysg).to_table()
    print(resultsg)

def NeoCreateSGAttachemnt(InstanceId, GroupId):
    #
    querysg = 'MATCH (a:SecurityGroup) where a.GroupId = "'+GroupId+'"\n\
MATCH (e:AWSEC2) where e.InstanceId = "'+InstanceId+'"\n\
MERGE (a)-[:SGAttachment]->(e)'
    print(querysg)
    resultsg = graph.run(querysg).to_table()
    print(resultsg)



    

def NeoLoadAccounts(filepath):
    with open(filepath) as f:
        accountList = yaml.safe_load(f)
        for acc in accountList["accounts"]:
            print(acc['name'])
            account_id = acc['account_id']
            print(account_id)
            #creo gli attachement
            for folder in os.listdir(outputfiles+acc['name'] ):
                Aregion = (folder)
                TransitAttachFilepath = outputfiles+acc['name']+"/"+Aregion+"/ec2-instances/resources.json"
                print(TransitAttachFilepath)
                NeoLoadEC2(TransitAttachFilepath,Aregion, account_id)


NeoLoadAccounts(AccountsFilepath)


