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
## ${name}  bbbbb ${stringType}
## <%!

## from django.utils.translation import ugettext as _

## from desktop import conf
## from desktop.lib.i18n import smart_unicode
## from desktop.views import _ko, antixss

## from metadata.conf import has_optimizer
## from notebook.conf import ENABLE_QUERY_BUILDER, ENABLE_QUERY_SCHEDULING, ENABLE_BATCH_EXECUTE, ENABLE_EXTERNAL_STATEMENT
## %>


## <%def name="topBar(suffix='')">

##  <div class="player-toolbar" data-bind="visible: $root.isPlayerMode() && $root.isFullscreenMode()" style="display: none;">
##     <div class="pull-right pointer" data-bind="click: function(){ hueUtils.exitFullScreen(); $root.isPlayerMode(false); $root.isFullscreenMode(false);  }"><i class="fa fa-times"></i></div>
##     <img src="${ static('desktop/art/icon_hue_48.png') }"  alt="${ _('Hue logo') }"/>
##     <!-- ko if: $root.selectedNotebook() -->
##     <h4 data-bind="text: $root.selectedNotebook().name"></h4>
##     <!-- /ko -->
##   </div>
## </%def>


## <%def name="commonHTML(is_embeddable=False, suffix='')">
<script src="${ static('desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.custom.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.contextMenu.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.ui.position.min.js') }"></script>

<script src="${ static('desktop/js/jquery.hdfstree.js') }"></script>
<script src="${ static('desktop/ext/js/markdown.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.hotkeys.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.mousewheel.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery.mCustomScrollbar.concat.min.js') }"></script>

<link rel="stylesheet" href="${ static('desktop/ext/css/jquery.contextMenu.min.css') }">
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.contextMenu.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.ui.position.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/jquery-2.2.3.min.js') }"></script>

<script src="${ static('desktop/ext/chosen/chosen.jquery.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/ko.charts.js') }"></script>
<script src="${ static('desktop/js/ko.editable.js') }"></script>

<script src="${ static('notebook/js/notebook.ko.js') }"></script>

<script src="${ static('oozie/js/coordinator-editor.ko.js') }"></script>
<script src="${ static('oozie/js/list-oozie-coordinator.ko.js') }"></script>
<script src="${ static('desktop/js/ko.selectize.js') }"></script>

<script src="${ static('desktop/ext/js/knockout.min.js') }"></script>
<script src="${ static('desktop/ext/js/knockout-mapping.min.js') }"></script>
<script src="${ static('desktop/ext/js/knockout.validation.min.js') }"></script>


## <script type="text/html" id="snippet${ suffix }">
  <div data-bind="visibleOnHover: { override: inFocus() || settingsVisible() || dbSelectionVisible() || $root.editorMode() || saveResultsModalVisible(), selector: '.hover-actions' }">
    <div class="snippet-container row-fluid" data-bind="visibleOnHover: { override: $root.editorMode() || inFocus() || saveResultsModalVisible(), selector: '.snippet-actions' }">
    <br></br>  
      <div class="airy" style="text-align: center">
        <span class="widget-label" >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Index Name: </span>
        <input type="text" disabled="true" data-bind='${name}' id="idxname" class="input-xlarge" validate="nonempty" >
      </div>
<div>
<br></br>
  <title>编辑表格数据</title>    
  <style type="text/css"> </style> 

  <form style="text-align:center" id="form1" name="form1" method="post" action="">    
<h3 align="center">编辑索引字段</h3>    
<table align="center" width="900" border="0" cellpadding="0" cellspacing="0" id="tabProduct">    
    <tr>    
      <td width="100" align="center" bgcolor="#EFEFEF" Name="Checked"><input style="display:none" type="checkbox" name="checkbox" value="checkbox" /></td>    
      <td width="200" bgcolor="#EFEFEF" Name="FieldName" EditType="TextBox">字段名</td>    
      <td width="250" bgcolor="#EFEFEF" Name="DataType" EditType="DropDownList" DataItems="{text:'text:模糊匹配，全文搜索',value:'text'},{text:'keyword:全词匹配，可排序，可聚合',value:'keyword'},{text:'以上两项',value:'two'},{text:'Integer',value:'integer'},{text:'Long',value:'long'},{text:'Short',value:'short'},{text:'Double',value:'double'},{text:'Float',value:'float'},{text:'Boolean',value:'boolean'},{text:'Date',value:'date'},{text:'Range',value:'range'}">数据类型</td>    

      <td width="210" bgcolor="#EFEFEF" Name="Format" EditType="TextBox">格式</td>       
    </tr>    
    <tr onclick="SetRowCanEdit(this)">    
      <td align="center" bgcolor="#FFFFFF"><input type="checkbox" name="checkbox2" value="checkbox" /></td>    
      <td bgcolor="#FFFFFF" Name="FieldName">field1</td>    
      <td bgcolor="#FFFFFF" Name="DataType" Value="text" EditType="DropDownList">text:模糊匹配，全文搜索</td>      
      <td bgcolor="#FFFFFF" Name="Format"></td>     
    </tr>    
    <tr onclick="SetRowCanEdit(this)">    
      <td align="center" bgcolor="#FFFFFF"><input type="checkbox" name="checkbox22" value="checkbox" /></td>    
      <td bgcolor="#FFFFFF" Name="FieldName">field2</td>    
      <td bgcolor="#FFFFFF" Name="DataType" Value="date" EditType="DropDownList">Date</td>    
      ## <td bgcolor="#FFFFFF">date</td>    
      <td bgcolor="#FFFFFF" Name="Format">yyyyMMddHHmmssSSSZ</td>    
    ##   <td bgcolor="#FFFFFF">0</td>    
    ## </tr>    
