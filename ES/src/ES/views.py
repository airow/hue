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
#-*- encoding: utf-8 -*-
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

def addTemplates(request, is_mobile=False, is_embeddable=False):
  editor_id = request.GET.get('editor')
  editor_type = request.GET.get('type', 'template')

  if editor_type == 'notebook' or request.GET.get('notebook'):
    return notebook(request)

  if editor_id:  # Open existing saved editor document
    document = Document2.objects.get(id=editor_id)
    editor_type = document.type.rsplit('-', 1)[-1]

  template = 'template_editor.mako'
  if is_mobile:
    template = 'editor_m.mako'

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


def index(request, is_mobile=False, is_embeddable=False):
      
  editor_id = request.GET.get('editor')
  editor_type = request.GET.get('type', 'elasticsearch')

  if editor_type == 'notebook' or request.GET.get('notebook'):
    return notebook(request)

  if editor_id:  # Open existing saved editor document
    document = Document2.objects.get(id=editor_id)
    editor_type = document.type.rsplit('-', 1)[-1]

  template = 'editor.mako'
  if is_mobile:
    template = 'editor_m.mako'

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


def getJson(request):
    flag = json.loads(request.POST.get('flag', '{}'))
    indexJson = json.loads(request.POST.get('indexJson', '{}'))
    indexname = json.loads(request.POST.get('indexName', '{}'))
    cluster = json.loads(request.POST.get('inputCluster', '{}'))
    partitionGranularity=json.loads(request.POST.get('partitionGranularity', '{}'))
    if(flag==1):
        
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^indexJson:"+str(indexJson));
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^indexname:"+str(indexname));
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^cluster:"+str(cluster));
      data=json.dumps(indexJson);
    
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^indexData:"+str(data));
      result= createIndex(data,indexname,cluster);
      return result;
    elif(flag==2):

      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^indexJson:"+str(indexJson));
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^indexname:"+str(indexname));
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^cluster:"+str(cluster));
      data=json.dumps(indexJson);
    
      print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^indexData:"+str(data));
      result= createTemplate(data,indexname,cluster,partitionGranularity);
      return result;
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>No JSON<<<<<<<<<<<<<<<<<<<<<<<<<<");
      return false;
    

def deleteIndex(request):
    indexname = json.loads(request.POST.get('indexName', '{}'))
    cluster=json.loads(request.POST.get('cluster', '{}'))
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^indexname:"+str(indexname));
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^cluster:"+str(cluster));

    if (cluster==cluster1):
      url=url1
    elif(cluster==cluster2):
      url=url2
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>url:::::::"+url)
    reqUrl=str(url)+str(indexname)
    response = requests.delete(reqUrl)
    print(">>>>>>>>>>>>>>>>>>>>>>>response:::"+response.text);
    if(response.status_code==200):
      print("---------------------Success-------------------")
    else:
      print("---------------------Failed1--------------------")
    return HttpResponse(response.text);

def createIndex(indexJson,indexname,cluster):
    reqUrl=str(cluster)+str(indexname)
    # reqUrl="http://hdpjntest.chinacloudapp.cn:12200/"+str(indexname)
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


def createTemplate(indexJson,indexname,cluster,partitionGranularity):
    reqUrl=str(cluster)+"_template/"+str(indexname)+"_template"
    # reqUrl="http://hdpjntest.chinacloudapp.cn:12200/"+str(indexname)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>reqURL:"+reqUrl)
    headers={
      'Content-Type':"application/json;charset=UTF-8"
    }
    response = requests.put(reqUrl,data=indexJson,headers=headers)

    if(response.status_code==200):
      sgService(indexname,cluster,partitionGranularity);
      print("---------------------Success-------------------")
      # return True;
    else:
      print("---------------------Failed2--------------------")
      # return False
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>response:::"+str(response.text))
    return HttpResponse(response.text);


def sgService(indexname,cluster,partitionGranularity):
    if (cluster==url1):
      clustername="ES_BZ"
    elif(cluster==url2):
      clustername="ES"
    else:
      print("---------------------No cluster--------------------")
      return;
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
    


def addFields(request, is_mobile=False, is_embeddable=False):
    # name=json.loads(request.POST.get('indexName', '{}'))
    print("----------------------------name: "+request.GET.get('indexName')+"---------------------------")
    print("----------------------------cluster: "+request.GET.get('cluster')+"---------------------------")
    indName=request.GET.get('indexName')
    cluster=request.GET.get('cluster')
    if (cluster==cluster1):
      url=url1
    elif(cluster==cluster2):
      url=url2
    else:
      print(">>>>>>>>>>>>>>>>>>>>>>>>Error Getting Cluster!<<<<<<<<<<<<<<<<<<<<<<<")
      return
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>url:::::::"+url)
    reqUrl=str(url)+str(indName)
    response = requests.get(reqUrl)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print(response)
    print(response.text)
    print(type(response.text))
    print("--------------------------------------------------")
    dictResponse=json.loads(response.text)
    print(dictResponse)
    print("--------------------------------------------------")
    print(dictResponse[indName]['mappings'].keys())
    indType=dictResponse[indName]['mappings'].keys()
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^type(indType):"+str(type(indType)))
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^type(url):"+str(type(url)))
    stringType=','.join(indType)
    print("------------------------------stringType:"+stringType)

    editor_id = request.GET.get('editor')
    editor_type = request.GET.get('type', 'elasticsearch')

    if editor_type == 'notebook' or request.GET.get('notebook'):
      return notebook(request)

    if editor_id:  # Open existing saved editor document
      document = Document2.objects.get(id=editor_id)
      editor_type = document.type.rsplit('-', 1)[-1]

    template = 'fields_editor.mako'
    if is_mobile:
      template = 'editor_m.mako'

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


