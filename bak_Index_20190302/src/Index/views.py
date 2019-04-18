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

# from kafka import KafkaConsumer
# from kafka import KafkaProducer

import urllib 
import urllib2
import requests

from desktop.lib.django_util import render
from django.views.decorators.csrf import csrf_exempt
import time,datetime
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
# from selenium import webdriver

#-----------------------test environment----------------------
cluster1="ESBiz"
url1="http://hdpjntest.chinacloudapp.cn:12200/"
cluster2="ESLog"
url2="http://hdpjntest.chinacloudapp.cn:12200/"
cluster3="esbiz"
url3="http://hdpjntest.chinacloudapp.cn:12200/"
cluster4="eslog"
url4="http://hdpjntest.chinacloudapp.cn:12200/"
cluster5="ESLog2"
url5="http://hdpjntest.chinacloudapp.cn:12200/"
cluster6="eslog2"
url6="http://hdpjntest.chinacloudapp.cn:12200/"
#-----------------------test environment end----------------------

# kafka_server = '10.0.0.17:9093'
# kafka_topic = "TeldLogUserOPLogV1"

#-----------------------production environment----------------------
cluster1="ESBiz"
url1="http://192.168.2.237:12200/"
cluster2="ESLog"
url2="http://192.168.2.244:12200/"
cluster5="ESLog2"
url5="http://192.168.3.252:12200/"

cluster3="esbiz"
url3="http://192.168.2.237:12200/"
cluster4="eslog"
url4="http://192.168.2.244:12200/"
cluster6="eslog2"
url6="http://192.168.3.252:12200/"
#-----------------------production environment end----------------------


def index(request, is_mobile=False, is_embeddable=False):
      
  editor_id = request.GET.get('editor')
  editor_type = request.GET.get('type', 'elasticsearch')

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
     
def GetTemplateJson(templatename,clusterurl):
  reqUrl=str(clusterurl)+"_template/"+str(templatename)
  response = requests.get(reqUrl)
  print("----------------------response:"+str(response.text))
  return response.text

def print_result(response):
  if(response.status_code==200):
    print("----------------ESOpLog Write Success-------------------")
  else:
    print("----------------ESOpLog Write Failed-------------------")


# ESUsrOpLog parameter OpContent need a json format value,other parameters should be string
def ESUsrOpLog(saveuserid,saveusername,usergroupname,action=None,cluster=None,TableName=None,OpType=None,OpContent=None,context=None):

  url=url5

  now_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
  now_time2=time.time()
  data_secs = (now_time2 - int(now_time2)) * 1000
  now_time = "%s%03d+08:00" % (now_time, data_secs)
  now_date=str(now_time)[0:6]
  index_name="useroplog_"+str(now_date)
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
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    flag = json.loads(request.POST.get('flag', '{}'))
    indexJson = json.loads(request.POST.get('indexJson', '{}'))
    indexname = json.loads(request.POST.get('indexName', '{}'))
    cluster = json.loads(request.POST.get('inputCluster', '{}'))

    saveuserid = json.loads(request.POST.get('myUserId','{}'))
    saveusername = json.loads(request.POST.get('myUserName','{}'))
    usergroupname = json.loads(request.POST.get('myWorkGroup','{}'))
    print("---------------------------------saveusername:"+str(saveusername))
    print("---------------------------------usergroupname:"+str(usergroupname))

    if(cluster==cluster1):
      url=url1
    elif(cluster==cluster2):
      url=url2
    elif(cluster==cluster3):
      url=url3
    elif(cluster==cluster4):
      url=url4
    elif(cluster==cluster5):
      url=url5
    elif(cluster==cluster6):
      url=url6
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>getJson:Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return
      
    if(flag==2):
      partitionGranularity=json.loads(request.POST.get('partitionGranularity', '{}'))

    if(flag==1):     
      data=json.dumps(indexJson); 
      originalJson="";
      result= createIndex(data,indexname,cluster);
      # responsestr=json.dumps(result.content[0])
      # print(result.status_code)
      # print(result)
      # print(type(result))
      modifiedJson=GetIndexJson(indexname,url);
      modifiedJson=json.loads(modifiedJson)
      if(result.status_code==200):
        context={}
        action="ESIndexMgr"
        OpType="Create Index"
        context['OriginalFormat']=originalJson
        context['ModifiedFormat']=modifiedJson
        context=json.dumps(context)
        try:
          print("000000000000000000000000000")
          ESUsrOpLog(saveuserid,saveusername,usergroupname,action,cluster,indexname,OpType,indexJson,context)
        except:
          print(">>>>>>>>>>>>>>>>>Write UserOpLog Error<<<<<<<<<<<<<<<<<<<<<<<<<")
      return result;
    elif(flag==2):
      data=json.dumps(indexJson);
      originalTemplateJson="";
      result= createTemplate(data,indexname,cluster,partitionGranularity);
      modifiedTemplateJson=GetTemplateJson(indexname,url);
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
      data=json.dumps(indexJson); 
      result= createTemplate(data,indexname,cluster);
      return result;
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>No JSON<<<<<<<<<<<<<<<<<<<<<<<<<<");
      return false;


