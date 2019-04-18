#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import urllib 
import urllib2
import requests

# from kafka import KafkaConsumer
# from kafka import KafkaProducer

from desktop.lib.django_util import render
from django.views.decorators.csrf import csrf_exempt
import datetime
import time
import json
import logging

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from desktop.conf import USE_NEW_EDITOR
from desktop.lib.django_util import render, JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.json_utils import JSONEncoderForHTML
from desktop.models import Document2, Document, FilesystemException
from desktop.views import serve_403_error

from metadata.conf import has_optimizer, has_navigator

from notebook.conf import get_ordered_interpreters, SHOW_NOTEBOOKS
from notebook.connectors.base import Notebook, get_api, _get_snippet_name
from notebook.connectors.spark_shell import SparkApi
from notebook.decorators import check_document_access_permission, check_document_modify_permission
from notebook.management.commands.notebook_setup import Command
from notebook.models import make_notebook


##---------------------------test environment------------------------------
cluster1="ESBiz"
url1="http://hdpjntest.chinacloudapp.cn:12200/"
cluster2="ESLog"
url2="http://hdpjntest.chinacloudapp.cn:12200/"
cluster5="ESLog2"
url5="http://hdpjntest.chinacloudapp.cn:12200/"
cluster7="ESTest"
url7="http://hdpjntest.chinacloudapp.cn:12200/"


cluster3="esbiz"
url3="http://hdpjntest.chinacloudapp.cn:12200/"
cluster4="eslog"
url4="http://hdpjntest.chinacloudapp.cn:12200/"
cluster6="eslog2"
url6="http://hdpjntest.chinacloudapp.cn:12200/"
cluster8="estest"
url8="http://hdpjntest.chinacloudapp.cn:12200/"

##---------------------------test environment end---------------------------



# kafka_server = '10.0.0.17:9093'
# kafka_topic = "TeldLogUserOPLogV1"

# funcflag=0;


# ---------------------production environment----------------------
# cluster1="ESBiz"
# url1="http://192.168.2.237:12200/"
# cluster2="ESLog"
# url2="http://192.168.2.244:12200/"
# cluster5="ESLog2"
# url5="http://192.168.3.252:12200/"
# cluster7="ESTest"
# url7="http://hdpjntest.chinacloudapp.cn:12200/"

# cluster3="esbiz"
# url3="http://192.168.2.237:12200/"
# cluster4="eslog"
# url4="http://192.168.2.244:12200/"
# cluster6="eslog2"
# url6="http://192.168.3.252:12200/"
# cluster8="estest"
# url8="http://hdpjntest.chinacloudapp.cn:12200/"
# --------------------production environment end---------------------


def index(request, is_mobile=False, is_embeddable=False):
      
  editor_id = request.GET.get('editor')
  editor_type = request.GET.get('type', 'template')

  if editor_type == 'notebook' or request.GET.get('notebook'):
    return notebook(request)

  if editor_id:  # Open existing saved editor document
    document = Document2.objects.get(id=editor_id)
    editor_type = document.type.rsplit('-', 1)[-1]

  template = 'index.mako'
  if is_mobile:
    template = 'index.mako'

  return render(template, request, {
      'editor_id': editor_id or None,
      'notebooks_json': '{}',
      'is_embeddable': request.GET.get('is_embeddable', False),
      'editor_type': editor_type,
      'options_json': json.dumps({
        'languages': get_ordered_interpreters(request.user),
        'mode': 'editor',
        'is_optimizer_enabled': has_optimizer(),
        'is_navigator_enabled': has_navigator(request.user),
        'editor_type': editor_type,
        'mobile': is_mobile
      })
  })


def GetIndexJson(indexname,clusterurl):
  reqUrl=str(clusterurl)+str(indexname)
  response = requests.get(reqUrl)
  print("----------------------response:"+str(response.text))
  return response.text
     
