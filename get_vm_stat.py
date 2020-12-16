import json
#import prettytable

tf_state='terraform.tfstate'
#title="resource_name, computer_name, cpu_hot_add_enabled, memory_hot_add_enabled"
count = 0

with open(tf_state) as json_file:
    data = json.load(json_file)
    #t = prettytable(title)
    print("resource_name, computer_name, cpu_hot_add_enabled, memory_hot_add_enabled")
    for res in data["resources"]:
        if res["type"] == "vcd_vapp_vm":
            #print(res["name"])
            for vm in res["instances"]:
                if (vm['attributes']["cpu_hot_add_enabled"] == False or vm['attributes']["memory_hot_add_enabled"] == False):
                    print(res["name"], ",", vm['attributes']['computer_name'], ",", vm['attributes']["cpu_hot_add_enabled"], ",", vm['attributes']["memory_hot_add_enabled"])
                    count += 1
                    #t.add_row([res["name"], vm['attributes']['computer_name'], vm['attributes']["cpu_hot_add_enabled"], vm['attributes']["memory_hot_add_enabled"]])
    #print(t)
    print("Total VMs: ", count)