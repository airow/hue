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
import os
import sys

import urllib
import pandas as pd
import urllib2
import json
import pymysql

LOG = logging.getLogger(__name__)


def query_and_fetch(db, statement, n=None):
  data = None
  statement = statement.rstrip(';')
  statement = statement.replace('.','/')
  data = db.execute_statement(statement,n)
  print data
  return data

class DruidClient():

  def __init__(self, options):
    self.options = options
    self.url = self.options['url']
    self.host = self.options['host']
    self.port = self.options['port']

  def execute_statement(self, statement, n=None):
        
    conn = pymysql.connect(host=self.host, port=int(self.port), charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    try:
        exc_result = 'ok'
        with conn.cursor() as cursor:
            cursor.execute(sql)
            list2 = []
            for i in cursor.fetchall():
                dict1 = {}
                for q in i.keys():
                    dict1[q] = str(i[q])
                list2.append(dict1)
            content = json.dumps(list2, encoding="UTF-8", ensure_ascii=False)
    except Exception:
        exc_result = 'error'
    finally:
        conn.close()

    # test_data = {'sql': statement}
    # test_data_urlencode = urllib.urlencode(test_data)
    # requrl = self.queryUrl
    # req = urllib2.Request(url=requrl, data=test_data_urlencode)
    # res_data = urllib2.urlopen(req)
    # res = res_data.read()
    # data = json.loads(res);
    return data, res

  def catAliases(self):
    parsed = pd.read_table(self.url + '/_cat/aliases?v', sep=r'\s+')
    alias = parsed['alias']
    index = parsed['index']
    return alias, index

  def _mappings(self, alias):
    requrl = self.url + "/"+alias+"/_mappings"
    req = urllib2.Request(url=requrl)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    data = json.loads(res);
    return data, res

  def get_databases(self):        
    alias,index = self.catAliases()
    #databases = [row for row in alias.tolist())] if False else ['huebyeshuebyes']
    databases = list(set(index.tolist()))
    return databases

  def get_tables(self, database):
    databaseMappings = self._mappings(database)
    mappings = databaseMappings[0][database]["mappings"]
    tables = [key for key in mappings if key != '_default_' ]
    return tables


  def get_columns(self, database, table, names_only=False):
    databaseMappings = self._mappings(database)
    mappings = databaseMappings[0][database]["mappings"]
    properties = mappings[table].get("properties")

    if names_only:
      columns = [key for key in properties]
    else:
      columns = [dict(name=key, type=properties[key]['type'], comment='') for key in properties]
    return columns 


  def get_sample_data(self, database, table, column=None, limit=100):
    column = '`%s`' % column if column else '*'
    statement = "SELECT %s FROM `%s`.`%s` LIMIT %d" % (column, database, table, limit)
    return self.execute_statement(statement)