def GetTemplateJson(funcflag=None,templatename=None,clusterurl=None):
  if(funcflag==2):
    reqUrl=str(clusterurl)+"_template/"+str(templatename)+"_template";
  else:
    reqUrl=str(clusterurl)+"_template/"+str(templatename)
  print("----------------------------reqUrl:"+reqUrl)
  response = requests.get(reqUrl)
  print("----------------------response:"+str(response.text))
  return response.text


# ESUsrOpLog parameter OpContent need a json format value,other parameters should be string
def ESUsrOpLog(saveuserid,saveusername,usergroupname,action=None,cluster=None,TableName=None,OpType=None,OpContent=None,context=None):

  url=url5
  now_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
  print("---------------------nowtime:")
  print(now_time)
  now_time2=time.time()
  print(now_time2)
  data_secs = (now_time2 - int(now_time2)) * 1000
  now_time = "%s%03d+08:00" % (now_time, data_secs)

  now_date=str(now_time)[0:6]
  
  index_name="useroplog_"+now_date
  index_type="useroplog"
  requrl=url+index_name+"/"+index_type
  # producer = KafkaProducer(bootstrap_servers=kafka_server)
  save_data={}
  save_data['AppCode']="BDP"
  save_data['ModuleCode']='HUE'
  #UserID value 
  save_data['UserID']=str(saveuserid)
  save_data['CreateTime']=now_time
  save_data['Action']=action
  save_data['Ext10']=cluster
  save_data['Ext11']=TableName
  save_data['Ext12']=OpType
  strOpContent = json.dumps(OpContent)
  save_data['Ext13']=strOpContent
  save_data['Ext14']=str(saveusername)
  save_data['Context']=context
  save_data['ExtColumnNames']="Ext10:ClusteName,Ext11:TargetTable,Ext12:OpType,Ext13:OpJson,Ext14:UserName"
  msg=json.dumps(save_data)
  ## kafka send method
  # print("-------------------producer.send()------------------")
  # producer.send(kafka_topic,msg,partition=0)
  # producer.close()
  headers={
      'Content-Type':"application/json;charset=UTF-8"
    }
    
  write_es_response = requests.post(requrl,data=msg,headers=headers)
  print(">>>>>>>>>>>>>>>>>>>>>>>>>>write_es_response:"+str(write_es_response.text))



def getJson(request):
    saveuserid = json.loads(request.POST.get('myUserId','{}')) 
    saveusername = json.loads(request.POST.get('myUserName','{}'))
    usergroupname = json.loads(request.POST.get('myWorkGroup','{}'))
    print("---------------------------------saveusername:"+str(saveusername))
    print("---------------------------------usergroupname:"+str(usergroupname))
    
    flag = json.loads(request.POST.get('flag', '{}'))
    indexJson = json.loads(request.POST.get('indexJson', '{}'))
    indexname = json.loads(request.POST.get('indexName', '{}'))
    cluster = json.loads(request.POST.get('inputCluster', '{}'))
    completeindname=json.loads(request.POST.get('completeindexName', '{}'))

    # saveusername = json.loads(request.POST.get('myUserName','{}'))
    usergroupname = "BDP"
    # print("---------------------------------saveusername:"+str(saveusername))
    # print("---------------------------------usergroupname:"+str(usergroupname))
    
    if (cluster==cluster3):
      url=url3
    elif(cluster==cluster4):
      url=url4
    elif(cluster==cluster6):
      url=url6
    elif(cluster==cluster8):
      url=url8
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>getJson:Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return

    if(flag==2):
      partitionGranularity=json.loads(request.POST.get('partitionGranularity', '{}'))

    if(flag==1):
        
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^indexname:"+str(indexname));
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^cluster:"+str(cluster));
      data=json.dumps(indexJson);
    
      result= createIndex(data,indexname,cluster);
      return result;
    elif(flag==2):
      funcflag=2;
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^indexname:"+str(indexname));
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^cluster:"+str(cluster));
      data=json.dumps(indexJson);
      originalTemplateJson="";
      result= createTemplate(data,indexname,cluster,partitionGranularity);
      modifiedTemplateJson=GetTemplateJson(funcflag,indexname,url);
      modifiedTemplateJson=json.loads(modifiedTemplateJson)
      if(result.status_code==200):
        context={}
        action="ESTemplateMgr"
        OpType="Create Template"
        context['OriginalFormat']=originalTemplateJson
        context['ModifiedFormat']=modifiedTemplateJson
        context=json.dumps(context)
        try:
          ESUsrOpLog(saveuserid,saveusername,usergroupname,action,cluster,indexname,OpType,indexJson,context)
        except:
          print(">>>>>>>>>>>>>>>>>Write UserOpLog Error<<<<<<<<<<<<<<<<<<<<<<<<<")
      return result;
    elif(flag==3):
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^flag:"+str(flag));
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^indexname:"+str(indexname));
      # templateind=indexname.find('_template');
      # indexname=indexname[0:templateind];
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^cluster:"+str(cluster));
      data=json.dumps(indexJson);
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^completeindname:"+str())
      originalJson=GetTemplateJson(None,completeindname,url);
      originalJson=json.loads(originalJson)
      result= createTemplate(data,completeindname,cluster,None,flag);
      modifiedJson=GetTemplateJson(None,completeindname,url);
      modifiedJson=json.loads(modifiedJson);
      if(result.status_code==200):
        context={}
        action="ESTemplateMgr"
        OpType="Edit Template"
        context['OriginalFormat']=originalJson
        context['ModifiedFormat']=modifiedJson
        context=json.dumps(context)
        try:
          ESUsrOpLog(saveuserid,saveusername,usergroupname,action,cluster,completeindname,OpType,indexJson,context)
        except:
          print(">>>>>>>>>>>>>>>>>Write UserOpLog Error<<<<<<<<<<<<<<<<<<<<<<<<<")
      return result;
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>No JSON<<<<<<<<<<<<<<<<<<<<<<<<<<");
      return false;
 
