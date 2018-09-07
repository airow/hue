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

import logging
import codecs 
import numpy as np
import os
#import pandas as pd
import csv
import json
import sys
import codecs
import logging

from django.utils.translation import ugettext as _
from beeswax.server import dbms
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode, smart_str
from librdbms.template_lib import TemplateClient, query_and_fetch
from beeswax.server.dbms import get_query_server_config, QueryServerException
from notebook.connectors.base import Api, QueryError, AuthenticationRequired
from django.shortcuts import HttpResponse 
from django.http import StreamingHttpResponse

LOG = logging.getLogger(__name__)


# Cache one JDBC connection by user for not saving user credentials
API_CACHE = {}


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except AuthenticationRequired, e:
      raise e
    except Exception, e:
      message = force_unicode(smart_str(e))
      if 'error occurred while trying to connect to the Java server' in message:
        raise QueryError(_('%s: is the DB Proxy server running?') % message)
      else:
        raise QueryError(message)
  return decorator


class TemplateApi(Api):

  def __init__(self, user, interpreter=None):
    global API_CACHE
    Api.__init__(self, user, interpreter=interpreter)

    self.db = None
    self.options = interpreter['options']

    if self.cache_key in API_CACHE:
      self.db = API_CACHE[self.cache_key]
    else:        
      self.db = API_CACHE[self.cache_key] = TemplateClient(self.options)

  def create_session(self, lang=None, properties=None):
    global API_CACHE
    props = super(TemplateApi, self).create_session(lang, properties)

    properties = dict([(p['name'], p['value']) for p in properties]) if properties is not None else {}
    props['properties'] = {} # We don't store passwords

    if self.db is None:
      self.db = API_CACHE[self.cache_key] = TemplateClient(self.options)

    if self.db is None:
      raise AuthenticationRequired()

    return props

  @query_error_handler
  def execute(self, notebook, snippet):
    if self.db is None:
      raise AuthenticationRequired()
    
    resultSet = query_and_fetch(self.db, snippet['statement'],snippet['database'],1000)
    print(type(resultSet))
    print(resultSet)
    # while i<len_tuple:
    # has_result_set = resultSet is not None
    data = resultSet[0]
    if data:
      has_result_set=True
    else:   
      has_result_set=False  
    # if 'errorMessage' in data[0]:
    #   raise Exception(data[0].get('exceptionStack'))
    print(has_result_set)
    print(data)
    return {
      'sync': True,
      'has_result_set': has_result_set,
      'result': {
        'has_more': False,
        'data': [row.values() for row in data] if has_result_set else [],
        'meta': [{
          'name': col,
          'type': '',
          'comment': ''
        } for col in data[0].keys()] if has_result_set else [],
        'type': 'table'
      }
    }

  @query_error_handler
  def check_status(self, notebook, snippet):
    return {'status': 'available'}

  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    return {
      'has_more': False,
      'data': [],
      'meta': [],
      'type': 'table'
    }

  @query_error_handler
  def fetch_result_metadata(self):
    pass

  @query_error_handler
  def cancel(self, notebook, snippet):
    return {'status': 0}

  def ReadFile(self,filePath,encoding):  
    with codecs.open(filePath,"r",encoding) as f:  
        return f.read() 

  def WriteFile(self,filePath,u,encoding):  
    with codecs.open(filePath,"w",encoding) as f:  
        f.write(u)  

  def is_number(self,s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

  def dict2csv(self,mydict,file):
      np.set_printoptions(suppress=True)
      # print('77777777777777777777777777777777777777777777')
      # print(file)
      f=codecs.open(file,'ab','utf_8_sig')
    # with open(file, 'ab') as f:
      wr = csv.writer(f, dialect='excel',delimiter=',',escapechar='\\')    # list=wr.read  ,quoting=csv.QUOTE_NONE
      for word in mydict: 
        # print("00000000000000000000000000000000000000000000000000\n")
        # print(word)
        # print("\n**************************************************\n") 
        i=len(word)
        temp=word
        wr.writerow(temp)         
      f.close()
      return f

  def download(self, notebook, snippet, format):
    #raise PopupException('Downloading is not supported yet')
    filepath='result.csv'
    np.set_printoptions(suppress=True)
    response=self.execute( notebook, snippet)
    if(os.path.exists(filepath)):
      os.remove(filepath)
    dictHead=response["result"]["meta"]
    # print("------------------------------dict_head-------------------------")
    # print(dictHead)
    mylist=[]
    while len(dictHead)>0 :
      temp=dictHead.pop()
      mylist.append(temp["name"])
    # mylist=pd.DataFrame(dictHead).to_dict('records')
    mylist.reverse()
    mylist=[mylist]
    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>mylist<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    # print(mylist)
    dictData=response["result"]["data"]
    # print("-----------------------------dict_data-------------------------------")
    # print(dictData)

    resultData=mylist+dictData
    #dictData.replace("\","\\")
    has_result_set = dictData is not None
    
    # print('11111111111111111111111111111111111111')
    file=self.dict2csv(resultData,filepath)
    # print('222222222222222222222222222222222')
    # file=self.dict2csv(dictData,filepath)
    # print('33333333333333333333333333333333333333333')
    csvfile = open(filepath, 'rb')
    # print('44444444444444444444444444444444444444444444444')
    # csvfile2=csvfile
    response =StreamingHttpResponse(csvfile)
     
    response['Content-Type']='application/octet-stream'  
    response['Content-Disposition']='attachment;filename="result.csv"'
    # content = self.ReadFile('result.csv',encoding='gbk')
    # self.WriteFile('result.csv',content,encoding='utf_8')  
    return response   

  def progress(self, snippet, logs):
    return 50

  @query_error_handler
  def close_statement(self, snippet):
    return {'status': -1}

  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    if self.db is None:
      raise AuthenticationRequired()

    assist = Assist(self.db)
    response = {'status': -1}

    if database is None:
      response['databases'] = assist.get_databases()
    elif table is None:
      tables_meta = []
      for t in assist.get_tables(database):
        tables_meta.append({'name': t, 'type': 'Table', 'comment': ''})
      response['tables_meta'] = tables_meta
    elif column is None:
      columns = assist.get_columns(database, table)
      response['columns'] = [col['name'] for col in columns]
      response['extended_columns'] = columns
    else:
      columns = assist.get_columns(database, table)
      response['name'] = next((col['name'] for col in columns if column == col['name']), '')
      response['type'] = next((col['type'] for col in columns if column == col['name']), '')

    response['status'] = 0
    return response

  @query_error_handler
  def get_sample_data(self, snippet, database=None, table=None, column=None):
    if self.db is None:
      raise AuthenticationRequired()

    assist = Assist(self.db)
    response = {'status': -1}

    sample_data, description = assist.get_sample_data(database, table, column)

    if sample_data:
      response['status'] = 0
      response['headers'] = [col[0] for col in description] if description else []
      response['rows'] = sample_data
    else:
      response['message'] = _('Failed to get sample data.')

    return response

  @property
  def cache_key(self):
    return '%s-%s' % (self.interpreter['name'], self.user.username)

class Assist():

  def __init__(self, db):
    self.db = db

  def get_databases(self):
    databases = self.db.get_databases()
    return databases

  def get_tables(self, database):
    tables = self.db.get_tables(database)
    return tables

  def get_columns(self, database, table):
    columns = self.db.get_columns(database, table)
    return columns

  def get_sample_data(self, database, table, column=None):
    column = column or '*'
    return query_and_fetch(self.db, 'SELECT %s FROM %s.%s' % (column, database, table))
