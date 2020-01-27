# swinds-ansible-inv
Dynamic Inventory for Solar Winds hosts in Ansible

~~This python script connects to Solar Winds via rest API to create a dynamic inventory in Ansible.  JSON data is pulled into the python script via rest https API call to Orion.   Groups are based on 'Vendor'.  It pulls the 'IPAddress' for hosts field.  The impetus for this script was for network devices.  As such, the 'IPAddress' was chosen over say hostname.  If one wanted to use anisble for servers with DNS using hostnames, replacing the 'IPAdrress' string to 'SysName' should produce that result.  One could also change the 'Vendor' to somethign else like the OS version.  I would recommend downloading the SWQL Studio and look under Orion.Nodes table for more options.~~

Based on the groundwork layed by [cbabs](https://github.com/cbabs/solarwinds-ansible-inv), this dynamic inventory script has been totally rewritten aiming primarily for simplicity. All configuration has been moved to swinds.ini. Apart from the connection details, now it contains:
* **hostfields** which is a plain list of columns to get from the Nodes table. More items may be added as long as the mandatory ones (sysname, ansible_host) remain in the list.
* **groupings** which is a list of 'groupings' along with their respective SWQL queries; these are used to create Ansible groups. More groupings may be added given a correct SWQL query. Solarwinds Database Manager will come as great help for constructing new queries.

## Usage
`solarwinds.py` is a python script that can be executed on any host with python installed. It responds to --list and --host arguments. Variables can be set in the environment to define the behavior of this script, see  VARIABLES below.

`solarwinds.ini` is the configuration file where servername, username and password are contained. This file must be in the same directory as `solarwinds.py`. 

Any suggestions/code to improve would be awesome. 
