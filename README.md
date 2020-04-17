# Infoblox-monitor-subnet-changes
Continous monitoring of subnets, using Infoblox' API: wapi

## Introduction
### Overview

The purpose of the following scripts is to :

Query IPAM subnets, and compare to what we had the last time it was queried (ex : day before if executed everyday). A change is either a 'subnet added', or a 'subnet deleted' event.

log any detected change. Any new change is appended to the log file gap.csv , along with the date the event has been detected by the script.

When a change happens, email the log file as an attached document, to the security engineering team and the network administrator. As a consequence, the security team will continuously be notified of any change in the corporate environment.

### Flow
![The Flow](https://github.com/MarwaAbdallah/Infoblox-monitor-subnet-changes/blob/master/ipam-flow.JPG)

## Requirements
### IPAM certificate
In an effort to reduce the attack surface, and as opposed to the steps taken to access IPAM via the web browser, the following code requires IPAM to authenticate to the client, using it's certifiate issued by SecureKey.

To do before running the client: save the certificate in a file, in the same folder. The certificate will be passed as a parameter in the GET queries. The current certificate, issued in 2017, is valid until 2027. Once expired, it is important to save the new one.

Note, for demo ease, here the website cert is accepted

### Libraries :
python 2.7


Using pip, install:

pandas
requests
schedule
json
time

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
