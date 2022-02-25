import pandas as pd
import openpyxl as xl
import urllib3 as ur
import base64
import argparse
from getpass import getpass
import logging
import requests
import sys
ur.disable_warnings()

def find_clstr():
    
    """Get cluster info from inventory using user inputs"""
   

    usr_data = "C:\\Users\\Administrator.DEMO\\Documents\\GitHub\\ProjC\\test\\svmvol.xlsx"
    inv_data = "C:\\Users\\Administrator.DEMO\\Documents\\GitHub\\ProjC\\test\\clstrsvm.xlsx"
       
    usr_df = pd.read_excel(usr_data)
    inv_df = pd.read_excel(inv_data)
    
    
    for ind1 in usr_df.index:
        usr_df.loc[ind1,'clstr_match'] = list(inv_df[inv_df['svm_name'].str.contains(usr_df['SVM_Name'][ind1])]['cls_name'])
    
    cons_df = usr_df[['clstr_match','Vol_Name','SVM_Name']]
    cons_df.to_excel("C:\\Users\\Administrator.DEMO\\Documents\\GitHub\\ProjC\\test\\clstrvol.xlsx", sheet_name='clstrvol', index=False, header=False)
    

    return cons_df
    
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


def vol_meta(cluster: str, svm_name: str, volume_name: str, headers_inc: str):
    
    """ Pulls Volume Name & UUID """
    
    vol_url = "https://{}/api/storage/volumes/?svm.name={}&name={}".format(cluster,svm_name,volume_name)
    vol_response = requests.get(vol_url, headers=headers_inc, verify=False)
    vol_json = vol_response.json()
    
    vol_dt = dict(vol_json)
    if 'error' in vol_json:
        print ("Incorrect User Name / Password")
        sys.exit(1)
    else:
        vol_rd = vol_dt['records']
        
        
        for i in vol_rd:
            volume = dict(i)
            
        vol_name = volume['name']
        vol_uuid = volume['uuid']
        
    
    return vol_name,vol_uuid
    
    
def nas_path(cluster: str, volume_uuid: str, headers_inc: str):
    
    """ Pulls Junction Path & Vserver details"""
    
    vol_url = "https://{}/api/storage/volumes/{}".format(cluster, volume_uuid)
    vol_response = requests.get(vol_url, headers=headers_inc, verify=False)
    vol_json = vol_response.json()
    
    vol_dt = dict(vol_json)
    tmp = vol_dt['svm']
    vsrv = tmp['name']
    state = vol_dt['state']
    tier = vol_dt['type']
    
    nas_url = "https://{}/api/storage/volumes?uuid={}&fields=nas.path".format(cluster, volume_uuid)
    response = requests.get(nas_url, headers=headers_inc, verify=False)
    nas_json = response.json()
    
    nas_dt = dict(nas_json)
    nas_rd = nas_dt['records']
    for keys in nas_rd:
        chk = keys.get('nas')
        if chk is None:
            path = "NA"
        else:
            val = keys['nas']
            nas_jp = dict(val)
            chk1 = nas_jp['path']
            if (chk1 is None):
                path = "NA"
            else:
                path = nas_jp['path']
                
                
    return vsrv, state, tier, path

def vol_stats(cluster: str, volume_uuid: str, headers_inc: str):
    
    """ Pulls Volume's Raw Statistical IOPS & Throughput details"""
        
    stat_url = "https://{}/api/storage/volumes?uuid={}&fields=metric.iops.read,metric.iops.write,metric.iops.other,metric.iops.total,metric.throughput.total,metric.throughput.read,metric.throughput.write,metric.throughput.other".format(cluster, volume_uuid)
    response = requests.get(stat_url, headers=headers_inc, verify=False)
    stat_json = response.json()
    print("stat_json",stat_json)
    stat_dt = dict(stat_json)
    stat_rd = stat_dt['records']
    for keys in stat_rd:
        val = keys['metric']
        st_js = dict(val)
        iops = st_js['iops']
        ival = dict(iops)
        riops = ival['read']
        wiops = ival['write']
        oiops = ival['other']
        tiops = ival['total']
        thrp = st_js['throughput']
        ithrp = dict(thrp)
        rthrp = ithrp['read']
        wthrp = ithrp['write']
        othrp = ithrp['other']
        tthrp = ithrp['total']

    return riops,wiops,oiops,tiops,rthrp,wthrp,othrp,tthrp

