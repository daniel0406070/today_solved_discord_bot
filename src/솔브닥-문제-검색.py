import http.client
import json
import os

conn = http.client.HTTPSConnection("solved.ac")
headers = { 'Accept': "application/json" }

problem=input("problem: ")
conn.request("GET", f"/api/v3/problem/show?problemId={problem}", headers=headers)

res = conn.getresponse()
data = res.read()
data = data.decode("utf-8")
json_data = json.loads(data)

print(json_data["problemId"],"!!",json_data["titleKo"],"!!",json_data["level"],"\\\\",end=" ")

for j in range(len(json_data["tags"])):
    print(json_data["tags"][j]["displayNames"][0]["name"],end=",")
print()

os.system("pause")