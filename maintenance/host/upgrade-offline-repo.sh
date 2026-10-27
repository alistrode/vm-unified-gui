set -euxo pipefail
cp /home/workspace/unified-source/xpra.sources /etc/apt/sources.list.d/xpra.sources
export DEBIAN_FRONTEND=noninteractive
nohup bash -c 'apt-get update && apt-get install --no-install-recommends -y xpra xpra-html5' > /home/workspace/xpra-upgrade.log 2>&1 < /dev/null &
