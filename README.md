# Infoblox-monitor-subnet-changes
Continous monitoring of subnets, using Infoblox' API: wapi

Blog articles **Automate subnet discovery with Infoblox IPAM API**

- [Part 1](https://www.marwaabdallah.com/2021/automate-subnet-discovery-with-infoblox-ipam-api-part-i/)
- [Part 2](https://www.marwaabdallah.com/2021/automate-subnet-discovery-with-infoblox-ipam-api-part-ii/)

## Introduction
### Overview

The purpose of the following scripts is to :

Query IPAM subnets, and compare to what we had the last time it was queried (ex : day before if executed everyday). A change is either a 'subnet added', or a 'subnet deleted' event.

log any detected change, email stakeholders (security team, network team.....)


## Requirements

python 2.7
Using pip, install packages in requirements.txt

## Security
Server certificate stored, to avoid MiTM attacks and server spoofing
TLS v1.2 to ensure confidentiality and integrity


## Scripts
Description of the files:

* config.py contains the configuration needed to authenticate to IPAM, credentials are not shared in the wiki.
* smail.py contains the method that sends email to the appropriate stakeholders.
* DetectNewCorpSubnets.py is the main file.

To launch the script, edit where appropriate (such as smail.py):


python DetectNewCorpSubnets.py
