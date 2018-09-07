## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Edit Connection"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='connection') }


<div class="container-fluid">


  <div class="row-fluid">
    <div class="span2">
      <div id="connectionControls" class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Edit connection') }</li>
          <li class="active"><a href="#properties"><i class="fa fa-reorder"></i> ${ _('Properties') }</a></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="card card-small">
        <div class="alert alert-info"><h3>${ _('Properties') }</h3></div>
          <div class="card-body">
            <p>
              <form class="form-horizontal" id="connectionForm" action="${ url('oozie:edit_connections', connection=connection.id) }" method="POST">
                ${ csrf_token(request) | n,unicode }
              <fieldset>
                ${ utils.render_field(connection_form['Coon_type']) }
                ${ utils.render_field(connection_form['Coon_key']) }
                ${ utils.render_field(connection_form['Coon_value']) }
             </fieldset>
              <div class="form-actions center">
                <input class="btn btn-primary" type="submit" value="${ _('Save') }" />
                <a class="btn" onclick="history.back()">${ _('Back') }</a>
              </div>
            </form>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>






