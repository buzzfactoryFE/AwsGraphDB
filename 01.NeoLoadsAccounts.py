import os, yaml, json
from py2neo import Graph

with open("./AWSNEoConfig.json") as c:
    conf = json.load(c)
    print(conf[0]["AccountsFilepath"])
    print(conf[0]["NeoParametes"][0]["Url"])
c.close

graph = Graph(conf[0]["NeoParametes"][0]["Url"], auth=(conf[0]["NeoParametes"][0]["Username"], conf[0]["NeoParametes"][0]["Password"]))
AccountsFilepath = conf[0]["AccountsFilepath"]

def NeoLoadAccounts(filepath):
# loads contents aws accounts
    with open(filepath) as f:
        accountList = yaml.load(f)
        for acc in accountList["accounts"]:
            print(acc['name'])
            print(acc['account_id'])
            NeoInsertAccounts(acc['name'],acc['account_id'])


def NeoInsertAccounts(AccName, accID):
    query = 'MERGE (c:AwsMaster {Name : "CRIF-MASTER"})\n\
    MERGE (n:LinkedAccount {Name: "'+AccName+'" , Id: "'+accID+'"})\n\
    MERGE (c)-[:Linked]->(n)'
    print(query)
    result = graph.run(query).to_table()
    print(result)

NeoLoadAccounts(AccountsFilepath)

