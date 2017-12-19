
<%!from desktop.views import commonheader, commonfooter %>
<%!from exec_log.conf import URL %>

<%namespace name="shared" file="shared_components.mako" />

%if not is_embeddable:
${commonheader("Exec Log", "exec_log", user, request, "28px") | n,unicode}
%endif

## Use double hashes for a mako template comment
## Main body

<style type="text/css">
  #appframe {
    width: 100%;
    border: 0;
  }
</style>

<iframe id="appframe" src="${ URL.get() if URL.get() else 'http://mls.teld.cn:4330/grafana/dashboard/ooziewflog?orgId=1' }"></iframe>

<script type="text/javascript">
  $(document).ready(function () {
    var _resizeTimeout = -1;
    $(window).on("resize", function () {
      window.clearTimeout(_resizeTimeout);
      _resizeTimeout = window.setTimeout(resizeAppframe, 300);
    });

    function resizeAppframe() {
      $("#appframe").height($(window).height() - (IS_HUE_4 ? 48 : 34)); // magic: navigator height + safety pixels
    }

    resizeAppframe();
  });
</script>

%if not is_embeddable:
${commonfooter(request, messages) | n,unicode}
%endif
