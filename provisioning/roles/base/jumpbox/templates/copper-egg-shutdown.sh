#!/bin/bash -x

apisrv='api.copperegg.com'
apikey='{{ copper_egg_token }}'
# Remove the system:
/usr/local/revealcloud/revealcloud -k ${apikey} -R -m -a ${apisrv}
# Optional: Remove a related website probe (comment these out if not needed)
probeid=`cat probe.id`
/usr/bin/curl -s -k -u ${apikey}:U -XDELETE https://${apisrv}/v2/revealuptime/probes/${probeid}.json
/sbin/poweroff -p