def createIndex(indexJson,indexname,cluster):
    if (cluster==cluster1):
      url=url1
    elif(cluster==cluster2):
      url=url2
    elif(cluster==cluster7):
      url=url7
    reqUrl=str(url)+str(indexname)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>reqURL:"+reqUrl)
    headers={
      'Content-Type':"application/json;charset=UTF-8"
    }
    response = requests.put(reqUrl,data=indexJson,headers=headers)

    if(response.status_code==200):
      print("---------------------Success-------------------")
      # return True;
    else:
      print("---------------------Failed2--------------------")
      # return False
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>response:::"+str(response.text))
    return HttpResponse(response.text);


def createTemplate(indexJson,indexname,cluster,partitionGranularity="",flag=None):
    if (cluster==cluster3):
      url=url3
    elif(cluster==cluster4):
      url=url4
    elif(cluster==cluster6):
      url=url6
    elif(cluster==cluster8):
      url=url8
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>getJson:Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return

    if(flag==3):
      reqUrl=str(url)+"_template/"+str(indexname)
    else:
      reqUrl=str(url)+"_template/"+str(indexname)+"_template"

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>reqURL:"+reqUrl)
    headers={
      'Content-Type':"application/json;charset=UTF-8"
    }
    response = requests.put(reqUrl,data=indexJson,headers=headers)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>response:"+str(response));
    if(response.status_code==200):
      if(partitionGranularity!=""):
        sgService(indexname,cluster,partitionGranularity);
        print("---------------------SgService Success-------------------")
      print("---------------------Create Template Success-------------------")
      # return True;
    else:
      print("---------------------Failed2--------------------")
      # return False
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>response:::"+str(response.text))
    return HttpResponse(response.text);

