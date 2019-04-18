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
from kafka import KafkaConsumer
from kafka import KafkaProducer

import urllib 
import urllib2
import requests

from desktop.lib.django_util import render
from django.views.decorators.csrf import csrf_exempt
import datetime
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


cluster1="ESBiz"
url1="http://hdpjntest.chinacloudapp.cn:12200/"
cluster2="ESLog"
url2="http://hdpjntest.chinacloudapp.cn:12200/"
cluster3="esbiz"
url3="http://hdpjntest.chinacloudapp.cn:12200/"
cluster4="eslog"
url4="http://hdpjntest.chinacloudapp.cn:12200/"

# cluster1="ESBiz"
# url1="http://192.168.2.237:12200/"
# cluster2="ESLog"
# url2="http://192.168.2.244:12200/"
# cluster3="esbiz"
# url3="http://192.168.2.237:12200/"
# cluster4="eslog"
# url4="http://192.168.2.244:12200/"


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

def ESUsrOpLog(saveusername,usergroupname,action=None,cluster=None,TableName=None,OpType=None,OpContent=None,context=None):
  now_time=datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
  producer = KafkaProducer(bootstrap_servers='telddruidteal.chinacloudapp.cn:9095')
  save_data={}
  save_data['AppCode']=str(usergroupname)
  save_data['ModuleCode']='HUE'
  #UserID value 
  save_data['UserID']=str(saveusername)
  save_data['time']=str(now_time)
  save_data['Action']=action
  save_data['Ext10']=cluster
  save_data['Ext11']=TableName
  save_data['Ext12']=OpType
  save_data['Ext13']=OpContent
  save_data['Context']=context
  save_data['ExtColumnNames']="Ext10:ClusteName,Ext11:TargetTable,Ext12:OpType,Ext13:OpJson"
  msg=json.dumps(save_data)

  # index_json={"UserQueryLog":str(save_data)}
  # msg=json.dumps(index_json)
  print("-------------------producer.send()------------------")
  producer.send("test_useroplog",msg,partition=0)
  producer.close()


def getJson(request):
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    flag = json.loads(request.POST.get('flag', '{}'))
    indexJson = json.loads(request.POST.get('indexJson', '{}'))
    indexname = json.loads(request.POST.get('indexName', '{}'))
    cluster = json.loads(request.POST.get('inputCluster', '{}'))

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
        context=context
        ESUsrOpLog(saveusername,usergroupname,action,cluster,indexname,OpType,indexJson,context)
        # save_statement="Create Index"
        # now_time=datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
        # producer = KafkaProducer(bootstrap_servers='telddruidteal.chinacloudapp.cn:9095')
        # save_data={}
        # save_data['user']=str(request.user)
        # save_data['time']=str(now_time)
        # save_data['op']=str(save_statement)
        # index_json={"UserESOpLog":str(save_data)}
        # msg=json.dumps(index_json)
        # print("-------------------producer.send()------------------")
        # producer.send("test_userquerylog",msg,partition=0)
        # producer.close()
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
        context=context
        ESUsrOpLog(saveusername,usergroupname,action,cluster,indexname,OpType,indexJson,context)
      return result;
    elif(flag==3): 
      # templateind=indexname.find('_template');
      # indexname=indexname[0:templateind];
      data=json.dumps(indexJson); 
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^indexData:"+str(data));
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


def createTemplate(indexJson,indexname,cluster,partitionGranularity=""):
    if (cluster==cluster3):
      url=url3
    elif(cluster==cluster4):
      url=url4
    reqUrl=str(url)+"_template/"+str(indexname)+"_template"

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
    # if (cluster==url1):
    #   clustername="ES_BZ"
    # elif(cluster==url2):
    #   clustername="ES"
    # else:
    #   print("---------------------No cluster--------------------")
    #   return;
    if (cluster==cluster1):
          clustername="ES_BZ"
    elif(cluster==cluster2):
      clustername="ES"
    else:
      print("---------------------No cluster--------------------")
      return;    
    print(str(partitionGranularity));
    response = requests.get("http://configcenter.teld.local:8777/api/get?key=TTP.SG.InternalNgx")
    dictResponse=json.loads(response.text)
    print(dictResponse)
    result_content=dictResponse['result_content']
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
    response2 = requests.get(sg_url);
    dictResponse2=json.loads(response2.text)
    state=dictResponse2['state']
    if (state==0):
      print("SG Service ERROR!");
      return;
    else:
      print("SG Service SUCCESS!");
      return;

