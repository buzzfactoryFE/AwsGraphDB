import os, json, yaml, untangle
from py2neo import Graph

with open("./AWSNEoConfig.json") as c:
    conf = json.load(c)
    print(conf[0]["AccountsFilepath"])
    print(conf[0]["NeoParametes"][0]["Url"])
c.close

graph = Graph(conf[0]["NeoParametes"][0]["Url"], auth=(conf[0]["NeoParametes"][0]["Username"], conf[0]["NeoParametes"][0]["Password"]))
AccountsFilepath = conf[0]["AccountsFilepath"]
outputfiles = conf[0]["custodianFiles"]


def NeoLoadVpns(filepath,region, account_id):
    try:
        with open(filepath) as f:
            data = json.load(f)
            for vpn in data:
                #print(vpn["CustomerGatewayConfiguration"])
                vpnconfxml = untangle.parse(vpn["CustomerGatewayConfiguration"])
                print(vpnconfxml.vpn_connection.ipsec_tunnel[0].customer_gateway.tunnel_outside_address.ip_address.cdata)
                print(vpn["CustomerGatewayId"])
                print(vpn["VpnConnectionId"])
                CgwIp = vpnconfxml.vpn_connection.ipsec_tunnel[0].customer_gateway.tunnel_outside_address.ip_address.cdata
                try:
                    tags = vpn["Tags"]
                    for tag in tags:
                        if tag["Key"] == "Name":
                            VpnName = (tag["Value"])
                            print(VpnName)
                            NeoCreateCustomerGateway(vpn["CustomerGatewayId"],CgwIp,VpnName, vpn["VpnConnectionId"],account_id)
                except:
                    VpnName = "NoName"
                    print(VpnName)
                    NeoCreateCustomerGateway(vpn["CustomerGatewayId"],CgwIp,VpnName, vpn["VpnConnectionId"],account_id)
                    
        f.close()
    except Exception as inst:
        print(inst)


def NeoCreateCustomerGateway(CgwId,IPaddress,Name, vpnId ,accountId ):
    query = 'MERGE (c: VPNCustomerGateway {Name : "'+Name+'", Id: "'+CgwId+'" , IPAddress : "'+IPaddress+'", vpnId: "'+vpnId+'", AccountId: "'+accountId+'" })'
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
                VpnFilepath = outputfiles+acc['name']+"/"+Aregion+"/vpns/resources.json"
                print(VpnFilepath)
                NeoLoadVpns(VpnFilepath,Aregion, account_id)


NeoLoadAccounts(AccountsFilepath)

