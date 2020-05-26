import os, csv, json
from py2neo import Graph

with open("./AWSNEoConfig.json") as c:
    conf = json.load(c)
c.close

graph = Graph(conf[0]["NeoParametes"][0]["Url"], auth=(conf[0]["NeoParametes"][0]["Username"], conf[0]["NeoParametes"][0]["Password"]))


regions ="US East (Ohio),us-east-2\n\
US East (N. Virginia),us-east-1\n\
US West (N. California),us-west-1\n\
US West (Oregon),us-west-2\n\
Asia Pacific (Hong Kong),ap-east-1\n\
Asia Pacific (Mumbai),ap-south-1\n\
Asia Pacific (Osaka-Local),ap-northeast-3\n\
Asia Pacific (Seoul),ap-northeast-2\n\
Asia Pacific (Singapore),ap-southeast-1\n\
Asia Pacific (Sydney),ap-southeast-2\n\
Asia Pacific (Tokyo),ap-northeast-1\n\
Canada (Central),ca-central-1\n\
Europe (Frankfurt),eu-central-1\n\
Europe (Ireland),eu-west-1\n\
Europe (London),eu-west-2\n\
Europe (Paris),eu-west-3\n\
Europe (Stockholm),eu-north-1\n\
Middle East (Bahrain),me-south-1\n\
South America (São Paulo),sa-east-1"

def NeoInsertRegions(Name,id):#
    query = 'MERGE (: AWSRegion { Name: "'+Name+'" , Id : "'+id+'" })'
    print(query)
    result = graph.run(query).to_table()
    print(result)

#print(regions)
reader = csv.reader(regions.split('\n'), delimiter=',')
for row in reader:
    NeoInsertRegions(row[0],row[1])