def snap_mirr(cluster: str, svm_name: str, volume_name: str, headers_inc: str):
    
    """ Pulls Volume's Snapmirror details"""
        
    snap_url = "https://{}/api/snapmirror/relationships?list_destinations_only=true&source.path={}:{}&return_records=true&return_timeout=15".format(cluster, svm_name, volume_name)
    response = requests.get(snap_url, headers=headers_inc, verify=False)
    snap_json = response.json()
    
    snap_dt = dict(snap_json)
    snap_rd = snap_dt['records']
    # isp is "is_proctedted", scrp is "source_path", desp is "destination_path"
    isp = scrp = desp = "NA"
    if snap_rd:
        for keys in snap_rd:
            src_val = keys['source']
            src_p = dict(src_val)
            scrp = src_p['path']
            des_val = keys['destination']
            des_p = dict(des_val)
            desp = des_p['path']
            isp = "Yes"
    else:
        scrp = "NA"
        desp = "NA"
        isp = "No"
            
    return isp,scrp,desp

def nfs_connect(cluster: str, volume_name: str, headers_inc: str):
    
    """Get NFS connected clients to Volume/Shares """
    
    nfs_url = "https://{}/api/private/cli/nfs/connected-clients/?volume={}".format(cluster,volume_name)
    response = requests.get(nfs_url, headers=headers_inc, verify=False)
    nfs_json = response.json()
    
    nfs_dt=dict(nfs_json)
    nfs_rd=nfs_dt['records']
    
    i=0
    nfs_conn=[]
    for conn in nfs_rd:
        i=i+1
        nfs_clnt=dict(conn)
        nfs_ip=nfs_clnt['client_ip']
        nfs_conn.append(nfs_ip)
        
    return volume_name, nfs_conn
    
    
def qtr_quo(cluster: str, volume_uuid: str, headers_inc: str):
   
    """Get Qtree and Quota details of Volumes """
   
    qtree_url= "https://{}/api/storage/qtrees/{}/".format(cluster,volume_uuid)
    response = requests.get(qtree_url, headers=headers_inc, verify=False)
    qtree_json = response.json()
    print ("qtree_json",qtree_json)
    qtree_dt=dict(qtree_json)
    qtree_rd=qtree_dt['records']
    print("qtree_rd",qtree_rd)
    output=[]
    for i in qtree_rd:
        qtree=dict(i)
        qtree_name=qtree['name']
        qid = qtree['id']
        qvol=qtree['volume']
        qvol_dt=dict(qvol)
        qvol_n=qvol_dt['name']
        print("qvol_n",qvol_n)
        qind_url = "https://{}/api/storage/quota/reports?qtree.name={}".format(cluster,qtree_name)
        response = requests.get(qind_url, headers=headers_inc, verify=False)
        qind_json = response.json()
        #print("qind_json",qind_json)
        
        if 'error' in qind_json:
            op = str(" id "+str(qid)+" with no Qtree/Quota")
            output.append(op)
        elif 'records' in qind_json : 
            qind_dt = dict(qind_json)
            qind_rd = qind_dt['records']
            qind_num = qind_dt['num_records']
            if qind_num ==0:
               op = str("Qtree "+ qtree_name +" with No Quota")
               output.append(op)
            else:
                for k in qind_rd:
                   index_dt = dict(k)
                   index_rd = index_dt['index']
                   space_ur1= "https://{}/api/storage/quota/reports/{}/{}".format(cluster,volume_uuid,index_rd)
                   response = requests.get(space_ur1, headers=headers_inc, verify=False)
                   space_jsos= response.json()
                   space_rd=space_jsos['space']
                   space_dt=dict(space_rd)
                   hard_raw=space_dt['hard_limit']
                   hard_limit=(((int(hard_raw)/1024)/1024)/1024)
                   op = str("Qtree "+ qtree_name +" with Quota of "+str(hard_limit)+" GB")
                   output.append(op)
        else:
            print()
    
    str_output = ', '.join([str(i) for i in output])
    
    return qvol_n, str_output            

