#!/bin/bash
set -e
cp /home/workspace/unified-source/publish-python.sh /srv/unified/publish-python.sh
chmod +x /srv/unified/publish-python.sh
runuser -u workspace -- env VERIFY_IMPORTS=sharedkit bash /srv/unified/publish-python.sh --no-build-isolation /srv/unified/state/sharedkit-src
bash /srv/unified/verify.sh