def createIndex(indexJson,indexname,cluster):
    if (cluster==cluster1):
      url=url1
    elif(cluster==cluster2):
      url=url2
    elif(cluster==cluster5):
      url=url5
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>createIndex:Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return
    
    reqUrl=str(url)+str(indexname)

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



def EditMaxResultWindow(request, is_mobile=False, is_embeddable=False):
    indName=request.GET.get('indexName')
    cluster=request.GET.get('cluster')
    if (cluster==cluster1):
      url=url1
    elif(cluster==cluster2):
      url=url2
    elif(cluster==cluster5):
      url=url5
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return
    reqUrl=str(url)+str(indName)
    response = requests.get(reqUrl)
    print(response.text)
    print(type(response.text))

    dictResponse=json.loads(response.text)
    if(dictResponse[indName]['settings']['index'].has_key('max_result_window')):
      nummaxresultwindow=dictResponse[indName]['settings']['index']['max_result_window']
    else:
      nummaxresultwindow=""

    if(nummaxresultwindow!=None):
      strnummaxresultwindow=str(nummaxresultwindow);
    else:
      strnummaxresultwindow="";

    editor_id = request.GET.get('editor')
    editor_type = request.GET.get('type', 'elasticsearch')

    if editor_type == 'notebook' or request.GET.get('notebook'):
      return notebook(request)

    if editor_id:  # Open existing saved editor document
      document = Document2.objects.get(id=editor_id)
      editor_type = document.type.rsplit('-', 1)[-1]
    template = 'index_maxresultwindow_editor.mako'
    if is_mobile:
      template = 'index_maxresultwindow_editor.mako'
    # rnd=
    return render(template, request, {
      'editor_id': editor_id or None,
      'notebooks_json': '{}',
      'is_embeddable': request.GET.get('is_embeddable', False),
      'editor_type': editor_type,
      'nummaxresultwindow':strnummaxresultwindow,
      'indName':indName,
      'myurl':url,
      'mycluster':cluster,
      'options_json': json.dumps({
        'languages': get_ordered_interpreters(request.user),
        'mode': 'editor',
        'is_optimizer_enabled': has_optimizer(),
        'is_navigator_enabled': has_navigator(request.user),
        'editor_type': editor_type,
        'mobile': is_mobile
      })
  })


