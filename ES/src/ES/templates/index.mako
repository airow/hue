<%! 
    from desktop.views import commonheader, commonfooter 
    from desktop import conf
    from django.utils.translation import ugettext as _
%>

<%namespace name="assist" file="assist.mako" />
<%namespace name="shared" file="shared_components.mako" />
<%namespace name="editorComponents" file="editor_components.mako" />


%if not is_embeddable:
${commonheader("Es", "ES", user, request) | n,unicode}
%endif

<meta http-equiv="pragma" content="no-cache"> 
<meta http-equiv="Cache-Control" content="no-cache, must-revalidate"> 
<meta http-equiv="expires" content="Wed, 26 Feb 1997 08:21:57 GMT">

<span id="editorComponents" class="editorComponents notebook">
${ editorComponents.includes(is_embeddable=is_embeddable, suffix='editor') }

${ editorComponents.topBar(suffix='editor') }
${ editorComponents.commonHTML(is_embeddable=is_embeddable, suffix='editor') }
##${shared.menubar(section='mytab')}

## Use double hashes for a mako template comment
## Main body

## <div class="container-fluid">
##   <div class="card">
##     <h2 class="card-heading simple">Es app is successfully setup!</h2>
##     <div class="card-body">
##       <p>It's now ${date}.</p>
##     </div>
##   </div>
## </div>
%if not is_embeddable:
${commonfooter(request, messages) | n,unicode}
${ assist.assistPanel() }
${ assist.assistJSModels() }
%endif
