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
import re
import logging
import os
import sys

import urllib
import pandas as pd
import urllib2
import json
reload(sys)
sys.setdefaultencoding('utf-8')
LOG = logging.getLogger(__name__)


def query_and_fetch(db, statement, database,n=None):
  data = None
  statement = statement.rstrip(';')
  # statement = statement.replace('.','/')
  print('>>>>>>>>>>> elaticsearch_lib.py query_and fetch statement:  '+statement)
  # print("------------------------------type(db):"+str(type(db)))
  # print(db)
  data = db.execute_statement(statement,database)
  # print data
				  
  return data

class ElasticsearchClient():

  def __init__(self, options):
    self.options = options
    #self.url = self.options['url']
    #self.queryUrl = self.options['queryUrl']

  def execute_statement(self, statement, database):
    print('*********************elasticsearch_lib.py ES:execute_statement************************************')																																												 
    utf8statement=statement.encode("utf-8")
    lastcharactor=utf8statement[-1]
    ind_lastcharactor=len(utf8statement)
    print("----------------------------ind_lastcharactor:"+str(ind_lastcharactor))
    print("----------------------------lastcharactor:"+lastcharactor)

    if(lastcharactor==";"):
      lower_statement=statement[0:(ind_lastcharactor-1)]
      statement=statement[0:(ind_lastcharactor-1)]																						
      lower_statement=lower_statement.lower()
    else:
      lower_statement=statement.lower()
    print(statement)
    print(lower_statement)
																			  
    list_lower_statement=lower_statement.split()
    list_statement=statement.split()
    print(">>>>>>>>>>>>>>>>>>>>list_lower_statement:")
    print(list_lower_statement)
    if(cmp(list_lower_statement[0],"update")==0):
      print('-------------------UPDATE operation is not allowed-----------------')
      return   
    if(cmp(list_lower_statement[0],"drop")==0):
      print('-------------------DROP operation is not allowed-----------------')
      return 
    if(cmp(list_lower_statement[0],"truncate")==0):
      print('-------------------TRUNCATE operation is not allowed-----------------')
      return 
    if(cmp(list_lower_statement[0],"delete")==0):
      print('-------------------DELETE operation is not allowed-----------------')
      return 
    if(cmp(list_lower_statement[0],"insert")==0):
      print('-------------------INSERT operation is not allowed-----------------')
      return    
    ind= lower_statement.find("limit") 
    if(ind==-1):
      print('--------------------------ERROR:No limit clause---------------------')
      return
    ind_from=list_lower_statement.index("from")
    table_name=list_statement[ind_from+1]
    statement=statement.replace(table_name+".","")
    ind_where=lower_statement.find("where")
    sub_string1=statement[0:ind_where]
    sub_string2=statement[ind_where:]
    sub_string2=sub_string2.replace("`","")
    statement=sub_string1+sub_string2
    print('>>>>>>>>>>>>>statement without tablename: '+statement+'<<<<<<<<<<<<<<<<')
    if(cmp(list_lower_statement[0],"select")==0): 
      ind_limit=list_lower_statement.index("limit")
      limit_value=list_lower_statement[ind_limit+1]
      ind_comma=limit_value.find(",")
      if(ind_comma!=-1):
        limit_value=limit_value[ind_comma+1:]
      print('---------------------limit_value:'+limit_value+'--------------------')
      es_limit_value=10000
      if(int(limit_value)>es_limit_value):
        print('------------More than '+str(es_limit_value)+' traces is not allowed--------------')
        return

      test_data = {'sql': statement}
      test_data_urlencode = urllib.urlencode(test_data)
      self.queryUrl = self.options[database+'.queryUrl']													  
																				  																				  
      requrl = self.queryUrl
      req = urllib2.Request(url=requrl, data=test_data_urlencode, headers={'Content-Type' : 'application/x-www-form-urlencoded;charset=UTF-8'})
      res_data = urllib2.urlopen(req)																								 			 
      res = res_data.read()																								 		
      data = json.loads(res);
      # print("-----------------------data:"+str(data))
      
      return data, res

  def catAliases(self,database):
    self.url = self.options[database+'.url']
    print("-1-1-1-1-------------------------111111111111111111111111")
    print(self.url)
    self.queryUrl = self.options[database+'.queryUrl']
    print("-2-2-2-2-------------------------222222222222222222222222")
    print(self.queryUrl)
    parsed = pd.read_table(self.url + '/_cat/indices?v', sep=r'\s+')
    parsed2=pd.read_table(self.url+'/_template')
    print("-3-3-3-3----------------------------33333333333333333")
    # print(parsed)
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<^^^^^^^^^^^^^^^^^^^^^^^^^^^^^>>>>>>>>>>>>>>>>>>")
    # print(parsed2)
    index = parsed.loc[parsed['status'] == 'open']['index']
    print("-4-4-4-4--------------------------4444444444444444444444")
    # print(index)
    return index

  def _mappings(self, database, alias):
    self.url = self.options[database+'.url']
    print("-5-5-5-5------------------------55555555555555555555555")
    print(self.url)
    self.queryUrl = self.options[database+'.queryUrl']
    print("-6-6-6-6----------------------------6666666666666666666")
    print(self.queryUrl)

    requrl = self.url + "/"+alias+"/_mappings"
    print("-7-7-7-7----------------------7777777777777777777777777")
    print(requrl)
    req = urllib2.Request(url=requrl)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    data = json.loads(res);
    print("-8-8-8-8-------------8888888888888888888888888")
    # print(data)
    print("-9-9-9-9----------------------9999999999999999999999999")
    # print(res)
    return data, res

  def get_databases(self):        
    
    print('clusters:')
    print(self.options['clusters'])
    clusters = self.options['clusters']

    databases = clusters.split(",")
    # print(databases)
    return databases

  def get_tables(self, database):
    print("0000000000000000000000000")
    print('database:')
    # print(database)
    
    index = self.catAliases(database)
    print("11111111111111111111111")
    # print(index)
    temp_tables=[elem for elem in index if str('.') not in str(elem)]
    # tables = list(set(index.tolist()))
    tables =temp_tables
    print("22222222222222222222222222222222222")
    # print(tables)
    return tables


  def get_columns(self, database, table, names_only=False):
    databaseMappings = self._mappings(database,table)
    mappings = databaseMappings[0][table]["mappings"]
    print("3333333333333333333333333333")
    # print(mappings)
    properties = mappings[mappings.keys()[0]].get("properties")
    print("44444444444444444444444444444444")
    # print(properties)

    if names_only:
      columns = [key for key in properties]
    else:
      columns = [dict(name=key, type=properties[key]['type'], comment='') for key in properties]
    print("555555555555555555555555555555")
    # print(columns)
    return columns 


  def get_sample_data(self, database, table, column=None, limit=100):
    column = '`%s`' % column if column else '*'
    print("6666666666666666666666666666666")
    # print(column)
    statement = "SELECT %s FROM `%s` LIMIT %d" % (column, table, limit)
    print("7777777777777777777777777777777777")
    # print(statement)
    print("888888888888888888888888888888888888")
    # print(self.execute_statement(statement,database))
    return self.execute_statement(statement,database)

