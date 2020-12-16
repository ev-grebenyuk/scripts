#!/usr/bin/env python

"""
Script for getting information about resources in VDCs
"""
import sys
import subprocess
import xml.etree.ElementTree as ET
import base64
try:
    import json
except ImportError:
    import simplejson as json
import requests
import re
import os

USER = 'readonly'
KEY = 'VCDPASS'
PASS = os.getenv(KEY)
ORG = 'pcbl_ru'
URL = 'vcd.sbercloud.ru'
ACCEPT = 'application/*;version=31.0'
HREF = '{http://www.vmware.com/vcloud/v1.5}'
vdc = { 'vdc01' : '01fe6f3a-9c1a-451b-98fa-5638aa1921db', 'vdc02' : '9e16021c-22b0-4eb2-b7ae-5f1994f1f6a3'}
storage_policies = {'slow': 'Silver', 'fast': 'Tier 1'}
kilo=1000

def get_response(url, h):
    response = requests.get(url=url, headers=h)
    return response.headers, response.content.decode('utf-8')

def post_response(url, headers):
    response = requests.post(url=url, headers=headers)
    return response.headers, response.content.decode('utf-8')

def get_auth_token():
    auth = f'{USER}@{ORG}:{PASS}'
    auth_ascii = auth.encode('utf-8')
    auth_b64 = base64.b64encode(auth_ascii)
    auth_b64m = auth_b64.decode('utf-8')
    headers = {
        'Accept': ACCEPT,
        'Authorization': f'Basic {auth_b64m}'
    }
    headers, output = post_response(f'https://{URL}/api/sessions', headers)
    return headers['x-vmware-vcloud-access-token']

def get_cpu_ram(auth_token, vdc):
    headers = {
        'Accept': ACCEPT,
        'Authorization': f'Bearer {auth_token}'
    }
    url = f'https://{URL}/api/vdc/{vdc}'
    headers, output = get_response(url, headers)
    xml_data = ET.fromstring(output)
    cpu = {}
    ram = {}
    cpu_ram = {}
    for ents in xml_data.findall(f'{HREF}VCpuInMhz2'):
        cpu['MHz'] = ents.text
    for ents in xml_data.findall(f'{HREF}ComputeCapacity'):
        for entity in ents.findall(f'{HREF}Cpu'):
            cpu['Units'] = entity.find(f'{HREF}Units').text
            cpu['Allocated'] = entity.find(f'{HREF}Allocated').text
            cpu['Limit'] = entity.find(f'{HREF}Limit').text
            cpu['Reserved'] = entity.find(f'{HREF}Reserved').text
            cpu['Used'] = entity.find(f'{HREF}Used').text
        for entity in ents.findall(f'{HREF}Memory'):
            ram['Units'] = entity.find(f'{HREF}Units').text
            ram['Allocated'] = entity.find(f'{HREF}Allocated').text
            ram['Limit'] = entity.find(f'{HREF}Limit').text
            ram['Reserved'] = entity.find(f'{HREF}Reserved').text
            ram['Used'] = entity.find(f'{HREF}Used').text
    cpu_ram['cpu'] = cpu
    cpu_ram['ram'] = ram
    return cpu_ram

def get_storage(auth_token):
    headers = {
        'Accept': ACCEPT,
        'Authorization': f'Bearer {auth_token}'
    }
    url = f'https://{URL}/api/query?type=orgVdcStorageProfile'
    headers, output = get_response(url, headers)
    xml_data = ET.fromstring(output)
    storage = {}
    for ents in xml_data.findall(f'{HREF}OrgVdcStorageProfileRecord'):
        storage[str(ents.get('vdcName'))+'@'+str(ents.get('name'))] = ({'vdcName': ents.get('vdcName'), 'name': ents.get('name'), 'storageLimitMB': ents.get('storageLimitMB'), 'storageUsedMB': ents.get('storageUsedMB')})
    return storage

def get_free_cpu(res):
    # in number
    return (int(res['cpu']['Limit'])-int(res['cpu']['Used']))/int(res['cpu']['MHz'])

def get_free_ram(res):
    # in megabytes
    return (int(res['ram']['Limit'])-int(res['ram']['Used'])) #/ kilo

def get_free_disk(res, vdc, policy):
    # in megabytes
    for i in res.keys():
        vdc_i = i.split('@')[0].split('_')[1]
        policy_i = i.split('@')[1]
        if (vdc_i == vdc) and (policy_i == policy):
            return (int(res[i]['storageLimitMB']) - int(res[i]['storageUsedMB'])) #/ kilo
#    return 0

# Main
auth_token = get_auth_token()
resources_disks = get_storage(auth_token)
resources_cpu_ram = {}

for i in vdc:
    resources_cpu_ram[i] = get_cpu_ram(auth_token, vdc[i])

