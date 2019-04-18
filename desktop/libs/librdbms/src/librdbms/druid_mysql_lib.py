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
import json
import datetime
import dateutil
import time
import logging
import urllib2
import pandas as pd

from dateutil import tz

try:
    import MySQLdb as Database
except ImportError, e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading MySQLdb module: %s" % e)

# We want version (1, 2, 1, 'final', 2) or later. We can't just use
# lexicographic ordering in this check because then (1, 2, 1, 'gamma')
# inadvertently passes the version test.
version = Database.version_info
if (version < (1,2,1) or (version[:3] == (1, 2, 1) and
        (len(version) < 5 or version[3] != 'final' or version[4] < 2))):
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("MySQLdb-1.2.1p2 or newer is required; you have %s" % Database.__version__)

from django.utils.translation import ugettext as _
from MySQLdb.converters import FIELD_TYPE

from librdbms.server.rdbms_base_lib import BaseRDBMSDataTable, BaseRDBMSResult, BaseRDMSClient


LOG = logging.getLogger(__name__)


class DataTable(BaseRDBMSDataTable): pass


class Result(BaseRDBMSResult): pass


def _convert_types(t):
  if t == FIELD_TYPE.DECIMAL:
    return 'DECIMAL_TYPE'
  elif t == FIELD_TYPE.TINY:
    return 'TINYINT_TYPE'
  elif t == FIELD_TYPE.SHORT:
    return 'SMALLINT_TYPE'
  elif t == FIELD_TYPE.LONG:
    return 'BIGINT_TYPE'
  elif t == FIELD_TYPE.FLOAT:
    return 'FLOAT_TYPE'
  elif t == FIELD_TYPE.DOUBLE:
    return 'DOUBLE_TYPE'
  elif t == FIELD_TYPE.NULL:
    return 'NULL_TYPE'
  elif t == FIELD_TYPE.LONGLONG:
    return 'BIGINT_TYPE'
  elif t == FIELD_TYPE.INT24:
    return 'INT_TYPE'
  elif t == FIELD_TYPE.TIMESTAMP:
    return 'TIMESTAMP_TYPE'
  elif t == FIELD_TYPE.DATE:
    return 'DATE_TYPE'
  elif t == FIELD_TYPE.YEAR:
    return 'INT_TYPE'
  elif t == FIELD_TYPE.NEWDATE:
    return 'DATE_TYPE'
  elif t == FIELD_TYPE.VARCHAR:
    return 'VARCHAR_TYPE'
  elif t == FIELD_TYPE.BIT:
    return 'BOOLEAN_TYPE'
  elif t == FIELD_TYPE.NEWDECIMAL:
    return 'DECIMAL_TYPE'
  elif t == FIELD_TYPE.ENUM:
    return 'INT_TYPE'
  elif t == FIELD_TYPE.SET:
    return 'ARRAY_TYPE'
  elif t == FIELD_TYPE.TINY_BLOB:
    return 'BINARY_TYPE'
  elif t == FIELD_TYPE.MEDIUM_BLOB:
    return 'BINARY_TYPE'
  elif t == FIELD_TYPE.LONG_BLOB:
    return 'BINARY_TYPE'
  else:
    return 'STRING_TYPE'


