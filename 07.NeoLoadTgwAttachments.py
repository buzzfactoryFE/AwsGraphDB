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


def NeoLoadTransitAttachment(filepath,region, account_id):
    try:
        with open(filepath) as f:
            data = json.load(f)
            for transit in data:
                print(transit["TransitGatewayId"])
                print(transit["ResourceId"])
                print(transit["ResourceType"])
                print(transit["TransitGatewayAttachmentId"])
                print(transit["ResourceOwnerId"])
                if transit["ResourceType"] == "vpc":
                    try:
                        if transit["TransitGatewayOwnerId"] == account_id:
                            restype = "tgtovpc"
                        else:
                            restype = "vpctotg"
                    except:
                        restype = "vpctotg"
                    print(restype)
                    try:
                        tags = transit["Tags"]
                        if len(tags) == 0:
                            TransitName = "NoName"
                            NeoCreateAttachment(transit["TransitGatewayId"],transit["TransitGatewayAttachmentId"],TransitName,restype,transit["ResourceId"])
                        else:
                            for tag in tags:
                                if tag["Key"] == "Name":
                                    TransitName = (tag["Value"])
                                    print(TransitName)
                                    NeoCreateAttachment(transit["TransitGatewayId"],transit["TransitGatewayAttachmentId"],TransitName,restype,transit["ResourceId"])
                                else:
                                    TransitName = "NoName"
                                    print(TransitName)
                                    NeoCreateAttachment(transit["TransitGatewayId"],transit["TransitGatewayAttachmentId"],TransitName,restype,transit["ResourceId"])
                    except:
                        TransitName = "NoName"
                        print(TransitName)
                        NeoCreateAttachment(transit["TransitGatewayId"],transit["TransitGatewayAttachmentId"],TransitName,restype,transit["ResourceId"])
                if transit["ResourceType"] == "vpn":
                    restype = "vpn"
                    print(restype)
                    try:
                        tags = transit["Tags"]
                        if len(tags) == 0:
                            TransitName = "NoName"
                            NeoCreateAttachment(transit["TransitGatewayId"],transit["TransitGatewayAttachmentId"],TransitName,restype,transit["ResourceId"])
                        else:
                            TransitName == ""
                            for tag in tags:
                                if tag["Key"] == "Name":
                                    TransitName = (tag["Value"])
                                    print(TransitName)
                            
                            if TransitName == "":
                                TransitName = "NoName"
                            print(TransitName)
                            NeoCreateAttachment(transit["TransitGatewayId"],transit["TransitGatewayAttachmentId"],TransitName,restype,transit["ResourceId"])
                    except:
                        TransitName = "NoName"
                        print(TransitName)


        f.close()
    except Exception as inst:
        print(inst)





def NeoCreateAttachment(TgwTransitGatewayIdId,TransitGatewayAttachmentId,Name,ResourceType,ResourceId ):
    if ResourceType == "tgtovpc":
        query = 'MATCH (n:AWSVpc) where n.Id = "'+ResourceId+'"\n\
MATCH (t:AWSTgw) where t.Id = "'+TgwTransitGatewayIdId+'"\n\
MERGE (t)-[:TransitGatewayAttachment {Name: "'+Name+'", Id: "'+TransitGatewayAttachmentId+'"}]->(n)'
    if ResourceType == "vpctotg":
        query = 'MATCH (n:AWSVpc) where n.Id = "'+ResourceId+'"\n\
MATCH (t:AWSTgw) where t.Id = "'+TgwTransitGatewayIdId+'"\n\
MERGE (t)<-[:TransitGatewayAttachment {Name: "'+Name+'", Id: "'+TransitGatewayAttachmentId+'"}]-(n)'
    if ResourceType == "vpn":
        query = 'MATCH (n:VPNCustomerGateway) where n.vpnId = "'+ResourceId+'"\n\
MATCH (t:AWSTgw) where t.Id = "'+TgwTransitGatewayIdId+'"\n\
MERGE (t)-[:TransitGatewayAttachment {Name: "'+Name+'", Id: "'+TransitGatewayAttachmentId+'"}]->(n)'
    
    
    print(query)
    result = graph.run(query).to_table()
    print(result)


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
                TransitAttachFilepath = outputfiles+acc['name']+"/"+Aregion+"/TransitGatewayAttachment/resources.json"
                print(TransitAttachFilepath)
                NeoLoadTransitAttachment(TransitAttachFilepath,Aregion, account_id)


NeoLoadAccounts(AccountsFilepath)


