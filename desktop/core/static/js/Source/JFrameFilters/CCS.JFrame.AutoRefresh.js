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
---
description: An auto refresh filter for Jframe keyed on the meta-refresh tag.
provides: [CCS.JFrame.AutoRefresh]
requires: [/CCS.JFrame, More/Date, Table/Table]
script: CCS.JFrame.AutoRefresh.js

...
*/

(function(){
var metaRE = /<meta(.*)?\/>/;  //regular expression to remove all but attributes
var removeQuotes = /"/g; //regular expression to remove quotes


CCS.JFrame.addGlobalFilters({

	autorefresh: function(container, content){
		$clear(refreshTable.get(this));
		//get the first input.autorefresh and use its value as the duration before 
		//it auto refreshes the input. if span.sec_to_autorefresh is present, fill its
		//contents with the number of seconds until a refresh.
                if (content && content.meta) {
			var sec, url;
                        			content.meta.each(function(meta) {
			        var match = metaRE.exec(meta);
                                if(match[1]) {
                                         var data = match[1]; //set data to string of html attributes, space separated
                                } else {
                                         return;
                                }  
                                data = data.trim().split(' ');
                                var attributeMap = new Object;
                                data.each(function(item) {
                                        var attribute = item.split('=');
                                        attributeMap[attribute[0].replace(removeQuotes, '')] = attribute[1].replace(removeQuotes, ''); // remove quotes within string
                                }); 
                                var parts = attributeMap['content'].split(';');
				if (attributeMap['http-equiv'] == "refresh") {
					sec = parts[0];
					if (parts[1]) url = unescape(parts[1].replace('url=', ''));
				}
			}, this);
			if (!sec) return;
			var end = new Date().increment('second', sec);
			var until, diff, span;
			var update = function() {
				span = $(this).getElement('span.sec_to_autorefresh');
				diff = ((end - new Date()) / Date.units['second']());
				until = diff.toInt();
				if (span) span.set('html', until);
			}.bind(this);
			update();

			var timer = (function(){
				if (diff < 1) {
					if (span) span.set('html', 0);
					if (url && url != unescape(this.currentPath)) this.load({ requestPath: url, autorefreshed: true });
					else this.refresh({ autorefreshed: true });
					$clear(timer);
				} else {
					update();
				}
			}).periodical(250, this);
			
			refreshTable.set(this, timer);
			
			var clearer = function(){
				$clear(timer);
				this.removeEvent('request', clearer);
			};
			this.addEvent('request', clearer);
			this.markForCleanup(function(){
				$clear(timer);
			});
		}
	}

});

var refreshTable = new Table();

})();