</table>    
    
<br />    
<input align="center" type="button" name="Submit" value="新增" onclick="AddRow(document.getElementById('tabProduct'),1)" />    
<input align="center" type="button" name="Submit2" value="删除" onclick="DeleteRow(document.getElementById('tabProduct'),1)" />    
## <input align="center" type="button" name="Submit22" value="重置" onclick="window.location.reload()" />    
<input align="center" type="button" name="Submit3" value="索引JSON" onclick="IndexJSON(document.getElementById('tabProduct'))" />    
</form> 
</div>
<br></br>
<div style="text-align:center">
<textarea id="textarea1" style="height: 500px;width: 700px;resize: none;">
##用来显示ES的建表语句
</textarea>
</div>
</br>
<div style="text-align:center">
<input align="center" type="button" name="Create" value="添加字段" onclick="uploadAddFields()" />
</div>
<br></br>
</div>
</script>
<script> 
debugger;
var count = 1;
var aliasNum=1;
var indexName;
## var indexJson={};
var inputIdxName="";
var arrayType=new Array();
var localName="${name}";
idxname.setAttribute("value", localName); 
##用来判断是删除 还是增加按钮 以便count值进行计算  
## function checkCount(boolOK, coun) {  
##   if (boolOK == true) {  
##       return count++;  
##     }  
##   else {  
##       count--;  
##     }  
## }

## function AddAliasInput(table, index){    
##   countAA = checkCount(true, count);    
##   var question = document.getElementById("alias");  
  
##   ##创建span  
##   var span = document.createElement("span");  
##   span.id = "spanAlias" + count;  
##   span.innerText = "Alias"+count+"："; 
## 	span.class="widget-label";
##   question.appendChild(span);  
  
##   ##创建input  
##   var input = document.createElement("input");  
##   input.type = "text";  
##   input.id = "Alias" + count;  
##   input.name = "Alias" + count;
## 	input.class="input-xlarge";
## 	input.validate="nonempty";
## 	input.placeholder="Alias.";
##   question.appendChild(input);  
  
##   ##创建一个空格  
##   var br = document.createElement("br");  
##   question.appendChild(br);    

##   aliasNum = aliasNum+1; 

## }

## ##每次删除最后一个input标签  
## function DecInput() {  

##   var count2 = 0  
##   var inputs = document.getElementsByTagName("input");  
##   for (var i = 0; i < inputs.length; i++) {  
##       var input = inputs[i];  
##       if (input.type == "text") {  
##           count2++;  
##       }  
##   }  

## 	count2=count2-7;
##   var question = document.getElementById("alias");  
  
##   var whichInput = document.getElementById("Alias" + count2);  
##   var whichSpan = document.getElementById("spanAlias" + count2);  
##   if(count2>1){
##   question.removeChild(whichInput);  
##   question.removeChild(whichSpan);  
  
##   var brs = document.getElementsByTagName("br");  
##   question.removeChild(brs[count2]);  
  
##   checkCount(false, count2);  
##   aliasNum=aliasNum-1;

##   }
## }

function EditTables(){    
for(var i=0;i<arguments.length;i++){    
   SetTableCanEdit(arguments[i]);    
}    
} 

function SetTableCanEdit(table){    
for(var i=1; i<table.rows.length;i++){    
   SetRowCanEdit(table.rows[i]);    
}    
}
function SetRowCanEdit(row){    
for(var j=0;j<row.cells.length; j++){    
    
   ##如果当前单元格指定了编辑类型，则表示允许编辑    
   var editType = row.cells[j].getAttribute("EditType");    
   if(!editType){    
    ##如果当前单元格没有指定，则查看当前列是否指定    
    editType = row.parentNode.rows[0].cells[j].getAttribute("EditType");    
   }    
   if(editType){    
    row.cells[j].onclick = function (){    
     EditCell(this);    
    }    
   }    
}    
    
}
function EditCell(element, editType){    
    
var editType = element.getAttribute("EditType");    
if(!editType){    
   ##如果当前单元格没有指定，则查看当前列是否指定    
   editType = element.parentNode.parentNode.rows[0].cells[element.cellIndex].getAttribute("EditType");    
}    
    
switch(editType){    
   case "TextBox":    
    CreateTextBox(element, element.innerHTML);    
    break;    
   case "DropDownList":    
    CreateDropDownList(element);    
    break;    
   default:    
    break;    
}    
}

