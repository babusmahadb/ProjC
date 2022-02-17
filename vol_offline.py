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


def vol_ren(cluster: str, svm_name: str, headers_inc: str):
    """Display Volumes"""
    ctr = 0
    tmp = dict(get_volumes(cluster, svm_name, headers_inc))
    vols = tmp['records']
    tab = tt.Texttable()
    header = (['Volume name', 'Volume UUID', 'Vserver Name', 'Vol State', ' Vol Type','IS Volume Protected?','Snapmirror UUID',"Dest_Clus"])
    tab.header(header)
    #tab.set_cols_width([18,50,25,15,15,15,50,15])
    tab.set_cols_width([10,40,15,10,10,10,40,10])
    tab.set_cols_align(['c','c','c','c','c','c','c','c'])
    for volumelist in vols:
        ctr = ctr + 1
        vol = volumelist['name']
        uuid = volumelist['uuid']
        #nas_url = "https://{}/api/storage/volumes?uuid={}&fields=nas.path".format(cluster, uuid)
        #response = requests.get(nas_url, headers=headers_inc, verify=False)
        #nas_json = response.json()
        #
        #nas_dt = dict(nas_json)
        #print("nas_dt",nas_dt)
        dataobj = {}
        print ("Current Volume",vol)
        nambool = input("Would you like to offline the volume name (y/n):- ")
        if nambool == 'y':
            #volname = input("Enter the name of the volume that needs to be modified:- ")
            #dataobj = {}
            #dataobj['name'] = volname
            dataobj['state'] = "offline"
            print("dataobj",dataobj)
            unurl="https://{}/api/storage/volumes/{}".format(cluster, uuid)
            unres = requests.patch(unurl, headers=headers_inc, json=dataobj, verify=False)
            vren = unres.json()
            print("vren",vren)
  


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

    vol_ren(ARGS.cluster, ARGS.svm_name, headers)