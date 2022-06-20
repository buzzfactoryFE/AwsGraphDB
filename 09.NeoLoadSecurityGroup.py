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


def NeoLoadSG(filepath,region, account_id):
# loads contents of Ec2 files
    try:
        with open(filepath) as f:
            data = json.load(f)
            for sg in data:
                print(sg["GroupName"])
                print(sg["GroupId"])
                print(sg["VpcId"])
                NeoCreateSG( sg["GroupName"],sg["GroupId"],sg["VpcId"])
                for ingress in sg["IpPermissions"]:
                    print(ingress["UserIdGroupPairs"])
                    if ingress["IpProtocol"] == '-1':
                        PortRanage = "All"
                        print(PortRanage)
                        NeoCreatePortRange(PortRanage,"all",sg["GroupId"],"IN",sg["VpcId"])
                        #get ip
                        for ips in ingress["IpRanges"]:
                            #print(ips["CidrIp"])
                            NeoCreateIP(PortRanage,"all",ips["CidrIp"],"IN",sg["GroupId"])
                    else:
                        #print(ingress["FromPort"])
                        #print(ingress["ToPort"])
                        #print(ingress["IpProtocol"])
                        PortRanage = 'From'+str(ingress["FromPort"])+'To'+str(ingress["ToPort"])
                        NeoCreatePortRange(PortRanage,ingress["IpProtocol"],sg["GroupId"],"IN",sg["VpcId"])
                        for ips in ingress["IpRanges"]:
                            #print(ips["CidrIp"])
                            NeoCreateIP(PortRanage,ingress["IpProtocol"],ips["CidrIp"],"IN",sg["GroupId"])
                for egress in sg["IpPermissionsEgress"]:
                    print(egress["UserIdGroupPairs"])
                    if egress["IpProtocol"] == '-1':
                        PortRanage = "All"
                        print(PortRanage)
                        NeoCreatePortRange(PortRanage,"all",sg["GroupId"],"OUT",sg["VpcId"])
                        for ips in egress["IpRanges"]:
                            #print(ips["CidrIp"])
                            NeoCreateIP(PortRanage,"all",ips["CidrIp"],"OUT",sg["GroupId"])
                    else:
                        PortRanage = 'From'+str(egress["FromPort"])+'To'+str(egress["ToPort"])
                        NeoCreatePortRange(PortRanage,egress["IpProtocol"],sg["GroupId"],"OUT",sg["VpcId"])
                        for ips in egress["IpRanges"]:
                            #print(ips["CidrIp"])
                            NeoCreateIP(PortRanage,egress["IpProtocol"],ips["CidrIp"],"OUT",sg["GroupId"])

        f.close()
        ####riciclo sul file per creare i legami in e out tra security group
        print('Secondo giro')
        LinkSG(filepath,region, account_id)
    except Exception as inst:
        print(inst)
        print("ROTTTTTTOOOOOO")


def LinkSG(filepath,region, account_id):
    try:
        with open(filepath) as f:
            data = json.load(f)
            for sg in data:
                print(sg["GroupName"])
                print(sg["GroupId"])
                print(sg["VpcId"])
                for ingress in sg["IpPermissions"]:
                    print(ingress["UserIdGroupPairs"])
                    if ingress["IpProtocol"] == '-1':
                        PortRanage = "All"
                        print(PortRanage)
                        #get ip
                        for ips in ingress["UserIdGroupPairs"]:
                            #print(ips["CidrIp"])
                            NeoCreateSGLink(PortRanage,"all",ips["GroupId"],"IN",sg["GroupId"])
                    else:
                        PortRanage = 'From'+str(ingress["FromPort"])+'To'+str(ingress["ToPort"])
                        for ips in ingress["UserIdGroupPairs"]:
                            #print(ips["CidrIp"])
                            NeoCreateSGLink(PortRanage,ingress["IpProtocol"],ips["GroupId"],"IN",sg["GroupId"])
                for egress in sg["IpPermissionsEgress"]:
                    print(egress["UserIdGroupPairs"])
                    if egress["IpProtocol"] == '-1':
                        PortRanage = "All"
                        print(PortRanage)
                        for ips in egress["UserIdGroupPairs"]:
                            #print(ips["CidrIp"])
                            NeoCreateSGLink(PortRanage,"all",ips["GroupId"],"OUT",sg["GroupId"])
                    else:
                        PortRanage = 'From'+str(egress["FromPort"])+'To'+str(egress["ToPort"])
                        for ips in egress["UserIdGroupPairs"]:
                            #print(ips["CidrIp"])
                            NeoCreateSGLink(PortRanage,egress["IpProtocol"],ips["GroupId"],"OUT",sg["GroupId"])

        f.close()
    except Exception as inst:
        print(inst)
        print("ROTTTTTTOOOOOO")

