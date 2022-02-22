
"""
ONTAP REST API Scripts

Purpose: Script to perform phase1 volume decommission using ONTAP REST API.

Usage: phase1_volumes_decom.py [-h] [-u API_USER] [-p API_PASS]
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


def sm_quiesce_break(cluster: str,smr_uuid: str, headers_inc: str):
    
    """ Pause and break the snapmirror relationship """
    dataobj = {}
    sm_url = "https://{}/api/snapmirror/relationships/{}".format(cluster, smr_uuid)
    response = requests.get(sm_url, headers=headers_inc, verify=False)
    sm_json = response.json()

    sm_dt = dict(sm_json)
    #print(cluster)
    #smr_rd = smr_dt['records']
    
    sm_state = sm_dt['state']
    #print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" of Cluster/Vserver :"+bcolors.HEADER +cls_name+"/"+svm_name+bcolors.ENDC +" SnapMirror relationship is in "+bcolors.WARNING +sm_state+bcolors.ENDC +" state.")
    #print()
        
    if sm_state == "snapmirrored":
        pau_state = input("Do you to want pause the snapmirror relationship?(y/n):")
        if pau_state == 'y':
           dataobj['state'] = 'paused'
           url = "https://{}/api/snapmirror/relationships/{}?return_timeout=30".format(cluster, smr_uuid)   
           try:
               response = requests.patch(url, headers=headers_inc, json=dataobj, verify=False)
           except requests.exceptions.HTTPError as err:
               print(str(err))
               sys.exit(1)
           except requests.exceptions.RequestException as err:
               print(str(err))
               sys.exit(1)
           url_text = response.json()
           #print(url_text)
           if 'error' in url_text:
               print(url_text)
               sys.exit(1)
           else:
               stat_dt = dict(url_text)
               stat_job = stat_dt['job']
               job_id = stat_job['uuid']
               
               status_url = "https://{}/api/cluster/jobs/{}".format(cluster, job_id)
               response = requests.get(status_url, headers=headers_inc, verify=False)
               status_json = response.json()
               
               job = dict(status_json)
               job_status = job['state']
               
               if job_status == "success":
                   print("Pausing SnapMirror relationship of volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" of Cluster/Vserver :"+bcolors.HEADER +cls_name+"/"+svm_name+bcolors.ENDC +" is "+bcolors.OKGREEN +"Successful"+ bcolors.ENDC +".") 
               
        else:
            return
            
        brk_state = input("Do you to want break the snapmirror relationship?(y/n):")
        if brk_state == 'y':
           dataobj['state'] = 'broken_off'
           url = "https://{}/api/snapmirror/relationships/{}?return_timeout=30".format(cluster, smr_uuid)   
           try:
               response = requests.patch(url, headers=headers_inc, json=dataobj, verify=False)
           except requests.exceptions.HTTPError as err:
               print(str(err))
               sys.exit(1)
           except requests.exceptions.RequestException as err:
               print(str(err))
               sys.exit(1)
           url_text = response.json()
           #print(url_text)
           if 'error' in url_text:
               print(url_text)
               sys.exit(1)
           else:
               stat_dt = dict(url_text)
               stat_job = stat_dt['job']
               job_id = stat_job['uuid']
               
               status_url = "https://{}/api/cluster/jobs/{}".format(cluster, job_id)
               response = requests.get(status_url, headers=headers_inc, verify=False)
               status_json = response.json()
               
               job = dict(status_json)
               job_status = job['state']
               
               if job_status == "success":
                   print("Breaking SnapMirror relationship of volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" of Cluster/Vserver :"+bcolors.HEADER +cls_name+"/"+svm_name+bcolors.ENDC +" is "+bcolors.OKGREEN +"Successful"+ bcolors.ENDC +".") 
        else:
            return
    
    elif sm_state == "paused":
        
        brk_state = input("Do you to want break the snapmirror relationship?(y/n):")
        if brk_state == 'y':
           dataobj['state'] = 'broken_off'
           url = "https://{}/api/snapmirror/relationships/{}?return_timeout=30".format(cluster, smr_uuid)   
           try:
               response = requests.patch(url, headers=headers_inc, json=dataobj, verify=False)
           except requests.exceptions.HTTPError as err:
               print(str(err))
               sys.exit(1)
           except requests.exceptions.RequestException as err:
               print(str(err))
               sys.exit(1)
           url_text = response.json()
           #print(url_text)
           if 'error' in url_text:
               print(url_text)
               sys.exit(1)
           else:
               stat_dt = dict(url_text)
               stat_job = stat_dt['job']
               job_id = stat_job['uuid']
               
               status_url = "https://{}/api/cluster/jobs/{}".format(cluster, job_id)
               response = requests.get(status_url, headers=headers_inc, verify=False)
               status_json = response.json()
               
               job = dict(status_json)
               job_status = job['state']
               
               if job_status == "success":
                   print("Breaking SnapMirror relationship of volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" of Cluster/Vserver :"+bcolors.HEADER +cls_name+"/"+svm_name+bcolors.ENDC +" is "+bcolors.OKGREEN +"Successful"+ bcolors.ENDC +".") 
        else:
            return
    else:
        print()
        
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
  

def cifs_delete(cluster: str,vol_name: str,svm_name: str,cifs_list: str, headers_inc: str):
    
    """ Delete cifs shares associated with volume """
    
    svm_url="https://{}/api/svm/svms?name={}".format(cluster,svm_name)
    response = requests.get(svm_url, headers=headers_inc, verify=False)
    svm_json = response.json()
    
    svm_dt = dict(svm_json)
    svm_rd = svm_dt['records']
    
    for i in svm_rd:
        svm_uuid = i['uuid']
    
    clist = cifs_list.replace("'","").strip('][').split(', ')
    
    for share in clist:
        
        if "root" in share:
            print("cifs share "+bcolors.OKBLUE +share+bcolors.ENDC +" is Root Volume")
        else:
            print()
            check = input("Do you want to delete cifs share named:"+bcolors.OKBLUE+share+bcolors.ENDC+"(y/n)")
            if check =='y':
                cifs_del_url = "https://{}/api/protocols/cifs/shares/{}/{}?return_timeout=5".format(cluster,svm_uuid,share)
                                
                try:
                    response = requests.delete(cifs_del_url, headers=headers_inc, verify=False)
                except requests.exceptions.HTTPError as err:
                    print(str(err))
                    sys.exit(1)
                except requests.exceptions.RequestException as err:
                    print(str(err))
                    sys.exit(1)
                cifs_del_json = response.json()
                #print(cifs_del_json)
                if 'error' in cifs_del_json:
                    print(cifs_del_json)
                    sys.exit(1)
                else:
                                        
                    if cifs_del_json == {}:
                        print("Deletion of Share name "+bcolors.OKBLUE +share+bcolors.ENDC +" of Volume:"+bcolors.OKBLUE +vol_name+bcolors.ENDC +" is "+bcolors.OKGREEN +"Successful"+ bcolors.ENDC +".") 
                        
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
    
    vol_data = "C:\\Users\\Administrator.DEMO\\Documents\\GitHub\\test\\VolumeDetails.xlsx"
           
    vol_df = pd.read_excel(vol_data)
    #print(vol_df.T)
   
    for ind in vol_df.index:
        
        vol_name = vol_df['Volume name'][ind]
        cls_name = vol_df['Cluster Name'][ind]
        svm_name = vol_df['Vserver Name'][ind]
        
        print("############################"+bcolors.OKCYAN+vol_name+bcolors.ENDC +"########################################################")
        print()
       # print(bcolors.WARNING+ vol_name +bcolors.ENDC)
        cifs_check = vol_df['No. of CIFS Shares'][ind]
        
        if cifs_check!=0:
            cifs_list = vol_df['CIFS Shares List'][ind]
            print("Volume "+bcolors.OKBLUE+vol_name+bcolors.ENDC +" has CIFS share(s) "+bcolors.OKBLUE+cifs_list+bcolors.ENDC +".")
            cifs_delete(cls_name,vol_name,svm_name,cifs_list, headers)
        else:
            print("Volume "+bcolors.OKBLUE+vol_name+bcolors.ENDC +" not configured for CIFS.")
            
        print()    
        snpmir_check = vol_df['SnapMirror(Y/N)'][ind]
        if snpmir_check == 'Yes':
            #print()
            tgt_cls = vol_df['Target Cluster'][ind]
            smr_uuid = vol_df['SnapMirror UUID'][ind]
            sm_quiesce_break(tgt_cls,smr_uuid, headers)
        else:
            #print()
            print("Volume "+bcolors.OKBLUE+vol_name+bcolors.ENDC +" of Cluster/Vserver :"+bcolors.HEADER+cls_name+"/"+svm_name+bcolors.ENDC +" does not have snapmirror configured")
            
        print()    
        #print("###########################################################################################################################")    
    #print(vol_df.loc[vol_df['SnapMirror(Y/N)']])
    ''#print(vol_df.T)

    #m_quiesce_break(cluster,smr_uuid, headers)
    
    #for row in vol_df:
    #    #print(vol_df['SnapMirror(Y/N)'])
    #    if vol_df['SnapMirror(Y/N)'] == "Yes":    
    #       print("UUID")
    #