def cifs_connect(cluster: str, volume_name: str, headers_inc: str):
    
    """ Pulls CIFS details """
    
    cifs_url= "https://{}/api/protocols/cifs/shares/?volume={}".format(cluster,volume_name)
    response = requests.get(cifs_url, headers=headers_inc, verify=False)
    cifs_json = response.json()
    
    cifs_num = cifs_json['num_records']
    CST=[]
    CSList=[]
    CSRList=[]
    CSTList=[]
    if cifs_num!=0:
        cifs_rd=cifs_json['records']
        #print(cifs_rd)
        for cs in cifs_rd:
            cifs_dt=dict(cs)
            cifs_name=cifs_dt['name']
            CST.append(cifs_name)
            VS=cifs_dt['svm']
            VSN=VS['uuid']
            
            if "root" in volume_name:
                CSRT= cifs_name + "Share is in Root Volume"
                CSRList.append(CSRT)
                vol_name = volume_name
                cifs_number = cifs_num
                cifs_list = CST
                cifs_acl = CSRList
            else:
                CSI= "https://{}/api/protocols/cifs/shares/{}/{}".format(cluster,VSN,cifs_name)
                CSIresponse=requests.get(CSI,headers=headers_inc, verify=False)
                CSID = CSIresponse.json()
                CSTN=CSID['name']
                if "acls" in CSID:
                    CSTA=CSID['acls']
                    CSTAT=[]
                    for i in CSTA:
                        CSTAC=i['permission']
                        CSTUG=i['user_or_group']
                        CSTMP="CIFS Share "+cifs_name+" has Permission to "+CSTUG+" with "+CSTAC+ " access"
                        #print(CSTMP)
                        CSList.append(CSTMP)
                    vol_name = volume_name
                    cifs_number = cifs_num
                    cifs_list = CST
                    cifs_acl = CSList
                else:
                    vol_name = volume_name
                    cifs_number = cifs_num
                    cifs_list = CST
                    cifs_acl = "NA"                    
    else:
        CT = "NA"
        CSTList.append(CT)
        vol_name = volume_name
        cifs_number = cifs_num
        cifs_list = "NA"
        cifs_acl = "NA"
    
    #return vol_name,cifs_number,cifs_list,cifs_acl
    return cifs_number,cifs_list,cifs_acl
    
                    
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
    
    # Pulls Cluster information using uservol.xls and inventory.xls using find_clstr() and place data to clstrvol.xls 
    cons_df = find_clstr()

    vd_df = nc_df = qq_df = cc_df = pd.DataFrame([], columns=None, index=None)
    
    
    for index, row in cons_df.iterrows():
        cluster = row[0]
        volume_name = row[1]
        svm_name = row[2]
        
        metavol = vol_meta(cluster, svm_name, volume_name, headers)
        js_vol_name = metavol[0]
        js_vol_uuid = metavol[1]
        
        naspath = nas_path(cluster,js_vol_uuid, headers)
        stats = vol_stats(cluster,js_vol_uuid, headers)
        snapdp = snap_mirr(cluster,svm_name,js_vol_name, headers)
        cifsc = cifs_connect(cluster,js_vol_name, headers)
        
        
        voldet = metavol + naspath + stats + snapdp + cifsc
        voldet_df = pd.DataFrame(data=voldet,columns=None,index=None)
        vd_df = vd_df.append(voldet_df.T, ignore_index=True)
        
        
        
        nfsc = nfs_connect(cluster,js_vol_name, headers)
        nfsc_df = pd.DataFrame(data=nfsc,columns=None,index=None)
        nc_df = nc_df.append(nfsc_df.T, ignore_index=True)
        
        qtrqo = qtr_quo(cluster,js_vol_uuid, headers)
        qtrqo_df = pd.DataFrame(data=qtrqo,columns=None,index=None)
        qq_df = qq_df.append(qtrqo_df.T, ignore_index=True)
        
        #cifsc = cifs_connect(cluster,js_vol_name, headers)
        #cifsc_df = pd.DataFrame(data=cifsc,columns=None,index=None)
        #cc_df = cc_df.append(cifsc_df.T, ignore_index=True)
        
       
    
    writer = pd.ExcelWriter(r'C:\\Users\\Administrator.DEMO\\Documents\\GitHub\\ProjC\\test\\VolumeDetails.xlsx')
    vd_df.to_excel(writer,sheet_name='VolDetails', index=False, header=['Volume name', 'Volume UUID', 'Vserver Name', 'Vol State', ' Vol Type', 'Junction Path', 'Read IOPS', 'Write IOPS', 'Other IOPS', 'Total IOPS', 'Read throughput', 'Write throughput', 'Other throughput', 'Total throughput', 'SnapMirror(Y/N)','Source Path', 'Destination Path','No. of CIFS Shares','CIFS Shares List','ACL'])
    nc_df.to_excel(writer,sheet_name='NFS Connected Clients', index=False, header=['Volume name', 'NFS Connections'])
    qq_df.to_excel(writer,sheet_name='Qtree and Quota', index=False, header=['Volume name', 'Qtree & Quota'])
    #cc_df.to_excel(writer,sheet_name='CIFS Connected Clients', index=False, header=['Volume name', 'No. of CIFS Shares','CIFS Shares List','ACL'])
    writer.save()
