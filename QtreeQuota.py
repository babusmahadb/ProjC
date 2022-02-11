  
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
    header = (['Volume name', 'Qtree'])
    tab.header(header)
    tab.set_cols_width([18,50])
    tab.set_cols_align(['c','c'])
    qr="https://{}/api/storage/qtrees/".format(cluster)
    response = requests.get(qr, headers=headers_inc, verify=False)
    qres = response.json()
    qres2=dict(qres)
    qres3=qres2['records']
    #print (qres3)
    #q2 contains qtree name
    qtree2=[]
    for i in qres3:
        q1=dict(i)
        q2=q1['name']
        q3=q1['volume']
        q4=dict(q3)
        q5=q4['name']
        vid="https://{}/api/storage/volumes?name={}".format(cluster,q5)
        response = requests.get(vid, headers=headers_inc, verify=False)
        vol = response.json()
        vol1=dict(vol)
        vol3=vol1['records']
        #vol2 contains vol uuid.
        for j in vol3:
            volt=dict(j)
            volt2= volt['uuid']
        qid="https://{}/api/storage/quota/reports/{}".format(cluster,volt2)
        response = requests.get(qid, headers=headers_inc, verify=False)
        vol2q = response.json()
        qti=dict(vol2q)
        qtr=qti['records']
        qtri=qti['num_records']
        qtreelist=[]
        if qtri == 0:
            qw=q2+" No Quota"
            qtreelist.append(qw)
            tab.add_row([q5,qw])
        else: 
            kidlist=[]
            for k in qtr:
                id=dict(k)
                kid=id['index']
                #print("XXXXXXXX",kid)
                qu1="https://{}/api/storage/quota/reports/{}/{}".format(cluster,volt2,kid)
                response = requests.get(qu1, headers=headers_inc, verify=False)
                quores= response.json()
                quores2=dict(quores)
                quos=quores['space']
                quost=dict(quos)
                hl=quost['hard_limit']
                h2=(((int(hl)/1024)/1024)/1024)
            if q2 == "":
                tab.add_row([q5,q2])

            else:
                h3=str(h2)
                tmpt=q2+h3
                tab.add_row([q5,tmpt])
        tab.set_cols_width([18,50])
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
