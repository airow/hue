// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
/*
 * jHue selector plugin
 * it tranforms a select multiple into a searchable/selectable alphabetical list
 */
;
(function ($, window, document, undefined) {

  window.permssionsMapping = {
    get: function (app, action) {

      var returnValue = "";
      var perm = window.permssionsMapping[app];
      if (perm) {
        perm.action = perm.action || {};
        perm.action.access = "启用";
        var desc = perm.action[action];
        returnValue = perm.name + (desc ? "=>" + desc : "");
      }

      return returnValue;
    },
    about: {
      name: "关于"
    },
    beeswax: {
      name: "Hive"
    },
    filebrowser: {
      name: "File Browser-文件",
      action: { s3_access: "访问S3" }
    },
    hbase: {
      name: "Hbase",
      action: { write: "允许写入" }
    },
    impala: {
      name: "Impala-组件"
    },
    jobbrowser:{
      name: "Job Browser-作业"
    },
    jobsub:{
      name: "jobsub-子作业"
    },
    metastore: {
      name: "Table Browser-表浏览器",
      action: { write: "允许DDL操作" }
    },
    oozie: {
      name: "Workflow-工作流",
      action: {
        disable_editor_access: "禁止编辑",
        dashboard_jobs_access: "查看全部作业"
      }
    },
    pig:{
      name: "Pig-组件",
    },
    proxy:{
      name: "Proxy-组件",
    },
    rdbms:{
      name: "rdbms-关系数据库组件",
    },
    search:{
      name: "Search-组件",
    },      
    security: {
      name: "Security-安全性",
      action: {
        impersonate:"用户模拟"
      }
    },
    spark: {
      name: "Spark-组件"
    },
    sqoop: {
      name: "Sqoop-组件"
    },
    useradmin:{
      name: "用户管理",
      action: { 
        "access_view:useradmin:view_user": "查看他人个人资料",
        "access_view:useradmin:edit_user": "编辑个人资料",
       }
    },
    sqoop: {
      name: "zookeeper-组件"
    },
    indexer:{
      name: "Index Browser-索引浏览器"
    },
    metadata: {
      name: '元数据',
      action: { write: "编辑" }
    },
    notebook: {
      name: "notebook-笔记本"
    },
    scheduler:{
      name: "Scheduler-计划程序",        
    },
    dashboard:{
      name: "Dashboard-控制面板",
      action: {
        disable_editor_access: "禁止编辑",
        dashboard_jobs_access: "查看全部作业"
     }
    }
  };

})(jQuery, window, document);