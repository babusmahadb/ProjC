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

import pandas as pd
import urllib3 as ur
import base64
import argparse
from getpass import getpass
import logging
import requests
import os
import sys
ur.disable_warnings()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def vol_delete(headers_inc: str):
    """Display Volumes"""
    
    change_chk = input("Enter the Change Details (ex: iochxxxx)")
    vol_data = "C:\\Users\\Administrator.DEMO\\Documents\\ProjC\\test\\Phase1.xlsx"
    vol_df = pd.read_excel(vol_data)
    for ind in vol_df.index:
        vol_name = vol_df['Volume_name'][ind]
        cls_name = vol_df['Cluster'][ind]
        svm_name = vol_df['svm'][ind]
        vol_uuid = vol_df['Volume_uuid'][ind]
        #print(cls_name)
        #print(vol_uuid)
        vol_url = "https://{}/api/storage/volumes/{}".format(cls_name, vol_uuid)
        vol_response = requests.get(vol_url, headers=headers_inc, verify=False)
        vol_json = vol_response.json()
        vol_dt = dict(vol_json)
        #print("helloG",vol_dt)
        state = vol_dt['state']
        if change_chk in vol_name:
            print("Volume is part of the change" + bcolors.OKBLUE + change_chk +bcolors.ENDC+".")
            if state == 'online':
                print("Volume:-" +bcolors.FAIL+vol_name+bcolors.ENDC+"is online, Please Offline the volume before the Deletion" +".")
            elif state == 'offline':
                check = input("Do you want to delete Volume:-   "+ vol_name +" From the Cluster:-  "+cls_name+"(Y/N)")
                if check == 'Y' or  check == 'y':
                    voldel="https://{}/api/storage/volumes/{}?return_timeout=20".format(cls_name, vol_uuid)
                    unres = requests.delete(voldel, headers=headers_inc, verify=False)
                    vdren = unres.json()
                    vd_j=vdren['job']
                    vd_uid=vd_j['uuid']
                    vd_url="https://{}//api/cluster/jobs/{}".format(cls_name, vd_uid)
                    vdes=requests.get(vd_url, headers=headers_inc,verify=False)
                    vdjson=vdes.json()
                    vdjst=vdjson['state']
                    if "success" in vdjst:
                        print ("volume:-" + bcolors.OKGREEN + vol_name  + " has been deleted from Cluster: "+cls_name+bcolors.ENDC+".")
                    elif "running" in vdjst:
                        print ("Job is still running")
                    else:   
                        print ("Job Failed")
                else:
                    print("Your Input is : N" +" volume:-" + bcolors.OKGREEN + vol_name  + " has Not been deleted  from Cluster: "+cls_name+bcolors.ENDC+".")
        else:
            print(bcolors.OKCYAN+vol_name+bcolors.ENDC+" Volume is not Part of Change:- "+change_chk +bcolors.OKCYAN+" Volume is not Deleted."+bcolors.ENDC)
  
def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will list volumes in a SVM")
      
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
    os.system('color')
    vol_delete(headers)