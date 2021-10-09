#!/usr/bin/python
# Import the required Python modules.
import requests
import numpy as np
import json
import time
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
requests.packages.urllib3.disable_warnings()
from itertools import tee
import pandas as pd
import schedule
import config
import smail
import sys
import os


'''
The following code :
    1- Connects a user to Infoblox IPAM's wapi
    2- Query for specific subnets, using IPAM attributes, and extensive
    attributes that are passed as URL parameters.
        For the subnets from Site='Chicago',
        query is: https://<IPAM URI>/wapi/v2.7/*Site:=Chicago
        More wapi Documentation:  https://ipam.illinois.edu/wapidoc/index.html


'''
def createCsvOutput(df):
    ''' Store the result in a csv file, it will be loaded next time script is run
    '''
    #its a good idea to specify an absolute path where to store the file and retrieve
    #from in main(), specially is the execution is croned, absolute path needed
    df.to_csv('corporate_subnet.csv', sep=',', encoding='utf-8',index=False)

def writeGap(df):
    '''Send an email
	'''
    smail.sendemail(df)

def convertColumnType(dfnew, dfprevious):
    for x in dfprevious.columns:
        dfnew[x]=dfnew[x].astype(df1[x].dtypes.name)
    return dfnew

def cleanData(df):
    ''' Handling NaN values.
    TO DO: It works for empty values, but need to replace 'n/a'
    Strings with an empty string
    '''
    df = df.replace(np.nan, '', regex=True)
    return df

def compareDataframes(new_table, previous_table):
    ''' compare newly created list of subnet, with the one that was stored previously. The gap is computed.
        Gap: every row in dfnew, for which the subnet value is not present in dfprevious
        saves the new result, erasing the previous one.
    '''

    result = pd.merge(new_table, previous_table, on='network',how='outer', indicator=True)
    removed_subnets= result[result['_merge']=='right_only'][result.columns]
    added_subnets = result[result['_merge']=='left_only'][result.columns]

    added_subnets.rename(columns={'Site_x': 'Site', 'VLAN_x': 'VLAN'}, inplace=True)
    removed_subnets.rename(columns={"Site_y": 'Site', 'VLAN_y': 'VLAN'}, inplace=True)
    added_subnets=added_subnets[['VLAN','network','Site']]
    removed_subnets=removed_subnets[['VLAN','network','Site']]

    added_subnets['event']='added'
    removed_subnets['event']='removed'

    diff=concatTwoDf(added_subnets,removed_subnets)
    if not diff.empty:
        writeGap(diff)


def extractNetworksFromNetworkContainers(df, url, cookie):
    '''
     Input: 1 Network container, represented as DataFrame,
            contains multiple subnets.
     Output: Each network in the Network Container, listed in a datafrane
     '''
    dftmp = pd.DataFrame()
    for net in df['network']:
        url_param="network?network_container=" +str(net)
        dftmp=dftmp.append(request(url,url_param, cookie))

    return dftmp


def checkRequestError(r):
    tmp=1
    if r.status_code != requests.codes.ok:
        smail.autherror(str(r.status_code), str(r.text))
        tmp=0
    return tmp


def setcookie(url,id,pw): # 1st connection jus to set the connection cookie

    r = requests.get(url + 'networkview',
                     auth=(id, pw),
                     verify=False)
    auth=checkRequestError(r) # if auth failure, return 0
    if auth!=0:
        ibapauth_cookie = r.cookies['ibapauth'] # Save the authentication cookie for use in subsequent requests.
        request_cookie = {'ibapauth': ibapauth_cookie}
        return request_cookie
    else:
        return 0


def request(url, url_param, request_cookies):
    '''
    Input: url_param: The GET parameter specifying the query;
            request_cookie: cookie for the session, none if FIRST call ;
            desc: description about the query (specific network or device...)
    Output: DataFrame containing the structured result
    '''
    r = requests.get(url + url_param,
                      cookies=request_cookies,
                     verify=False)
    checkRequestError(r)
    results = r.json()
    tmp= json.dumps(results, indent=4, sort_keys=True)
    df = pd.read_json(tmp, orient='columns')

    return df

def fromJsontoDf(df):
    '''
    input: dataframe['extattrs'], column containing Json data (columns)
    output: dataframe without messy nested json
    '''
    if len(df)!=0:
        tmp = (pd.concat({i: pd.DataFrame(x) for i, x in df.pop('extattrs').items()})
         .reset_index(level=1, drop=True)
         .join(df)
         .reset_index(drop=True))
        tmp=pd.DataFrame(tmp)
        return tmp
    pass


def concatTwoDf(dfa, dfb):
    '''
    In IPAM, corporate environment is composed of 2 smart folders, created and
    monitored by network admin. Once retrieved, this function concatenate them.
    '''
    frames = [dfa, dfb]
    df=pd.concat(frames,ignore_index=True)
    return df


def querySubnets(url, url_param,request_cookies):
    '''For each call from main, request IPAM for network and networkcontainer and concat them.'''
    network="network?"+url_param
    network_container="networkcontainer?"+url_param
    df= request(url,network, request_cookies)
    dfContainer=request(url,network_container, request_cookies)
    # the Json output is saved in a pandas dataframe
    df=fromJsontoDf(df)
    dfContainer=fromJsontoDf(dfContainer)
    # a container is a set of subnets. in the if statement,
    #  we extract each subnet composing the container.
    if dfContainer is not None:
        dfContainerSubnets= extractNetworksFromNetworkContainers(dfContainer, url, request_cookies)
        df=concatTwoDf(df, dfContainerSubnets)
    return df

def sessionInit(url):
    ''' authenticate once, then keep session cookie'''
    id = config.username # Userid with WAPI access
    pw = config.password # Prompt for the API user password.
    request_cookies=setcookie(url, id, pw) # a First connexion, just to set the cookie
    return request_cookies

def main():

    url = config.url
    request_cookies=sessionInit(url)
    if request_cookies!=0:
        network=querySubnets(url, "_return_fields=network,extattrs",request_cookies)
        network=network[['VLAN','network','Site']] # You can add as many IPAM column as you want
        #drop duplicates on column that serves as Merge sort_keys
        #because when network containers are used, subnets can be represented
        #in 2 distinct rows.
        network.drop_duplicates(subset=['network'],keep='first',inplace=True)

        exists = os.path.isfile('corporate_subnet.csv')
        if exists:
            previous_result=pd.read_csv('corporate_subnet.csv')
            previous_result=previous_result[['VLAN','network','Site']]
            previous_result.drop_duplicates(subset=['network'],keep='first',inplace=True)
            compareDataframes(network, previous_result)
        else:
        #1st execution serves to store for the 1st time, to be used in next executions of the script
        createCsvOutput(network)
    else:
        print "auth problem" # this is printed in the console additionally to sending an email

main()
