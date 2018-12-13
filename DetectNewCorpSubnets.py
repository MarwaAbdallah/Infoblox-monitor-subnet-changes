!/usr/bin/python
# Import the required Python modules.
import requests
import numpy as np
import json
import time
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
requests.packages.urllib3.disable_warnings()
import pandas as pd
import schedule
import config
import smail
import sys
 
def createCsvOutput(df):
    df.drop_duplicates(subset=['network'],keep='first',inplace=True)
    df.to_csv('corporate_subnet.csv', sep=',', encoding='utf-8',index=False)
 
def writeGap(df):
    ''' Append the gap to gap.csv, a file containing all previous gap
        and email the generated file to the stackholders
    '''
    df['time']=time.ctime()
    df = df[['VLAN','network','Site','event','time']]
    with open('gap.csv', 'a') as f:
             (df).to_csv(f, header=False)
    smail.sendemail()
 
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
 
def compareDataframes(dfnew, dfprevious):
    ''' compare newly created list of subnet, with the one that was stored previously. The gap is computed.
        Gap: every row in dfnew, for which the subnet value is not present in dfprevious
    '''
 
    df=cleanData(dfnew)
    df = pd.merge(dfnew, dfprevious, how='outer', indicator=True)
    added_subnets = df[df['_merge']=='left_only'][dfnew.columns]
    removed_subnets= df[df['_merge']=='right_only'][dfprevious.columns]
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
    if r.status_code != requests.codes.ok:
        print (r.text)
        exit_msg = 'Error {} finding network views: {}'
        sys.exit(exit_msg.format(r.status_code, r.reason))
 
def setcookie(url,id,pw): # 1st connection jus to set the connection cookie
 
    r = requests.get(url + 'networkview',
                     auth=(id, pw),
                     verify='ipamCert.pem')
    checkRequestError(r)
    ibapauth_cookie = r.cookies['ibapauth'] # Save the authentication cookie for use in subsequent requests.
    request_cookie = {'ibapauth': ibapauth_cookie}
    return request_cookie
 
 
def request(url, url_param, request_cookies):
    '''
    Input: url_param: The GET parameter specifying the query;
            request_cookie: cookie for the session, none if FIRST call ;
            desc: description about the query (specific network or device...)
    Output: DataFrame containing the structured result
    '''
    r = requests.get(url + url_param,
                      cookies=request_cookies,
                     verify='ipamCert.pem')
    checkRequestError(r)
    results = r.json()
    tmp= json.dumps(results, indent=4, sort_keys=True)
    df = pd.read_json(tmp, orient='columns')
 
    return df
 
def fromJsontoDf(df):
    '''
    input: dataframe['extattrs'], column containing Json data (columns)
    output:
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
    print id
    pw = config.password # Prompt for the API user password.
    request_cookies=setcookie(url, id, pw) # a First connexion, just to set the cookie
    return request_cookies
 
def main():
    previous_result=pd.read_csv('corporate_subnet.csv')
    url = config.url
 
    request_cookies=sessionInit(url)
    corp=querySubnets(url, "*Environment:=Corporate&_return_fields=network,extattrs",request_cookies)
    syst_Well4=querySubnets(url, "*Environment:=Development*Site:=Quebec&_return_fields=network,extattrs",request_cookies)
    syst_YM=querySubnets(url, "*Environment:=Development&*Site:=Quebec&_return_fields=network,extattrs",request_cookies)
    syst=concatTwoDf(syst_Well4, syst_YM)
    network=concatTwoDf(corp, syst)
 
    createCsvOutput(network)
    # before comparing previous to new corporate subnets, ensure consustency in column types
    for x in previous_result.columns:
        network[x]=network[x].astype(previous_result[x].dtypes.name)
 
    compareDataframes(network, previous_result)
    createCsvOutput(network)
 
 
schedule.every().wednesday.at("13:15").do(main)
while 1:
    schedule.run_pending()
    time.sleep(1)
