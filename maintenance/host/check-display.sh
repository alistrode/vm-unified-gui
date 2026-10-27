xpra --help | grep -i -A2 auth
tail -25 /run/user/1000/xpra/100/server.log
find /run/user/1000/xpra -name '*auth*' -o -name '*authority*'
ps -ef | grep -E '[X]org|[X]vfb'
