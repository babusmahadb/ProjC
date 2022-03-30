
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


def get_res(cluster: str, url: str, dataobj: str, headers_inc: str):

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
    
    
    return url_text, job_status
    
def sm_dst_del(tgt_cluster: str,smr_uuid: str, headers_inc: str):  

    """ deletion of snapmirror replationship only on destionation cluster """
    
    del_state = input("Do you to want delete the snapmirror relationship only on destionation cluster "+bcolors.HEADER +tgt_cluster+bcolors.ENDC +"?(y/n):")
    if del_state == 'y':
       
       url = "https://{}/api/snapmirror/relationships/{}/?destination_only=true&return_timeout=30".format(tgt_cluster, smr_uuid)   
       try:
            response = requests.delete(url, headers=headers_inc, verify=False)
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
           
           status_url = "https://{}/api/cluster/jobs/{}".format(tgt_cluster, job_id)
           response = requests.get(status_url, headers=headers_inc, verify=False)
           status_json = response.json()
           
           job = dict(status_json)
           job_status = job['state']
       
                    
       if job_status == "success":
            print(""+bcolors.WARNING +"Deletion"+bcolors.ENDC +" of SnapMirror relationship on destionation cluster "+bcolors.OKBLUE +tgt_cluster+bcolors.ENDC +" is "+bcolors.OKGREEN +"Successful"+ bcolors.ENDC +".") 
            print()
       elif job_status == "running":
            print("Job Status:- ",job_status)
            print("Job still running ")
       else:
            print("Job Failed",job_status)
    else:
        return
    
def sm_src_rel(src_cluster: str,smr_uuid: str, headers_inc: str): 

    """ release of snapmirror replationship on source cluster (source_info_only).This does not delete the common Snapshot copies between the source and destination. """
    
    rel_state = input("Do you to want release the snapmirror relationship on source cluster "+bcolors.HEADER +cls_name+bcolors.ENDC +"?(y/n):")
    if rel_state == 'y':
       
       url = "https://{}/api/snapmirror/relationships/{}/?source_info_only=true&return_timeout=30".format(src_cluster, smr_uuid)   
       try:
            response = requests.delete(url, headers=headers_inc, verify=False)
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
           
           status_url = "https://{}/api/cluster/jobs/{}".format(src_cluster, job_id)
           response = requests.get(status_url, headers=headers_inc, verify=False)
           status_json = response.json()
           
           job = dict(status_json)
           job_status = job['state']
       
                    
       if job_status == "success":
            print(""+bcolors.WARNING +"Release"+bcolors.ENDC +" of SnapMirror relationship on Source cluster "+bcolors.OKBLUE +src_cluster+bcolors.ENDC +" is "+bcolors.OKGREEN +"Successful"+ bcolors.ENDC +".") 
       elif job_status == "running":
            print("Job Status :- ",job_status)
            print("Job still running ")
       else:
            print("Job Failed",job_status)
    else:
        return