def NeoCreateSG(GroupName, GroupId,VpcId):
    #
    querysg = 'match (a:AWSVpc) where a.Id = "'+VpcId+'"\n\
MERGE (a)<-[:VpcOwner]-(s: SecurityGroup { Name: "'+GroupName+'", GroupId: "'+GroupId+'", VpcId: "'+VpcId+'" })'
    print(querysg)
    resultsg = graph.run(querysg).to_table()
    print(resultsg)


def NeoCreatePortRange(PRName, PRProtocol,sg,direction,vpc):
    #v
    querysg = 'MATCH (a:SecurityGroup) where a.GroupId = "'+sg+'"\n\
MERGE (p:PortRange {Name: "'+PRName+'", Protocol: "'+PRProtocol+'", SG: "'+sg+'"})\n\
MERGE (p)-[:PortRangeSG]->(a)'

    print(querysg)
    resultsg = graph.run(querysg).to_table()
    print(resultsg)

def NeoCreateIP(PRName, PRProtocol,CidrIp,direction,sgGroupId):
    if direction == "IN":
        queryip = 'MATCH (a:PortRange) where a.Name = "'+PRName+'" and a.Protocol = "'+PRProtocol+'" and a.SG = "'+sgGroupId+'"\n\
MATCH (s:SecurityGroup) where s.GroupId = "'+sgGroupId+'"\n\
MERGE (p:SGIPSource {CidrIp: "'+CidrIp+'"})\n\
MERGE (p)-[:In]->(a)\n\
MERGE (p)-[:Ingress]->(s)'
    if direction == "OUT":
        queryip = 'MATCH (a:PortRange) where a.Name = "'+PRName+'" and a.Protocol = "'+PRProtocol+'"and a.SG = "'+sgGroupId+'"\n\
MATCH (s:SecurityGroup) where s.GroupId = "'+sgGroupId+'"\n\
MERGE (p:SGIPSource {CidrIp: "'+CidrIp+'"})\n\
MERGE (p)<-[:Out]-(a)\n\
MERGE (p)<-[:Egress]-(s)'
    print(queryip)
    resultsg = graph.run(queryip).to_table()
    print(resultsg)

def NeoCreateSGLink(PRName, PRProtocol,CidrIp,direction,sgGroupId):
    if direction == "IN":
        queryip = 'MATCH (a:PortRange) where a.Name = "'+PRName+'" and a.Protocol = "'+PRProtocol+'" and a.SG = "'+sgGroupId+'"\n\
MATCH (s:SecurityGroup) where s.GroupId = "'+sgGroupId+'"\n\
MATCH (p:SecurityGroup) where p.GroupId = "'+CidrIp+'"\n\
MERGE (p)-[:In]->(a)\n\
MERGE (p)-[:Ingress]->(s)'
    if direction == "OUT":
        queryip = 'MATCH (a:PortRange) where a.Name = "'+PRName+'" and a.Protocol = "'+PRProtocol+'"and a.SG = "'+sgGroupId+'"\n\
MATCH (s:SecurityGroup) where s.GroupId = "'+sgGroupId+'"\n\
MATCH (p:SecurityGroup) where p.GroupId = "'+CidrIp+'"\n\
MERGE (p)<-[:Out]-(a)\n\
MERGE (p)<-[:Egress]-(s)'
    print(queryip)
    resultsg = graph.run(queryip).to_table()
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
                TransitAttachFilepath = outputfiles+acc['name']+"/"+Aregion+"/security-group/resources.json"
                print(TransitAttachFilepath)
                NeoLoadSG(TransitAttachFilepath,Aregion, account_id)


NeoLoadAccounts(AccountsFilepath)