# Print results
# CPU
print('# HELP vmware_cpu_allocated Returns number of allocated CPU')
print('# TYPE vmware_cpu_allocated gauge')
for i in vdc:
    cpu_mhz = int(resources_cpu_ram[i]['cpu']['MHz'])
    cpu_allocated = int(resources_cpu_ram[i]['cpu']['Allocated']) / cpu_mhz
    print('vmware_cpu_allocated{vdc="' + i.split('0')[1] + '"} ' + str(cpu_allocated))

print('# HELP vmware_cpu_limit Returns number of limit CPU')
print('# TYPE vmware_cpu_limit gauge')
for i in vdc:
    cpu_mhz = int(resources_cpu_ram[i]['cpu']['MHz'])
    cpu_limit = int(resources_cpu_ram[i]['cpu']['Limit']) / cpu_mhz
    print('vmware_cpu_limit{vdc="' + i.split('0')[1] + '"} ' + str(cpu_limit))

print('# HELP vmware_cpu_reserved Returns number of reserved CPU')
print('# TYPE vmware_cpu_reserved gauge')
for i in vdc:
    cpu_mhz = int(resources_cpu_ram[i]['cpu']['MHz'])
    cpu_reserved = int(resources_cpu_ram[i]['cpu']['Reserved']) / cpu_mhz
    print('vmware_cpu_reserved{vdc="' + i.split('0')[1] + '"} ' + str(cpu_reserved))

print('# HELP vmware_cpu_used Returns number of used CPU')
print('# TYPE vmware_cpu_used gauge')
for i in vdc:
    cpu_mhz = int(resources_cpu_ram[i]['cpu']['MHz'])
    cpu_used = int(resources_cpu_ram[i]['cpu']['Used']) / cpu_mhz
    print('vmware_cpu_used{vdc="' + i.split('0')[1] + '"} ' + str(cpu_used))

# RAM
print('# HELP vmware_ram_allocated Returns number of allocated RAM in MB')
print('# TYPE vmware_ram_allocated gauge')
for i in vdc:
    ram_allocated = resources_cpu_ram[i]['ram']['Allocated']
    print('vmware_ram_allocated{vdc="' + i.split('0')[1] + '"} ' + ram_allocated)

print('# HELP vmware_ram_limit Returns number of limit RAM in MB')
print('# TYPE vmware_ram_limit gauge')
for i in vdc:
    ram_limit = resources_cpu_ram[i]['ram']['Limit']
    print('vmware_ram_limit{vdc="' + i.split('0')[1] + '"} ' + ram_limit)

print('# HELP vmware_ram_reserved Returns number of reserved RAM in MB')
print('# TYPE vmware_ram_reserved gauge')
for i in vdc:
    ram_reserved = resources_cpu_ram[i]['ram']['Reserved']
    print('vmware_ram_reserved{vdc="' + i.split('0')[1] + '"} ' + ram_reserved)

print('# HELP vmware_ram_used Returns number of used RAM in MB')
print('# TYPE vmware_ram_used gauge')
for i in vdc:
    ram_used = resources_cpu_ram[i]['ram']['Used']
    print('vmware_ram_used{vdc="' + i.split('0')[1] + '"} ' + ram_used)

# Storage
# SAS
print('# HELP vmware_sas_limit Returns number of limit SAS storage in MB')
print('# TYPE vmware_sas_limit gauge')
for i in vdc:
    vdc_policy = 'pcblru_' + i + '@' + storage_policies['slow']
    sas_limit = resources_disks[vdc_policy]['storageLimitMB']
    print('vmware_sas_limit{vdc="' + i.split('0')[1] + '"} ' + sas_limit)

print('# HELP vmware_sas_used Returns number of used SAS storage in MB')
print('# TYPE vmware_sas_used gauge')
for i in vdc:
    vdc_policy = 'pcblru_' + i + '@' + storage_policies['slow']
    sas_used = resources_disks[vdc_policy]['storageUsedMB']
    print('vmware_sas_used{vdc="' + i.split('0')[1] + '"} ' + sas_used)

# SSDs
print('# HELP vmware_ssd_limit Returns number of limit SSD storage in MB')
print('# TYPE vmware_ssd_limit gauge')
for i in vdc:
    vdc_policy = 'pcblru_' + i + '@' + storage_policies['fast']
    ssd_limit = resources_disks[vdc_policy]['storageLimitMB']
    print('vmware_ssd_limit{vdc="' + i.split('0')[1] + '"} ' + ssd_limit)

print('# HELP vmware_ssd_used Returns number of used SSD storage in MB')
print('# TYPE vmware_ssd_used gauge')
for i in vdc:
    vdc_policy = 'pcblru_' + i + '@' + storage_policies['fast']
    ssd_used = resources_disks[vdc_policy]['storageUsedMB']
    print('vmware_ssd_used{vdc="' + i.split('0')[1] + '"} ' + ssd_used)
