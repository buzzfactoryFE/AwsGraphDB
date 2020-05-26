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


def NeoLoadPeering(filepath,region, account_id):
# loads contents of Ec2 files
    try:
        with open(filepath) as f:
            data = json.load(f)
            for peer in data:
                AccepterVpcInfoCidrBlock = (peer["AccepterVpcInfo"]["CidrBlock"])
                AccepterVpcInfoCidrVpcId = (peer["AccepterVpcInfo"]["VpcId"])
                RequesterVpcInfoCidrBlock = (peer["RequesterVpcInfo"]["CidrBlock"])
                RequesterVpcInfoCidrVpcId = (peer["RequesterVpcInfo"]["VpcId"])
                VpcPeeringConnectionId = (peer["VpcPeeringConnectionId"])
                try:
                    tags = peer["Tags"]
                    for tag in tags:
                        if tag["Key"] == "Name":
                            PeeringName = (tag["Value"])
                            print(PeeringName)
                            NeoCreatePeering(AccepterVpcInfoCidrBlock,AccepterVpcInfoCidrVpcId,RequesterVpcInfoCidrBlock,RequesterVpcInfoCidrVpcId,VpcPeeringConnectionId,PeeringName)

                except:
                    PeeringName = "NoName"
                    print(PeeringName)
                    NeoCreatePeering(AccepterVpcInfoCidrBlock,AccepterVpcInfoCidrVpcId,RequesterVpcInfoCidrBlock,RequesterVpcInfoCidrVpcId,VpcPeeringConnectionId,PeeringName)


        f.close()
    except Exception as inst:
        print(inst)





def NeoCreatePeering(AccepterVpcInfoCidrBlock,AccepterVpcInfoCidrVpcId,RequesterVpcInfoCidrBlock,RequesterVpcInfoCidrVpcId,VpcPeeringConnectionId,PeeringName ):
    #verifico se il peering esiste già
    querypeer = 'MATCH p=()-[r:Peering]->() where r.VpcPeeringConnectionId = "'+VpcPeeringConnectionId+'"\n\
return p'
    resultpeer = graph.run(querypeer).to_table()
    print(len(resultpeer))
    if (len(resultpeer)) == 0:
        query = 'match (r:AWSVpc) where r.CidrBlock = "'+RequesterVpcInfoCidrBlock+'" and r.Id = "'+RequesterVpcInfoCidrVpcId+'"\n\
match (a:AWSVpc) where a.CidrBlock = "'+AccepterVpcInfoCidrBlock+'" and a.Id = "'+AccepterVpcInfoCidrVpcId+'"\n\
merge (r)-[:Peering{ Name: "'+PeeringName+'", VpcPeeringConnectionId : "'+VpcPeeringConnectionId+'"}]->(a)'
    
        print(query)
        result = graph.run(query).to_table()
        print(result)
    else:
        print("Peering already exist")


def NeoLoadAccounts(filepath):
    with open(filepath) as f:
        accountList = yaml.load(f)
        for acc in accountList["accounts"]:
            print(acc['name'])
            account_id = acc['account_id']
            print(account_id)
            #creo gli attachement
            for folder in os.listdir(outputfiles+acc['name'] ):
                Aregion = (folder)
                TransitAttachFilepath = outputfiles+acc['name']+"/"+Aregion+"/peering/resources.json"
                print(TransitAttachFilepath)
                NeoLoadPeering(TransitAttachFilepath,Aregion, account_id)


NeoLoadAccounts(AccountsFilepath)


