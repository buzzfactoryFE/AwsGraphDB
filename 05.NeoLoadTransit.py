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


def NeoLoadTransit(filepath,region, account_id):
    try:
        with open(filepath) as f:
            data = json.load(f)
            for transit in data:
                print(transit["TransitGatewayId"])
                print(transit["OwnerId"])
                try:
                    tags = transit["Tags"]
                    for tag in tags:
                        if tag["Key"] == "Name":
                            TransitName = (tag["Value"])
                            print(TransitName)
                except:
                    TransitName = "NoName"
                    print(TransitName)
                if transit["OwnerId"] == account_id:
                    print('creo transit')
                    NeoCreateTransit(transit["TransitGatewayId"],transit["OwnerId"],TransitName)
        f.close()
    except:
        print("no TGW file")


def NeoCreateTransit(TgwId,OwnerId,Name ):#
    query = 'MATCH (l:LinkedAccount) where l.Id = "'+OwnerId+'"\n\
MERGE (z: AWSTgw { Name : "'+Name+'", Id: "'+TgwId+'" })\n\
MERGE (l)-[:ownTgw]->(z)'
    print(query)
    result = graph.run(query).to_table()
    print(result)


def NeoLoadAccounts(filepath):
    with open(filepath) as f:
        accountList = yaml.safe_load(f)
        for acc in accountList["accounts"]:
            print(acc['name'])
            account_id = acc['account_id']
            print(account_id)
            #creo i transit gateway
            for folder in os.listdir(outputfiles+acc['name'] ):
                Aregion = (folder)
                TransitFilepath = outputfiles+acc['name']+"/"+Aregion+"/TransitGateway/resources.json"
                print(TransitFilepath)
                NeoLoadTransit(TransitFilepath,Aregion, account_id)


NeoLoadAccounts(AccountsFilepath)


