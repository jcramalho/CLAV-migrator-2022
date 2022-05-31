import json
f = open('./files/100.json')
my100 = json.load(f)
print(type(my100), " :: ", my100)