def sgService(indexname,cluster,partitionGranularity):
    # ------------test environment---------------
    # return;
    # ----------test environment end------------------
    # ----------production environment------------------
    if (cluster==cluster3):
      clustername="ES_BZ"
    elif(cluster==cluster4):
      clustername="ES"
    elif(cluster==cluster6):
      clustername="ES_LOG"    
    else:
      print("---------------------No cluster--------------------")
      return;
    # ----------production environment end------------------    
    print(">>>>>>>>>>>>>>>>>>>clustername<<<<<<<<<<<<<<<<<<<");
    print(clustername);
    print(">>>>>>>>>>>>>>>>>>>indexname<<<<<<<<<<<<<<<<<<<");
    print(indexname);
    print(">>>>>>>>>>>>>>>>>>>partitionGranularity<<<<<<<<<<<<<<<<<<<");
    print(str(partitionGranularity));
    response = requests.get("http://configcenter.teld.local:8777/api/get?key=TTP.SG.InternalNgx")
    dictResponse=json.loads(response.text)
    print(">>>>>>>>>>>>>>>>>>>>>>>dictResponse<<<<<<<<<<<<<<<<<<<<<<<<")
    print(dictResponse)
    result_content=dictResponse['result_content']
    print(">>>>>>>>>>>>>>>>>>>>>>>result_content<<<<<<<<<<<<<<<<<<<<<<<<")
    print(result_content)
    if (result_content==""):
      print("Getting url from configcenter failed.")
      return;
    else:
      sg_url=result_content+"/api/invoke?SID=BDPDR-INNER-AddObjectMetadata";
      sg_url=sg_url+"&clusterName="+str(clustername)
      sg_url=sg_url+"&tableName="+str(indexname)
      # partitionGranularity is a digit ranging from 0 to 5
      sg_url=sg_url+"&partitionGranularity="+str(partitionGranularity)
      print(">>>>>>>>>>>>>>>>>>>>>>>sg_url<<<<<<<<<<<<<<<<<<<<<<<<")
      print(sg_url)
    response2 = requests.get(sg_url);
    dictResponse2=json.loads(response2.text)
    print(">>>>>>>>>>>>>>>>>>>>>>>dictResponse2<<<<<<<<<<<<<<<<<<<<<<<<")
    print(dictResponse2)
    state=dictResponse2['state']
    print(">>>>>>>>>>>>>>>>>>>>>>>state<<<<<<<<<<<<<<<<<<<<<<<<")
    print(state)
    if (state==0):
      print("SG Service ERROR!");
      return;
    else:
      print("SG Service SUCCESS!");
      return;