def editAlias(request, is_mobile=False, is_embeddable=False):
    print("----------------------------name: "+request.GET.get('indexName')+"---------------------------")
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
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5%555555")
    print(response)
    print(response.text)
    print(type(response.text))
    # dictresponse=json.loads(response.text)
    # if dictresponse['error']['root_cause'][0]['type']=="index_not_found_exception":
    #   print("--------------------Index Not Found.-----------------------")
    #   editor_id = request.GET.get('editor')
    #   editor_type = request.GET.get('type', 'elasticsearch')

    #   if editor_type == 'notebook' or request.GET.get('notebook'):
    #     return notebook(request)

    #   if editor_id:  # Open existing saved editor document
    #     document = Document2.objects.get(id=editor_id)
    #     editor_type = document.type.rsplit('-', 1)[-1]
    #   template = 'editor.mako'
    #   if is_mobile:
    #     template = 'editor.mako'
    #   return render(template, request, {
    #     'editor_id': editor_id or None,
    #     'notebooks_json': '{}',
    #     'is_embeddable': request.GET.get('is_embeddable', False),
    #     'editor_type': editor_type,
    #     'options_json': json.dumps({
    #       'languages': get_ordered_interpreters(request.user),
    #       'mode': 'editor',
    #       'is_optimizer_enabled': has_optimizer(),
    #       'is_navigator_enabled': has_navigator(request.user),
    #       'editor_type': editor_type,
    #       'mobile': is_mobile
    #     })
    # })
    print(type(response.text))
    print("--------------------------------------------------")
    dictResponse=json.loads(response.text)
    print(dictResponse)
    print("--------------------------------------------------")
    print(dictResponse[indName]['mappings'].keys())
    print("------------------Alias:---"+str(dictResponse[indName]['aliases'].keys()))
    indType=dictResponse[indName]['mappings'].keys()
    indAliases=dictResponse[indName]['aliases'].keys()
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^type(indType):"+str(type(indType)))
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^type(indAliases):"+str(type(indAliases)))
    print("---------------------------------indAliases:-----"+str(indAliases))
    strindAliases=','.join(indAliases);
    print("---------------------------------strindAliases:-----"+strindAliases)
    # stringType=','.join(indType)
    # print("------------------------------stringType:"+stringType)
    editor_id = request.GET.get('editor')
    editor_type = request.GET.get('type', 'elasticsearch')

    if editor_type == 'notebook' or request.GET.get('notebook'):
      return notebook(request)

    if editor_id:  # Open existing saved editor document
      document = Document2.objects.get(id=editor_id)
      editor_type = document.type.rsplit('-', 1)[-1]
    template = 'edit_alias_editor.mako'
    if is_mobile:
      template = 'editor_m.mako'
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
  #   return render('alias_manage.mako', request, {
  #   # 'name': json.dumps(indName),
  #   # 'stringType':stringType,
  #   # 'json_jobs': json.dumps(Connlist,cls=JSONEncoderForHTML),
  #   # 'json_jobs': json.dumps(indName),
  # })

@csrf_exempt
def getJsonAddFields(request):
    headers={
      'Content-Type':"application/json;charset=UTF-8"
    }
    indName=json.loads(request.POST.get('indexName', '{}'))
    addFieldJson = json.loads(request.POST.get('addFieldJson', '{}'))
    url= json.loads(request.POST.get('url', '{}'))
    print("*****************************************url:"+url)
    jsonData=json.dumps(addFieldJson)
    print(jsonData)
    print("*************************************")
    print(indName)
    print(addFieldJson)
    arrayType = json.loads(request.POST.get('arrayType', '{}'))
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    print(arrayType)
    lenArrayType=len(arrayType)
    for i in range(lenArrayType):
      if (arrayType[i]!="_default_"):
        print(arrayType[i]);
        reqUrl=str(url)+str(indName)+"/_mapping/"+str(arrayType[i])
        print(reqUrl)
        print(addFieldJson)
        response = requests.put(reqUrl,data=jsonData,headers=headers)
        return HttpResponse(response.text)

def modifyAlias(request):
    headers={
      'Content-Type':"text/plain"
    }
    indName=json.loads(request.POST.get('indexName', '{}'))
    aliasJson = json.loads(request.POST.get('aliasJson', '{}'))
    url= json.loads(request.POST.get('url', '{}'))
    print("*****************************************url:"+url)
    print("*****************************************aliasJson:"+str(aliasJson))
    print("*****************************************indName:"+indName)
    jsonData=json.dumps(aliasJson);
    print(jsonData)
    print("*************************************")
    requrl=url+"_aliases";
    print("*****************************************requrl:"+requrl)
    response = requests.post(requrl,data=jsonData,headers=headers)

    if(response.status_code==200):
      print("---------------------Success-------------------")
      # return True;
    else:
      print("---------------------Failed2--------------------")
      # return False
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>response:::"+str(response.text))
    return HttpResponse(response.text);
    # print(indName)
    # print(addFieldJson)
    # arrayType = json.loads(request.POST.get('arrayType', '{}'))
    # print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    # print(arrayType)
    # lenArrayType=len(arrayType)
    # for i in range(lenArrayType):
    #   if (arrayType[i]!="_default_"):
    #     print(arrayType[i]);
    #     reqUrl=str(url)+str(indName)+"/_mapping/"+str(arrayType[i])
    #     print(reqUrl)
    #     print(addFieldJson)
    #     response = requests.put(reqUrl,data=jsonData,headers=headers)
    #     return HttpResponse(response.text)