def EditMaxResultWindow(request, is_mobile=False, is_embeddable=False):
    indName=request.GET.get('indexName')
    cluster=request.GET.get('cluster')
    if (cluster==cluster1):
      url=url1
    elif(cluster==cluster2):
      url=url2
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return
    reqUrl=str(url)+str(indName)
    response = requests.get(reqUrl)
    print(response.text)
    print(type(response.text))

    dictResponse=json.loads(response.text)
    # print(dictResponse[indName]['mappings'].keys())
    # print("------------------Alias:---"+str(dictResponse[indName]['aliases'].keys()))
    # indType=dictResponse[indName]['mappings'].keys()
    # indAliases=dictResponse[indName]['aliases'].keys()
    if(dictResponse[indName]['settings']['index'].has_key('max_result_window')):
      nummaxresultwindow=dictResponse[indName]['settings']['index']['max_result_window']
    else:
      nummaxresultwindow=""

    if(nummaxresultwindow!=None):
      strnummaxresultwindow=str(nummaxresultwindow);
    else:
      strnummaxresultwindow="";
    # stringType=','.join(indType)
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
    if (cluster==cluster1):
      url=url1
    elif(cluster==cluster2):
      url=url2
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
    jsonData=json.dumps(aliasJson);
    requrl=url+"_aliases";
    response = requests.post(requrl,data=jsonData,headers=headers)

    if(response.status_code==200):
      print("---------------------Success-------------------")
      # return True;
    else:
      print("---------------------Failed2--------------------")
      # return False
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>response:::"+str(response.text))
    return HttpResponse(response.text);


def modifyMxRsltWin(request):
    max_result_window_value=500000
    headers={
      'Content-Type':"application/json;charset=UTF-8"
    }
    indName=json.loads(request.POST.get('indexName', '{}'))
    MxRsltWinnum = json.loads(request.POST.get('MxRsltWinnum', '{}'))
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
    response = requests.put(requrl,data=jsonData,headers=headers)

    if(response.status_code==200):
      print("---------------------Success-------------------")
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
    indName=json.loads(request.POST.get('indexName', '{}'))
    addFieldJson = json.loads(request.POST.get('addFieldJson', '{}'))
    url= json.loads(request.POST.get('url', '{}'))
    jsonData=json.dumps(addFieldJson)
    arrayType = json.loads(request.POST.get('arrayType', '{}'))
    lenArrayType=len(arrayType)
    for i in range(lenArrayType):
      if (arrayType[i]!="_default_"):
        print(arrayType[i]);
        reqUrl=str(url)+str(indName)+"/_mapping/"+str(arrayType[i])
        print(reqUrl)
        print(addFieldJson)
        response = requests.put(reqUrl,data=jsonData,headers=headers)
        return HttpResponse(response.text)

def deleteIndex(request):
    indexname = json.loads(request.POST.get('indexName', '{}'))
    cluster=json.loads(request.POST.get('cluster', '{}'))

    if (cluster==cluster1):
      url=url1
    elif(cluster==cluster2):
      url=url2
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return
    reqUrl=str(url)+str(indexname)
    response = requests.delete(reqUrl)
    print(">>>>>>>>>>>>>>>>>>>>>>>response:::"+response.text);
    if(response.status_code==200):
      print("---------------------Success-------------------")
    else:
      print("---------------------Failed1--------------------")
    return HttpResponse(response.text);