function CreateTextBox(element, value){    
##检查编辑状态，如果已经是编辑状态，跳过    
var editState = element.getAttribute("EditState");    
if(editState != "true"){    
   ##创建文本框    
   var textBox = document.createElement("INPUT");    
   textBox.type = "text";    
   textBox.className="EditCell_TextBox";    
      
      
   ##设置文本框当前值    
   if(!value){    
    value = element.getAttribute("Value");    
   }      
   textBox.value = value;    
      
   ##设置文本框的失去焦点事件    
   textBox.onblur = function (){    
    CancelEditCell(this.parentNode, this.value);    
   }    
   ##向当前单元格添加文本框    
   ClearChild(element);    
   element.appendChild(textBox);    
   textBox.focus();    
   textBox.select();    
      
   ##改变状态变量    
   element.setAttribute("EditState", "true");    
   element.parentNode.parentNode.setAttribute("CurrentRow", element.parentNode.rowIndex);    
}    
    
} 

function CreateDropDownList(element, value){    
##检查编辑状态，如果已经是编辑状态，跳过    
var editState = element.getAttribute("EditState");    
if(editState != "true"){    
   ##创建下接框    
   var downList = document.createElement("Select");    
   downList.className="EditCell_DropDownList";    
      
   ##添加列表项    
   var items = element.getAttribute("DataItems");    
   if(!items){    
    items = element.parentNode.parentNode.rows[0].cells[element.cellIndex].getAttribute("DataItems");    
   }    
      
   if(items){    
    items = eval("[" + items + "]");    
    for(var i=0; i<items.length; i++){    
     var oOption = document.createElement("OPTION");    
     oOption.text = items[i].text;    
     oOption.value = items[i].value;    
     downList.options.add(oOption);    
    }    
   }    
      
   ##设置列表当前值    
   if(!value){    
    value = element.getAttribute("Value");    
   }    
   downList.value = value;    
    
   ##设置创建下接框的失去焦点事件    
   downList.onblur = function (){    
    CancelEditCell(this.parentNode, this.value, this.options[this.selectedIndex].text);    
   }    
      
   ##向当前单元格添加创建下接框    
   ClearChild(element);    
   element.appendChild(downList);    
   downList.focus();    
      
   ##记录状态的改变    
   element.setAttribute("EditState", "true");    
   element.parentNode.parentNode.setAttribute("LastEditRow", element.parentNode.rowIndex);    
}    
    
}

function CancelEditCell(element, value, text){    
element.setAttribute("Value", value);    
if(text){    
   element.innerHTML = text;    
}else{    
   element.innerHTML = value;    
}    
element.setAttribute("EditState", "false");    
    
##检查是否有公式计算    
CheckExpression(element.parentNode);    
}    
    
##清空指定对象的所有字节点    
function ClearChild(element){    
element.innerHTML = "";    
}    
    
##添加行    
function AddRow(table, index){    
var lastRow = table.rows[table.rows.length-1];
var newRow = lastRow.cloneNode(true);

table.tBodies[0].appendChild(newRow); 
newRow.cell[0].innerHTML='';
 
SetRowCanEdit(newRow);    
return newRow;    
    
}

function DeleteRow(table, index){    
for(var i=table.rows.length - 1; i>0;i--){    
   var chkOrder = table.rows[i].cells[0].firstChild;    
   if(chkOrder){    
    if(chkOrder.type = "CHECKBOX"){    
     if(chkOrder.checked){    
      ##执行删除    
      table.deleteRow(i);    
     }    
    }    
   }    
}    
}

