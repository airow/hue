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
    self.connection = Database.connect(**self._conn_params)

  @property
  def _conn_params(self):
    params = {
      'host': self.options['host'],
      'port': int(self.options['port'])
    }

    return params




  
  
  def close(self):
    self.connection.close()

  def execute_statement(self, statement):
    cursor = self.connection.cursor()
    cursor.execute(statement)   
    #self.connection.commit()

    if cursor.description:
      columns = [{'name': column[0], 'type': _convert_types(column[1])} for column in cursor.description]
    else:
      columns = []
    return self.data_table_cls(cursor, columns)

  def get_datasource(self):
    cursor = self.connection.cursor()
    cursor.execute("SHOW TABLES")
    # self.connection.commit()
    databases = [row[0] for row in cursor.fetchall()]
    return databases

  def get_databases(self):
    datasource = self.get_datasource()
    return datasource


  def get_tables(self, database, table_names=[]):
    return [database]


  def get_columns(self, database, table, names_only=False):
    table_columns = self.execute_statement("SELECT * FROM %s.%s LIMIT 0" % (database, table))

    if names_only:
      columns = [col['name'] for col in table_columns.columns_description]
    else:
      columns = table_columns.columns_description
    return columns


  def get_sample_data(self, database, table, column=None, limit=100):
    column = '`%s`' % column if column else '*'
    statement = "SELECT %s FROM `%s`.`%s` LIMIT %d" % (column, database, table, limit)
    return self.execute_statement(statement)
