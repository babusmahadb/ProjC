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
    url = "https://{}/api/storage/volumes/?svm.name={}&fields=*".format(cluster, svm_name)
    response = requests.get(url, headers=headers_inc, verify=False)
    return response.json()

######new line

def vol_delete(cluster: str, svm_name: str, headers_inc: str):
    """Display Volumes"""
    ctr = 0
    tmp = dict(get_volumes(cluster, svm_name, headers_inc))
    vols = tmp['records']
    vol_in = input("Enter volume to Delete the volume name :- ")
    for volumelist in vols:
        vol = volumelist['name']
        if vol_in == vol: 
            uuid = volumelist['uuid']
            st = volumelist['state']
            volin = input("Are you Sure to delete (y/n):- ")
            if volin == 'y':
                if st == 'online':
                    print("Volume:-", vol_in, "is online, Please Offline the volume before the Deletion")
                elif st == 'offline':
                    voldel="https://{}/api/storage/volumes/{}?return_timeout=20".format(cluster, uuid)
                    unres = requests.delete(voldel, headers=headers_inc, verify=False)
                    vdren = unres.json()
                    vd_j=vdren['job']
                    vd_uid=vd_j['uuid']
                    vd_url="https://{}//api/cluster/jobs/{}".format(cluster, vd_uid)
                    vdes=requests.get(vd_url, headers=headers_inc,verify=False)
                    vdjson=vdes.json()
                    vdjst=vdjson['state']
                    if "success" in vdjst:
                        print ("volume:-",vol,"has been deleted from Cluster: ",cluster)
                    elif "running" in vdjst:
                        print ("Job is still running")
                    else:   
                        print ("Job Failed")
                    
                    
  


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

    vol_delete(ARGS.cluster, ARGS.svm_name, headers)