def editAlias(request, is_mobile=False, is_embeddable=False):
    indName=request.GET.get('indexName')
    cluster=request.GET.get('cluster')
    print(">>>>>>>>>>>>>>>>>>>>>>>>>cluster:")
    print(cluster)
    if (cluster==cluster1):
      url=url1
    elif(cluster==cluster2):
      url=url2
    elif(cluster==cluster5):
      url=url5
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return
    reqUrl=str(url)+str(indName)
    response = requests.get(reqUrl)
    print(response.text)
    print(type(response.text))

    dictResponse=json.loads(response.text)
    print(dictResponse[indName]['mappings'].keys())
    print("------------------Alias:---"+str(dictResponse[indName]['aliases'].keys()))
    indType=dictResponse[indName]['mappings'].keys()
    indAliases=dictResponse[indName]['aliases'].keys()

    if(indAliases!=None):
      strindAliases=','.join(indAliases);
    else:
      strindAliases="";
    # stringType=','.join(indType)
    editor_id = request.GET.get('editor')
    editor_type = request.GET.get('type', 'elasticsearch')

    if editor_type == 'notebook' or request.GET.get('notebook'):
      return notebook(request)

    if editor_id:  # Open existing saved editor document
      document = Document2.objects.get(id=editor_id)
      editor_type = document.type.rsplit('-', 1)[-1]
    template = 'index_alias_editor.mako'
    if is_mobile:
      template = 'index_alias_editor.mako'
    # rnd=
    return render(template, request, {
      'editor_id': editor_id or None,
      'notebooks_json': '{}',
      'is_embeddable': request.GET.get('is_embeddable', False),
      'editor_type': editor_type,
      'indAliases':strindAliases,
      'indName':indName,
      'myurl':url,
      'mycluster':cluster,
      'options_json': json.dumps({
        'languages': get_ordered_interpreters(request.user),
        'mode': 'editor',
        'is_optimizer_enabled': has_optimizer(),
        'is_navigator_enabled': has_navigator(request.user),
        'editor_type': editor_type,
        'mobile': is_mobile
      })
  })
   
def modifyAlias(request):
    headers={
      'Content-Type':"text/plain"
    }
    indName=json.loads(request.POST.get('indexName', '{}'))
    aliasJson = json.loads(request.POST.get('aliasJson', '{}'))
    url= json.loads(request.POST.get('url', '{}'))
    clustername=json.loads(request.POST.get('clustername', '{}'))
    jsonData=json.dumps(aliasJson);
    requrl=url+"_aliases";
    
    saveuserid = json.loads(request.POST.get('myUserId',{}))
    saveusername = json.loads(request.POST.get('myUserName','{}'))
    usergroupname = json.loads(request.POST.get('myWorkGroup','{}'))
    print("---------------------------------saveusername:"+str(saveusername))
    print("---------------------------------usergroupname:"+str(usergroupname))

      
    originalJson=GetIndexJson(indName,url);
    originalJson=json.loads(originalJson)
    response = requests.post(requrl,data=jsonData,headers=headers)
    modifiedJson=GetIndexJson(indName,url);
    modifiedJson=json.loads(modifiedJson)
    if(response.status_code==200):
      context={}
      action="ESIndexMgr"
      OpType="Edit Alias"
      context['OriginalFormat']=originalJson
      context['ModifiedFormat']=modifiedJson
      context=json.dumps(context)
      try:
        ESUsrOpLog(saveuserid,saveusername,usergroupname,action,clustername,indName,OpType,aliasJson,context)
      except:
        print(">>>>>>>>>>>>>>>>>Write UserOpLog Error<<<<<<<<<<<<<<<<<<<<<<<<<")

    if(response.status_code==200):
      print("---------------------Success-------------------")

    else:
      print("---------------------Failed2--------------------")

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>response:::"+str(response.text))
    return HttpResponse(response.text);


def modifyMxRsltWin(request):
      
#  --------------------------variables for useroplog----------------------
    saveuserid = json.loads(request.POST.get('myUserId','{}'))
    saveusername = json.loads(request.POST.get('myUserName','{}'))
    usergroupname = json.loads(request.POST.get('myWorkGroup','{}'))
    print("---------------------------------saveuserid:"+str(saveuserid))
    print("---------------------------------saveusername:"+str(saveusername))
    print("---------------------------------usergroupname:"+str(usergroupname))