##提取表格的值,JSON格式    
function IndexJSON(table){   
debugger;

var inputIdxName="${name}";
alert("~~~~~~~~~~~~~~~~~~~~~~~~~~indname:"+inputIdxName);

var stringType="${stringType}";
alert("~~~~~~~~~~~~~~~~~~~~~~~~~~stringType:"+stringType);
arrayType=stringType.split(",");

debugger;


var tableData = new Array();  
var textarea0 = document.getElementById("textarea1");  
  
for(var i=1; i<table.rows.length;i++){    
   tableData.push(GetRowData(tabProduct.rows[i]));    
}  

var len=tableData.length;
var contentType = new Array();
for(var j=0;j<len;j++){

  if(JSON.stringify(tableData[j].DataType)==JSON.stringify("two")){
    var contenttypeDef={};
    
    contenttypeDef={
    "type":"text",
    "fields": {
						"keyword": {
							"type": "keyword"
						}
					}
          };

    contentType[j]=contenttypeDef;
  }else if(JSON.stringify(tableData[j].DataType)==JSON.stringify("date")){
    contentType[j]={
    "type":"date",
    "format": tableData[j].Format,
    "ignore_malformed": true
          };
  }else{
    contentType[j]={"type":tableData[j].DataType}
  }
  alert("contentType:"+JSON.stringify(contentType[j]));
}

var properties={};
for(var j=0;j<len;j++){

  var fieldName0=tableData[j].FieldName;
  properties[fieldName0]=contentType[j];
}

indexName={"properties":properties}

textarea0.innerHTML=JSON.stringify(indexName);

}


function uploadAddFields(){
  var indexJson=document.getElementById("textarea1").value;
  var localIdxName=document.getElementById("idxname").value;
  alert(indexJson);
  debugger;
## var url="/ES/views/getJsonAddFields/"

    $.post("/ES/views/getJsonAddFields/", {
        indexName:ko.mapping.toJSON(localIdxName),
        addFieldJson:ko.mapping.toJSON(indexJson),
        arrayType:ko.mapping.toJSON(arrayType)
      }, function(msg) {
        alert(msg);

      });

}


function showResult(msg){
 alert(msg);

 }

##提取指定行的数据，JSON格式    
function GetRowData(row){    
var rowData = {};    
for(var j=0;j<row.cells.length; j++){    
   name = row.parentNode.rows[0].cells[j].getAttribute("Name"); 
  
   if(name){    
    var value = row.cells[j].getAttribute("Value"); 
  
    if(!value){    
     value = row.cells[j].innerHTML;    
    }    
       
    rowData[name] = value;    
   }    
}    
## alert("ProductName:" + rowData.ProductName);    
##或者这样：alert("ProductName:" + rowData["ProductName"]);    
return rowData;    
    
}

##检查当前数据行中需要运行的字段    
function CheckExpression(row){    
for(var j=0;j<row.cells.length; j++){    
   expn = row.parentNode.rows[0].cells[j].getAttribute("Expression");    
   ##如指定了公式则要求计算    
   if(expn){    
    var result = Expression(row,expn);    
    var format = row.parentNode.rows[0].cells[j].getAttribute("Format");    
    if(format){    
     ##如指定了格式，进行字值格式化    
     row.cells[j].innerHTML = formatNumber(Expression(row,expn), format);    
    }else{    
     row.cells[j].innerHTML = Expression(row,expn);    
    }    
   }    
      
}    
}


##计算需要运算的字段    
function Expression(row, expn){    
var rowData = GetRowData(row);    
##循环代值计算    
for(var j=0;j<row.cells.length; j++){    
   name = row.parentNode.rows[0].cells[j].getAttribute("Name");    
   if(name){    
    var reg = new RegExp(name, "i");    
    expn = expn.replace(reg, rowData[name].replace(/\,/g, ""));    
   }    
}    
return eval(expn);    
} 

function formatNumber(num,pattern){      
var strarr = num?num.toString().split('.'):['0'];      
var fmtarr = pattern?pattern.split('.'):[''];      
var retstr='';      
      
## 整数部分      
var str = strarr[0];      
var fmt = fmtarr[0];      
var i = str.length-1;        
var comma = false;      
for(var f=fmt.length-1;f>=0;f--){      

    switch(fmt.substr(f,1)){      
      case '#':      
        if(i>=0 ) retstr = str.substr(i--,1) + retstr;      
        break;      
      case '0':      
        if(i>=0) retstr = str.substr(i--,1) + retstr;      
        else retstr = '0' + retstr;      
        break;      
      case ',':      
        comma = true;      
        retstr=','+retstr;      
        break;      
    }      
}      
if(i>=0){      
    if(comma){      
      var l = str.length;      
      for(;i>=0;i--){      
        retstr = str.substr(i,1) + retstr;      
        if(i>0 && ((l-i)%3)==0) retstr = ',' + retstr;       
      }      
    }      
    else retstr = str.substr(0,i+1) + retstr;      
}      
      
retstr = retstr+'.';      
## 处理小数部分      
str=strarr.length>1?strarr[1]:'';      
fmt=fmtarr.length>1?fmtarr[1]:'';      
i=0;      
for(var f=0;f<fmt.length;f++){      
    switch(fmt.substr(f,1)){      
      case '#':      
        if(i<str.length) retstr+=str.substr(i++,1);      
        break;      
      case '0':      
        if(i<str.length) retstr+= str.substr(i++,1);      
        else retstr+='0';      
        break;      
    }      
}      
return retstr.replace(/^,+/,'').replace(/\.$/,'');      
}

</script>
## </%def>