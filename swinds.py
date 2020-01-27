#!/usr/bin/env python

# ======================================================================================================================
# IMPORTS
# ======================================================================================================================
import configparser
import requests
import re
import json
import os


# ======================================================================================================================
# FUNCTION DEFINITIONS
# ======================================================================================================================
# Creates an empty inventory
def empty_inventory():
  return {'_meta': {'hostvars': {}}}

# Modify group name to comply with Ansible's limitations (no special characters; underscores only)
def clean_group_name(group):
  group = re.sub('[^A-Za-z0-9]+', '_', group)
  return group

# Remove domain ('efka.gr') from hostname
def clean_host_name(host):
  host = host.split('.')[0]
  return host

# Perform SWQL query over REST API using the given payload string
def swql_query(payload):
  # Each SELECT statement must be prepended with 'query= '
  payload = "query= " + payload

  # Perform SWQL query for groups and validate results
  req = requests.get(url, params=payload, verify=False, auth=(user, password))
  jsonget = req.json()
  jsonget = eval(json.dumps(jsonget))

  return jsonget['results']

# Populate the hosts part of the inventory
def get_hosts(hostfields, inventory):
  # Construct 'query' including all the hostfields defined in the config_file
  query = "SELECT " + ", ".join(list(hostfields.values())) + " FROM Orion.Nodes WHERE Vendor = 'Cisco'"
  
  # Retrieve complete list of hosts
  hosts = swql_query(query)

  # Populate inventory with hosts containing values
  for host in hosts:
    host[sysname] = clean_host_name(host[sysname])                        # Remove domain suffix from hostname
    hDict = {k:host[v] for (k,v) in hostfields.items() if k!='sysname'}   # Use comprehension to construct values dict
    inventory['_meta']['hostvars'][host[sysname]] = hDict                 # Append consctucted values dict under host
  return inventory

# Populate the groups part of the inventory
def get_groups(groupings, inventory):
  # Perform the following actions for each grouping defined in the config_items
  for grouping, query in groupings.items():
    # Retrieve complete list of hosts
    hosts = swql_query(query)
    
    # Populate inventory with groups containing member hosts
    for host in hosts:
      host[sysname] = clean_host_name(host[sysname])                      # Remove domain suffix from hostname
      host[grouping] = grouping + '_' + clean_group_name(host[grouping])  # Replace special chars with underscores
      if host[grouping] in inventory:                                     # If group already exists in inventory
        inventory[host[grouping]]['hosts'].append(host[sysname])          # ...append host to it
      else:                                                               # ...or else
        inventory[host[grouping]] = {'hosts': [host[sysname]]}            # ...create group and add host to it
  return inventory


# ======================================================================================================================
# MAIN PROGRAM
# ======================================================================================================================
# Read config file
pwd = os.path.dirname(__file__)                                           # Assuming that 'swinds.ini' exists
config_file = pwd + '/swinds.ini'                                         # in the same folder as 'swinds.py'
config = configparser.ConfigParser()
config.readfp(open(config_file))

# Get all configuration variables from config file using dict comprehension
config_items = {section:dict(config.items(section)) for section in config.sections()}

# Define first-level variables parsing config_items directly
server = config_items['solarwinds']['npm_server']
user = config_items['solarwinds']['npm_user']
password = config_items['solarwinds']['npm_password']
hostfields = config_items['hostfields']
groupings = config_items['groupings']

# Define second-level variables that are products of the first-level ones
url = "https://"+server+":17778/SolarWinds/InformationService/v3/Json/Query"
sysname = hostfields['sysname']

# Create the inventory for Ansible
inventory = {'_meta': {'hostvars': {}}}                                   # Initialize inventory
inventory = get_hosts(hostfields, inventory)                              # Add hosts with vars
inventory = get_groups(groupings, inventory)                              # Add groups with members

# Print the inventory in JSON format
print(json.dumps(inventory, indent=2))