#  ------------------------variables for useroplog end ----------------------

    max_result_window_value=500000
    headers={
      'Content-Type':"application/json;charset=UTF-8"
    }
    indName=json.loads(request.POST.get('indexName', '{}'))
    MxRsltWinnum = json.loads(request.POST.get('MxRsltWinnum', '{}'))
    savecluster = json.loads(request.POST.get('mycluster', '{}'))
    print(type(MxRsltWinnum))
    print("--------------------MxRsltWinnum:"+str(MxRsltWinnum))
    MxRsltWinnum=int(str(MxRsltWinnum))
    if(MxRsltWinnum>max_result_window_value):
      print("--------------max_result_window should be no more than "+str(max_result_window_value)+"----------------")
      return
    reqjson=json.loads(request.POST.get('jsonstr', '{}'))
    url= json.loads(request.POST.get('url', '{}'))
    jsonData=json.dumps(reqjson);
    requrl=url+indName+"/_settings";
    # get original ES INDEX before update max_result_window value
    originalJson=GetIndexJson(indName,url);
    originalJson=json.loads(originalJson)

    response = requests.put(requrl,data=jsonData,headers=headers)
    # get modified ES INDEX after update max_result_window value
    modifiedJson=GetIndexJson(indName,url);
    modifiedJson=json.loads(modifiedJson)

    if(response.status_code==200):
      print("---------------------Success-------------------")
      # save user operation log by calling ESUsrOpLog()
      context={}
      action="ESIndexMgr"
      OpType="Edit Max_Result_Window"
      context['OriginalFormat']=originalJson
      context['ModifiedFormat']=modifiedJson
      context=json.dumps(context)
      try:
        ESUsrOpLog(saveuserid,saveusername,usergroupname,action,savecluster,indName,OpType,reqjson,context)
      except:
        print(">>>>>>>>>>>>>>>>>Write UserOpLog Error<<<<<<<<<<<<<<<<<<<<<<<<<")

    else:
      print("---------------------Failed2--------------------")

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>response:::"+str(response.text))
    return HttpResponse(response.text);    


def addFields(request, is_mobile=False, is_embeddable=False):
    # name=json.loads(request.POST.get('indexName', '{}'))
    indName=request.GET.get('indexName')
    cluster=request.GET.get('cluster')
    if (cluster==cluster1):
      url=url1
    elif(cluster==cluster2):
      url=url2
    elif(cluster==cluster5):
      url=url5
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return
    reqUrl=str(url)+str(indName)
    response = requests.get(reqUrl)
    print(">>>>>>>>>>>>>>>>>>>>>>>>response.text<<<<<<<<<<<<<<<<<<<<<<<")
    print(response.text)
    dictResponse=json.loads(response.text)
    print(dictResponse[indName]['mappings'].keys())
    indType=dictResponse[indName]['mappings'].keys()
    stringType=','.join(indType)

    editor_id = request.GET.get('editor')
    editor_type = request.GET.get('type', 'elasticsearch')

    if editor_type == 'notebook' or request.GET.get('notebook'):
      return notebook(request)

    if editor_id:  # Open existing saved editor document
      document = Document2.objects.get(id=editor_id)
      editor_type = document.type.rsplit('-', 1)[-1]

    template = 'index_fields_editor.mako'
    if is_mobile:
      template = 'index_fields_editor.mako'

    return render(template, request, {
      'editor_id': editor_id or None,
      'notebooks_json': '{}',
      'is_embeddable': request.GET.get('is_embeddable', False),
      'editor_type': editor_type,
      'name':indName,
      'stringType':stringType,
      'myurl':url,
      'clustername':cluster,
      'options_json': json.dumps({
        'languages': get_ordered_interpreters(request.user),
        'mode': 'editor',
        'is_optimizer_enabled': has_optimizer(),
        'is_navigator_enabled': has_navigator(request.user),
        'editor_type': editor_type,
        'mobile': is_mobile
      })
  })