def sm_quiesce_break(tgt_cluster: str,smr_uuid: str, headers_inc: str):
    
    """ Pause and break the snapmirror relationship """
    dataobj = {}
    sm_url = "https://{}/api/snapmirror/relationships/{}".format(tgt_cluster, smr_uuid)
    response = requests.get(sm_url, headers=headers_inc, verify=False)
    sm_json = response.json()

    sm_dt = dict(sm_json)
    #print(cluster)
    #smr_rd = smr_dt['records']
    
    sm_state = sm_dt['state']
    #print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" of Cluster/Vserver :"+bcolors.HEADER +cls_name+"/"+svm_name+bcolors.ENDC +" SnapMirror relationship is in "+bcolors.WARNING +sm_state+bcolors.ENDC +" state.")
    print()
        
    if sm_state == "snapmirrored":
        pau_state = input("Do you to want pause the snapmirror relationship?(y/n):")
        if pau_state == 'y':
           dataobj['state'] = 'paused'
           url = "https://{}/api/snapmirror/relationships/{}?return_timeout=30".format(tgt_cluster, smr_uuid)   
           result = get_res(tgt_cluster,url,dataobj,headers_inc)
               
           if result[1] == "success":
               print(""+bcolors.WARNING +"Pausing"+bcolors.ENDC +" SnapMirror relationship of volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" of Cluster/Vserver :"+bcolors.HEADER +cls_name+"/"+svm_name+bcolors.ENDC +" is "+bcolors.OKGREEN +"Successful"+ bcolors.ENDC +".") 
               print()         
           else:
               print("response",result[0])
        else:
            return
            
        brk_state = input("Do you to want break the snapmirror relationship?(y/n):")
        if brk_state == 'y':
           dataobj['state'] = 'broken_off'
           url = "https://{}/api/snapmirror/relationships/{}?return_timeout=30".format(tgt_cluster, smr_uuid)   
           result = get_res(tgt_cluster,url,dataobj,headers_inc)
               
           if result[1] == "success":
                print(""+bcolors.WARNING +"Breaking"+bcolors.ENDC +" SnapMirror relationship of volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" of Cluster/Vserver :"+bcolors.HEADER +cls_name+"/"+svm_name+bcolors.ENDC +" is "+bcolors.OKGREEN +"Successful"+ bcolors.ENDC +".") 
                print()
           else:
               print("response",result[0])
        else:
            return
            
        sm_dst_del(tgt_cluster,smr_uuid,headers_inc)
        
        sm_src_rel(cls_name,smr_uuid,headers_inc)
    
    elif sm_state == "paused":
        
        brk_state = input("Do you to want break the snapmirror relationship?(y/n):")
        if brk_state == 'y':
           dataobj['state'] = 'broken_off'
           url = "https://{}/api/snapmirror/relationships/{}?return_timeout=30".format(tgt_cluster, smr_uuid)   
           result = get_res(tgt_cluster,url,dataobj,headers_inc)
               
           if result[1] == "success":
                   print("Breaking SnapMirror relationship of volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" of Cluster/Vserver :"+bcolors.HEADER +cls_name+"/"+svm_name+bcolors.ENDC +" is "+bcolors.OKGREEN +"Successful"+ bcolors.ENDC +".") 
                   print()
           else:
               print("response",result[0])
        else:
            return
            
        sm_dst_del(tgt_cluster,smr_uuid,headers_inc)
        
        sm_src_rel(cls_name,smr_uuid,headers_inc)
        
    elif sm_state == "broken_off":
        
        sm_dst_del(tgt_cluster,smr_uuid,headers_inc)
        
        sm_src_rel(cls_name,smr_uuid,headers_inc)
        
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
 

def vol_unmnt(cluster: str, vol_name: str, vol_uuid: str, headers_inc: str):
    
    """ Unmount Volumes """
    print()
    dataobj = {}
    if "root" in vol_name:
        print("Volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" is Root Volume")
    else:    
        #print("Current Volume: "+bcolors.OKBLUE +vol_name+bcolors.ENDC +"") 
        mnt = input("Would you like to Unmount the volume (y/n): ")
        if mnt == 'y':
            mnt1 = input("Are you Sure to Unmount? (y/n):")
            if mnt1 == 'y':
                path = input("Press Enter to Unmount")
                nasjson = {
                    "path": path,
                    }
                dataobj['nas'] = nasjson  
                jpath_url = "https://{}/api/storage/volumes/{}?return_timeout=15" .format(cluster, vol_uuid)
                result = get_res(cluster,jpath_url,dataobj,headers_inc)
               
                if result[1] == "success":
                    print("Volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" unmounted :"+bcolors.OKGREEN +"Successful"+ bcolors.ENDC +".")
                    print()
                else:
                    print("respone",result[0])
                    
def vol_rename(cluster: str,vol_name: str, vol_uuid: str, chgnum: str, headers_inc: str):

    """ Rename Volume """
    new_name = vol_name
    dataobj = {}
    if "root" in vol_name:
        print("Volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" is not recommended to renamed, since it's root volume.")
        return new_name
    else:    
        
        
        chk = input("Would you like to rename volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" to "+bcolors.OKGREEN +new_name+"_"+chgnum+"_Tobedeleted"+ bcolors.ENDC +"? (y/n)")
        if chk =='y':
            new_name = vol_name+"_"+chgnum+"_Tobedeleted"
            dataobj['name'] = new_name
                        
            rname_url="https://{}/api/storage/volumes/{}?return_timeout=15".format(cluster, vol_uuid)
            result = get_res(cluster,rname_url,dataobj,headers_inc)
                
            if result[1] == "success":
                print("Volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" renamed to "+bcolors.OKBLUE +new_name+bcolors.ENDC +" was "+bcolors.OKGREEN +"Successful"+ bcolors.ENDC +".")
            else:
                print("respone",result[0])
 
    return new_name
 
def vol_offline(cls_name: str,vol_name: str,vol_uuid: str,headers_inc: str):

    """ Offline Volume """
    
    dataobj = {}
    if "root" in vol_name:
        print("Volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" is not recommended to offline, since it's root volume.")
    else:    
                
        chk = input("Would you like to offline volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" ? (y/n)")
        if chk =='y':
            
            dataobj['state'] = "offline"
                        
            offl_url="https://{}/api/storage/volumes/{}?return_timeout=15".format(cls_name, vol_uuid)
            result = get_res(cls_name,offl_url,dataobj,headers_inc)
                
            if result[1] == "success":
                print("Volume "+bcolors.OKBLUE +vol_name+bcolors.ENDC +" Offlined "+bcolors.OKGREEN +"Successful"+ bcolors.ENDC +".")
                print() 
            else:
                print("respone",result[0])


 
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
    
    vol_data = "C:\\Users\\Administrator.DEMO\\Documents\\ProjC\\test\\VolumeDetails.xlsx"
           
    vol_df = pd.read_excel(vol_data)
    #print(vol_df.T)
    vol_df["Junction Path"].fillna("No", inplace = True) 
    print()
    chgnum = input("Enter valid and approved change number:")
    print()
    for ind in vol_df.index:
        
        vol_name = vol_df['Volume name'][ind]
        cls_name = vol_df['Cluster Name'][ind]
        svm_name = vol_df['Vserver Name'][ind]
        vol_uuid = vol_df['Volume UUID'][ind]
        dsvol_name = vol_df['Dest_Vol_Name'][ind]
        dscls_name = vol_df['Target Cluster'][ind]
        dssvm_name = vol_df['Target SVM'][ind]
        dsvol_uuid = vol_df['Dest_Vol_UUID'][ind]
        snpmir_check = vol_df['SnapMirror(Y/N)'][ind]
        mnt_chk = vol_df['Junction Path'][ind]
        cifs_list = vol_df['CIFS Shares List'][ind]
        
        print("############################     "+bcolors.OKCYAN+vol_name+bcolors.ENDC +"       ########################################################")
        print()
       # print(bcolors.WARNING+ vol_name +bcolors.ENDC)
        cifs_check = vol_df['No. of CIFS Shares'][ind]
        
        if cifs_check!=0:
            if snpmir_check == 'Yes':
                dscifs_list = vol_df['Dest_Vol_CIFS_Name'][ind]
                print("Volume "+bcolors.OKBLUE+vol_name+bcolors.ENDC +" has CIFS share(s) "+bcolors.OKBLUE+cifs_list+bcolors.ENDC +".")
                CIN= input("Do you want to Delete CIFS Shares on Source & Destination Volume volumes (y/n)")
                print()
                if CIN=='y':
                    print("Volume "+bcolors.OKBLUE+vol_name+bcolors.ENDC +" has CIFS share(s) "+bcolors.OKBLUE+cifs_list+bcolors.ENDC +".")
                    print("Proceeding with CIFS Deletion on Source Volume....")
                    cifs_delete(cls_name,vol_name,svm_name,cifs_list, headers)
                    print()
                    #print("Volume "+bcolors.OKBLUE+dsvol_name+bcolors.ENDC +" has CIFS share(s) "+bcolors.OKBLUE+dscifs_list+bcolors.ENDC +".")
                    print("Proceeding with CIFS Deletion on Destination Volume....")
                    cifs_delete(dscls_name,dsvol_name,dssvm_name,dscifs_list, headers)
                else:
                    print("Volume "+bcolors.OKBLUE+vol_name+bcolors.ENDC +" has CIFS share(s) "+bcolors.OKBLUE+cifs_list+bcolors.ENDC +".")
                    CINS= input("Do you want to Delete CIFS Shares on Source Volume volumes Instead..(y/n)")
                    if CINS=='y':
                        cifs_delete(cls_name,vol_name,svm_name,cifs_list, headers)
            else:
                CINS= input("Do you want to Delete CIFS Shares...(Y/N)")
                if CINS=='y':
                    cifs_delete(cls_name,vol_name,svm_name,cifs_list, headers)
        else:
            print("Volume "+bcolors.OKBLUE+vol_name+bcolors.ENDC +" not configured for CIFS.")
            
        print()
        # Mount path Check# 
        mnt_chk = vol_df['Junction Path'][ind]
        if mnt_chk == "NA":
            print("Volume "+bcolors.OKBLUE+vol_name+bcolors.ENDC +" is not mounted")
        else:
            if snpmir_check == 'Yes':
                MO_IN= input("Do you want to Unmount Source & Destination Volume volumes (y/n)")
                print("Volume "+bcolors.OKBLUE+vol_name+bcolors.ENDC +" has juntion path "+bcolors.OKBLUE+mnt_chk+bcolors.ENDC +".")
                if MO_IN =='y':
                    print("Proceeding with Source Volume Unmount...."+bcolors.HEADER+vol_name+bcolors.ENDC )
                    vol_unmnt(cls_name,vol_name,vol_uuid,headers)
                    print("Proceeding with Destination Volume Unmount...."+bcolors.HEADER+dsvol_name+bcolors.ENDC )
                    vol_unmnt(dscls_name,dsvol_name,dsvol_uuid,headers)
                else:
                    print("Proceeding with Source Volume Unmount....")
                    vol_unmnt(cls_name,vol_name,vol_uuid,headers)
            else:
                    print("No Snapmirror, Proceeding with Volume Unmount....")
                    vol_unmnt(cls_name,vol_name,vol_uuid,headers)
        print()    
        
        if snpmir_check == 'Yes':
            #print()
            tgt_cls = vol_df['Target Cluster'][ind]
            smr_uuid = vol_df['SnapMirror UUID'][ind]
            sm_quiesce_break(tgt_cls,smr_uuid, headers)
        else:
            #print()
            print("Volume "+bcolors.OKBLUE+vol_name+bcolors.ENDC +" of Cluster/Vserver :"+bcolors.HEADER+cls_name+"/"+svm_name+bcolors.ENDC +" does not have snapmirror configured")
            
        print()
        if snpmir_check == 'Yes':
            dest= input("Do you want to Rename Source & Destination volumes (y/n)"+bcolors.HEADER+bcolors.ENDC) 
            print()
            if dest == 'y':
                print("Proceeding with Source Volume"+bcolors.HEADER+vol_name+bcolors.HEADER+bcolors.ENDC)
                vname = vol_rename(cls_name,vol_name,vol_uuid,chgnum,headers) #To_Excel -> vname,vol_uuid,cls_name
                
                print()
                print("Proceeding with Destination Volume"+bcolors.HEADER+dsvol_name+bcolors.HEADER+bcolors.ENDC)
                dname = vol_rename(dscls_name,dsvol_name,dsvol_uuid,chgnum,headers) # To_Excel -> dname,dsvol_uuid,dscls_name
                
            else:
                print("You Have selected Not to cleanup destination volume, Proceeding with  Source  volume cleanup"+bcolors.HEADER+vol_name+bcolors.HEADER+bcolors.ENDC)
                vname = vol_rename(cls_name,vol_name,vol_uuid,chgnum,headers)
        else:
            print("No Snapmirror, Proceeding with Volume Rename....")
            vname = vol_rename(cls_name,vol_name,vol_uuid,chgnum,headers)
        print()
        
        if snpmir_check == 'Yes':
            dest= input("Do you want to offline the Source & Destination volumes (y/n)")        
            print()
            if dest == 'y':
                print("Proceeding with Source Volume")
                vol_offline(cls_name,vname,vol_uuid,headers)
                print()
                print("Proceeding with Destination Volume")
                vol_offline(dscls_name,dname,dsvol_uuid,headers)
                
            else:
                print("You Have selected Not to cleanup destination volume, Proceeding with  Source  volume cleanup")
                vol_offline(cls_name,vname,vol_uuid,headers)
        else:
            print("No Snapmirror, Proceeding with Volume Offline....")
            vol_offline(cls_name,vname,vol_uuid,headers)
               
        print()
        
       