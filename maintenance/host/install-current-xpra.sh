set -euxo pipefail
while pgrep -x apt-get >/dev/null; do sleep 10; done
export DEBIAN_FRONTEND=noninteractive
curl -fL --max-time 40 https://xpra.org/xpra.asc -o /usr/share/keyrings/xpra.asc
curl -fL --max-time 40 https://raw.githubusercontent.com/Xpra-org/xpra/master/packaging/repos/noble/xpra.sources -o /etc/apt/sources.list.d/xpra.sources
apt-get update
apt-get install --no-install-recommends -y xpra xpra-html5
xpra --version