def editTemplate(request, is_mobile=False, is_embeddable=False):
    # editor_id = request.GET.get('editor')
    # editor_type = request.GET.get('type', 'template')
    print("----------------------------name: "+request.GET.get('templateName')+"---------------------------")
    indName=request.GET.get('templateName')
    cluster=request.GET.get('cluster')
    if (cluster==cluster3):
      url=url3
    elif(cluster==cluster4):
      url=url4
    elif(cluster==cluster6):
      url=url6
    elif(cluster==cluster8):
      url=url8
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return
    reqUrl=str(url)+"_template/"+str(indName)
    response = requests.get(reqUrl)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5%555555")
    print(response)
    print(response.text)
    print(type(response.text))
    
    print(type(response.text))
    print("--------------------------------------------------")
    dictResponse=json.loads(response.text)
    print(dictResponse)
    print("--------------------------------------------------")
    strtemplatename=indName;
    # ind=indName.find("_template")
    # if(ind!=-1):
    #     partIndName=indName[0:ind+1]
    # else:
    #     partIndName=indName[0:ind+1]  
    # print(dictResponse[strtemplatename]['mappings'].keys())

    # print("------------------Alias:---"+str(dictResponse[indName]['aliases'].keys()))
    if(dictResponse[strtemplatename]['mappings']):
      indexname00=str(dictResponse[strtemplatename]['mappings'].keys()[0])
      print("--------------------------"+indexname00)
    fields=dictResponse[strtemplatename]['mappings'][indexname00]['properties']
    tempFields=dictResponse[strtemplatename]['mappings'][indexname00]['properties'].keys()
    print("------------------------type(tempFields):"+str(type(tempFields)))
    print(">>>>>>>>>>>>>>>>>>>>>>>>tempFields<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print(tempFields)
    fieldType=[]
    fieldFormat=[]
    for field in tempFields:
        if(("fields" in fields[field].keys())):
          fieldType.append("AboveTwo")
        else:  
          fieldType.append(fields[field]["type"])
          
        if(fields[field]["type"]=="date"):
          if(fields[field].has_key('format')):
            fieldFormat.append(fields[field]["format"])
          else:
            fieldFormat.append("")   
        else:
          fieldFormat.append("")    
    print(">>>>>>>>>>>>>>>>>>>>>>>fieldType<<<<<<<<<<<<<<<<<<<<<<<<<")
    print(fieldType)
    print(">>>>>>>>>>>>>>>>>>>>>>>fieldFormat<<<<<<<<<<<<<<<<<<<<<<<<<")
    print(fieldFormat)
    if(dictResponse[strtemplatename]['aliases']):
      indAliases=dictResponse[strtemplatename]['aliases'].keys()
    else:
      indAliases=None

    if(dictResponse[strtemplatename]['settings']): 
      if(dictResponse[strtemplatename]['settings']['index']):  
        dictindex=dictResponse[strtemplatename]['settings']['index']
      else:
        dictindex=None
    else:
      dictindex=None

    print("-----------------------dictindex:"+str(dictindex))

    if(dictindex!=None):
      if(dictindex.has_key('max_result_window')):
        tempMaxResultWindow=dictindex['max_result_window']
      else:
        tempMaxResultWindow=None
      print("--------------------tempMaxResultWindow:"+str(tempMaxResultWindow))
      if(dictindex.has_key('number_of_shards')):
        tempNumofShards=dictindex['number_of_shards']
      else:
        tempNumofShards=None
      print("--------------------tempNumofShards:"+str(tempNumofShards))
      if(dictindex.has_key('number_of_replicas')):
        tempNumofRep=dictindex['number_of_replicas']
      else:
        tempNumofRep=None
    else:
      tempMaxResultWindow=None
      tempNumofShards=None
      tempNumofRep=None

    if(indAliases!=None):
      strindAliases=','.join(indAliases);
    else:
      strindAliases="";
    if(fieldFormat!=None):
      strfieldFormat=','.join(fieldFormat);
    else:
      strfieldFormat="";
    if(fieldType!=None):
      strfieldType=','.join(fieldType);
    else:
      strfieldType=""; 
    if(tempFields!=None):
      strtempFields=','.join(tempFields);
    else:
      strtempFields="";
    print("---------------------------------strindAliases:-----"+strindAliases)
    print("---------------------------------strfieldFormat:-----"+strfieldFormat)
    print("---------------------------------strfieldType:-----"+strfieldType)
    print("---------------------------------strtempFields:-----"+strtempFields)
    # stringType=','.join(indType)
    # print("------------------------------stringType:"+stringType)
    editor_id = request.GET.get('editor')
    editor_type = request.GET.get('type', 'template')

    if editor_type == 'notebook' or request.GET.get('notebook'):
      return notebook(request)

    if editor_id:  # Open existing saved editor document
      document = Document2.objects.get(id=editor_id)
      editor_type = document.type.rsplit('-', 1)[-1]
    template = 'editTemplateEditor.mako'
    if is_mobile:
      template = 'editTemplateEditor.mako'
    
    return render(template, request, {
      'editor_id': editor_id or None,
      'notebooks_json': '{}',
      'is_embeddable': request.GET.get('is_embeddable', False),
      'editor_type': editor_type,
      'indAliases':strindAliases,
      'templateFields':strtempFields,
      'templatefieldType':strfieldType,
      "templatefieldFormat":strfieldFormat,
      'indName':indName,
      'cluster':cluster,
      'tempMaxResultWindow':tempMaxResultWindow,
      'tempNumofShards':tempNumofShards,
      'tempNumofRep':tempNumofRep,
      'myurl':url,
      'options_json': json.dumps({
        'languages': get_ordered_interpreters(request.user),
        'mode': 'editor',
        'is_optimizer_enabled': has_optimizer(),
        'is_navigator_enabled': has_navigator(request.user),
        'editor_type': editor_type,
        'mobile': is_mobile
      })
  })

