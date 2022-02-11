  
#! /usr/bin/env python3

"""
ONTAP REST API Sample Scripts
This script was developed by NetApp to help demonstrate NetApp
technologies.  This script is not officially supported as a
standard NetApp product.
Purpose: Script to list volumes using ONTAP REST API.
Usage: list_volumes.py [-h] -c CLUSTER -vs SVM_NAME [-u API_USER]
                       [-p API_PASS]
Copyright (c) 2020 NetApp, Inc. All Rights Reserved.
Licensed under the BSD 3-Clause “New” or Revised” License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
"""
import base64
import argparse
from getpass import getpass
import logging
import texttable as tt
import requests
import urllib3 as ur
ur.disable_warnings()


def get_volumes(cluster: str, svm_name: str, headers_inc: str):
    """Get Volumes"""
    url = "https://{}/api/storage/volumes/?svm.name={}".format(cluster, svm_name)
    response = requests.get(url, headers=headers_inc, verify=False)
    return response.json()


def disp_vol(cluster: str, svm_name: str, headers_inc: str):
    """Display Volumes"""
    ctr = 0
    tmp = dict(get_volumes(cluster, svm_name, headers_inc))
    vols = tmp['records']
    tab = tt.Texttable()
    header = (['Volume name', 'Connected_Clients'])
    tab.header(header)
    tab.set_cols_width([18,150])
    tab.set_cols_align(['c','c'])
    for volumelist in vols:
        nfl=dict(volumelist)
        #print (nfl)
        ven=nfl['name']
        #print (ven)
        nc="https://{}/api/private/cli/nfs/connected-clients/?volume={}".format(cluster,ven)
        response = requests.get(nc, headers=headers_inc, verify=False)
        vuid12 = response.json()
        #print(vuid12)
        conn=dict(vuid12)
        conn1=conn['records']
        #print (conn1)
        c2=0
        tmp2=[]
        for con2 in conn1:
            c2=c2+1
            tmp=dict(con2)
            tmp1=tmp['client_ip']
            tmp2.append(tmp1)
            #print(c2)
            #print(tmp2)            
    #for i in cd:
        #ctr = ctr + 1
        #To Fetch SVM NAme
        #cs1 = i.get('svm')
        #csvs=dict(cs1)
        #csvsn=csvs['name']
        #csn=i['name']
        #print(csn)
        #csp=i['path']
        #csv1 = i.get('volume')
        #csvs=dict(csv1)
        #csvn=csvs['name']
        tab.add_row([ven,tmp2])
        tab.set_cols_width([18,150])
        tab.set_cols_align(['c','c'])
        
        
    setdisplay = tab.draw()
    print(setdisplay)


def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will list volumes in a SVM")
    parser.add_argument(
        "-c", "--cluster", required=True, help="API server IP:port details")
    parser.add_argument(
        "-vs", "--svm_name", required=True, help="SVM Name"
    )
    parser.add_argument(
        "-u",
        "--api_user",
        default="admin",
        help="API Username")
    parser.add_argument("-p", "--api_pass", help="API Password")
    parsed_args = parser.parse_args()

    # collect the password without echo if not already provided
    if not parsed_args.api_pass:
        parsed_args.api_pass = getpass()

    return parsed_args


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)5s] [%(module)s:%(lineno)s] %(message)s",
    )
    ARGS = parse_args()
    BASE_64_STRING = base64.encodebytes(
        ('%s:%s' %
         (ARGS.api_user, ARGS.api_pass)).encode()).decode().replace('\n', '')

    headers = {
        'authorization': "Basic %s" % BASE_64_STRING,
        'content-type': "application/json",
        'accept': "application/json"
    }

    disp_vol(ARGS.cluster, ARGS.svm_name, headers)
