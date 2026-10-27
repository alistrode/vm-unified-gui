#!/bin/bash
# Run as workspace: VERIFY_IMPORTS=requests ./publish-python.sh requests==VERSION
# Python runtime / Ubuntu ABI must match the common application image.
set -euo pipefail
exec 9>/srv/unified/state/dependency-publisher.lock
flock -x 9
cd /srv/unified
target=$(mktemp -d shared/user/python-next.XXXXXX)
trap 'test -d "$target" && rm -r -- "$target"' EXIT
state/publisher/bin/pip install --target "$target" "$@"
: "${VERIFY_IMPORTS:?Set VERIFY_IMPORTS to comma-separated module names to test in the common image}"
docker run --rm --user 1000:1000 --network none --cap-drop ALL --security-opt no-new-privileges:true \
 -v "$PWD/$target:/opt/shared-user/python:ro" -e PYTHONPATH=/opt/shared-user/python -e VERIFY_IMPORTS \
 unified-apps:24.04 python3 -c 'import importlib,os; [importlib.import_module(m.strip()) for m in os.environ["VERIFY_IMPORTS"].split(",")]; print("Container import verification passed")'
old="shared/user/python-previous-$(date +%s)"
mv shared/user/python "$old"
mv "$target" shared/user/python
echo "Published. Previous environment retained at $old; restart apps to load new imports."