@csrf_exempt
def getJsonAddFields(request):
    headers={
      'Content-Type':"application/json;charset=UTF-8"
    }

    saveuserid = json.loads(request.POST.get('myUserId','{}'))
    saveusername = json.loads(request.POST.get('myUserName','{}'))
    usergroupname = json.loads(request.POST.get('myWorkGroup','{}'))
    print("---------------------------------saveusername:"+str(saveusername))
    print("---------------------------------usergroupname:"+str(usergroupname))

    indName=json.loads(request.POST.get('indexName', '{}'))
    addFieldJson = json.loads(request.POST.get('addFieldJson', '{}'))
    url= json.loads(request.POST.get('url', '{}'))
    clustername=json.loads(request.POST.get('mycluster', '{}'))
    jsonData=json.dumps(addFieldJson)
    arrayType = json.loads(request.POST.get('arrayType', '{}'))
    lenArrayType=len(arrayType)
    for i in range(lenArrayType):
      if (arrayType[i]!="_default_"):
        print(arrayType[i]);
        reqUrl=str(url)+str(indName)+"/_mapping/"+str(arrayType[i])
        print(reqUrl)
        print(addFieldJson)
        originalJson=GetIndexJson(indName,url);
        originalJson=json.loads(originalJson)
        response = requests.put(reqUrl,data=jsonData,headers=headers)
        modifiedJson=GetIndexJson(indName,url);
        modifiedJson=json.loads(modifiedJson)
        if(response.status_code==200):
          context={}
          action="ESIndexMgr"
          OpType="Add Index Fields"
          context['OriginalFormat']=originalJson
          context['ModifiedFormat']=modifiedJson
          context=json.dumps(context)
          try:
            ESUsrOpLog(saveuserid,saveusername,usergroupname,action,clustername,indName,OpType,addFieldJson,context)
          except:
            print(">>>>>>>>>>>>>>>>>Write UserOpLog Error<<<<<<<<<<<<<<<<<<<<<<<<<")

        return HttpResponse(response.text)

def deleteIndex(request):
    
    saveuseid = json.loads(request.POST.get('myUserId','{}'))
    saveusername = json.loads(request.POST.get('myUserName','{}'))
    usergroupname = json.loads(request.POST.get('myWorkGroup','{}'))
    print("---------------------------------saveusername:"+str(saveusername))
    print("---------------------------------usergroupname:"+str(usergroupname))

    indexname = json.loads(request.POST.get('indexName', '{}'))
    cluster=json.loads(request.POST.get('cluster', '{}'))

    if (cluster==cluster1):
      url=url1
    elif(cluster==cluster2):
      url=url2
    elif(cluster==cluster5):
      url=url5
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return
    reqUrl=str(url)+str(indexname)

    originalJson=GetIndexJson(indexname,url);
    originalJson=json.loads(originalJson)
    response = requests.delete(reqUrl)
    modifiedJson=""
    

    print(">>>>>>>>>>>>>>>>>>>>>>>response:::"+response.text);
    if(response.status_code==200):
      print("---------------------Success-------------------")
      context={}
      action="ESIndexMgr"
      OpType="Delete Index"
      context['OriginalFormat']=originalJson
      context['ModifiedFormat']=modifiedJson
      context=json.dumps(context)
      try:
        ESUsrOpLog(saveuseid,saveusername,usergroupname,action,cluster,indexname,OpType,"",context)
      except:
        print(">>>>>>>>>>>>>>>>>Write UserOpLog Error<<<<<<<<<<<<<<<<<<<<<<<<<")
        
    else:
      print("---------------------Failed1--------------------")
    return HttpResponse(response.text);
