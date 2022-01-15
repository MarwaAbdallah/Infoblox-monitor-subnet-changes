# Infoblox-monitor-subnet-changes
Continous monitoring of subnets, using Infoblox' API: wapi

Blog articles **Automate subnet discovery with Infoblox IPAM API**

- [Part 1](https://www.marwaabdallah.com/2021/automate-subnet-discovery-with-infoblox-ipam-api-part-i/)
- [Part 2](https://www.marwaabdallah.com/2021/automate-subnet-discovery-with-infoblox-ipam-api-part-ii/)

## Introduction
### Overview

The purpose of the following scripts is to :

* Query IPAM subnets, and compare the retrieved list to the one from the last time the script executed (ex : day before if executed everyday)
  * If there is a new record (not present in the output of the list previously retrieved, but present in the list that has just been collected), a  new subnet was added
  * If a record that was present in the list obtained previosuly is no longer present, a subnet was decomissioned (not common in practice)
* Email a list of recipients (add emails of desired recipients, such as Network or Security teams, in `smail.py`


## Requirements

python 2.7
Using pip, install packages in requirements.txt

## Security
The server certificate is stored, to avoid MiTM attacks and server spoofing.

TLS v1.2 is used to ensure confidentiality and integrity.


## Scripts
Description of the files:

* config.py contains the configuration needed to authenticate to IPAM, credentials are not shared in the wiki.
* smail.py contains the method that sends email to the appropriate stakeholders.
* DetectNewCorpSubnets.py is the main file.

To launch the script, 
* edit where appropriate (such as smail.py)
* execute `python DetectNewCorpSubnets.py`