class DruidMySQLClient():
  """Same API as Beeswax"""

  data_table_cls = DataTable
  result_cls = Result

  def __init__(self, options):
    self.options = options
    #self.url = options['url']
    #self.connection = Database.connect(**self._conn_params)

  @property
  def _conn_params(self):
    params = {
      'host': self.options[self.database+'.host'],
      'port': int(self.options[self.database+'.port'])
    }

    return params

  
  def close(self):
    #self.connection.close()
	print('close');				


  def execute_sql(self, sql, database):
    self.queryUrl = self.options[database+'.queryUrl']                                                      
    test_data='{"query":"'+ sql+'"}'
    requrl = self.queryUrl
    print(requrl)
    print("data:"+str(test_data));
    test_data=test_data.encode('utf-8')
    print(">>>>>>>>>>>>>>>>>>"+sql+"<<<<<<<<<<<<<<<<<<<<<")
    req = urllib2.Request(url=requrl, data=test_data, headers={'Content-Type' : 'application/json'})
    
    res_data = urllib2.urlopen(req)
    # print(res_data)
    res = res_data.read()
    # print(">>>>>>>>>>>>>>>>>>"+res+"<<<<<<<<<<<<<<<<<<<<<")
    # parsed = pd.read_table(res);
    resut=json.loads(res)
    return resut


  def execute_statement(self, statement, database):
    print('-----------------------------execute_statement-----------------------------')
    			
    ind_semicolon=statement.find(";")#find("\;")
																				  
    if(ind_semicolon!=-1):
      lower_statement=statement[0:ind_semicolon]
      lower_statement=lower_statement.lower()
      statement=statement[0:ind_semicolon]																		  
    else:
      lower_statement=statement.lower()
    
    ind_where=lower_statement.find("where")
    sub_string1=statement[0:ind_where]
    sub_string2=statement[ind_where:]
    sub_string2=sub_string2.replace("`","")
    statement=sub_string1+sub_string2
    lower_statement=statement.lower()										   
    list_lower_statement=lower_statement.split()
    list_statement=statement.split()
    
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
    
    ind_from=list_lower_statement.index("from")
    table_name=list_statement[ind_from+1]
    statement=statement.replace(table_name+".","")
    list_statement=statement.split()

    print('*************************statement:'+statement+'*****************************')
    if(cmp(list_lower_statement[0],"select")==0):  
      ind= lower_statement.find("limit") 
      if(ind==-1):
        print('--------------------------ERROR:No limit clause---------------------')
        return

      ind_limit=list_lower_statement.index("limit")
      limit_value=list_lower_statement[ind_limit+1]
      ind_comma=limit_value.find(",")
      if(ind_comma!=-1):
        limit_value=limit_value[ind_comma+1:]
      print('---------------------limit_value:'+limit_value+'--------------------')
																				   
      druid_limit_value=8000
      
      if(int(limit_value)>druid_limit_value):
        print('------------More than '+str(druid_limit_value)+' traces is not allowed--------------')
        return

      ind_time=[idx for idx, e in enumerate(list_lower_statement) if e=="__time"]
      if len(ind_time)<2:
        print("---------len(ind_time):"+str(len(ind_time))+"-----------------")
        print("A time range is needed.")
        return    

      utc=tz.tzutc()

      # get time string from query statement and parse them to date format
      time1=list_statement[ind_time[0]+2]
      time2=list_statement[ind_time[1]+2]
      time1_date=dateutil.parser.parse(time1)
      time2_date=dateutil.parser.parse(time2)
      print time1_date
      print time2_date
      part_time1=time1[10:]
      ind_plus=time1.find('+')
      ind_minus=part_time1.find('-')
      str_utcoffset="+00:00"
      if(ind_plus!=-1):
        str_utcoffset=time1[ind_plus:len(time1)-1]
        print(str_utcoffset)
      elif(ind_minus!=-1):
        str_utcoffset=part_time1[ind_minus:len(part_time1)-1]
        print(str_utcoffset)

      utcoffset= time1_date.utcoffset()

      if((time1_date.tzinfo==None)|(time2_date.tzinfo==None)):
        time1_date=time1_date.replace(tzinfo=utc)
        time2_date=time2_date.replace(tzinfo=utc)

      time1_date=time1_date.astimezone(utc)
      time2_date=time2_date.astimezone(utc)
      print time1_date
      print time2_date

      # time difference and time range limit
      time_difference=time2_date-time1_date
      print('----------------------------time_difference:'+str(time_difference))
      
      # use utc time to replace original query time
      list_statement[ind_time[0]+2]="'"+time1_date.strftime("%Y-%m-%dT%H:%M:%S.%f")+"'"
      list_statement[ind_time[1]+2]="'"+time2_date.strftime("%Y-%m-%dT%H:%M:%S.%f")+"'"
   
      time_difference_limit=7

      if(time_difference.days>time_difference_limit):
        print('----------Query of more than '+str(time_difference_limit)+' days is not allowed----------')
        return

      # self.database = database
      # self.connection = Database.connect(**self._conn_params)			   
      # cursor = self.connection.cursor()
      # cursor.execute(statement)   
      #self.connection.commit()

      # if cursor.description:
      #   columns = [{'name': column[0], 'type': _convert_types(column[1])} for column in cursor.description]
      # else:
      #   columns = []
      # return self.data_table_cls(cursor, columns)

      # make up a query string
      list2str_statement=' '.join(list_statement)
      print('------------------list2str_statement--------------------')
      print(list2str_statement)
      print('----------------------statement----------------------')
      print(statement)
      print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>result<<<<<<<<<<<<<<<<<<")
      result = self.execute_sql(list2str_statement, database)
      
      returndata={'data':result,'offset':utcoffset,'str_offset':str_utcoffset}
      return returndata								
				   


  def get_datasource(self):
    cursor = self.connection.cursor()
    cursor.execute("SHOW TABLES")
    # self.connection.commit()
    databases = [row[0] for row in cursor.fetchall()]
    return databases

  def get_datasourceMapping(self,database):
    try:
      self.url = self.options[database+'.queryurl']
      tables = pd.read_json(self.url)[0].tolist()
    except urllib2.URLError as ex:
      tables = []
    return tables 

  def get_databases(self):
    print('clusters:')
    print(self.options['clusters'])
    clusters = self.options['clusters']

    databases = clusters.split(",")
    return databases


  def get_tables(self, database, table_names=[]):
    datasource = self.execute_sql('SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=\'druid\'', database)

    tables = [row['TABLE_NAME'] for row in datasource] 
    return tables


  def get_columns(self, database, table, names_only=False):
    print('druid database:')
    print(database)
    table_columns = self.execute_sql('SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = \'druid\' AND TABLE_NAME = \''+table+'\'', database)

    if names_only:
      columns = [dict(name=row['COLUMN_NAME']) for row in table_columns] 
      
    else:
      columns = [dict(name=row['COLUMN_NAME'], type=row['DATA_TYPE']) for row in table_columns]
    return columns


  def get_sample_data(self, database, table, column=None, limit=100):
    column = '`%s`' % column if column else '*'
    statement = "SELECT %s FROM `%s`.`%s` LIMIT %d" % (column, database, table, limit)
    return self.execute_statement(statement,database)

  

