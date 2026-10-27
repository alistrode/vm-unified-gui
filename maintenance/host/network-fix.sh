set -e
pkill -TERM -x apt-get || true
printf 'Acquire::ForceIPv4 "true";\nAcquire::http::Timeout "30";\nAcquire::Retries "2";\n' > /etc/apt/apt.conf.d/99-unified-network
nohup bash /home/workspace/unified-source/bootstrap.sh > /home/workspace/bootstrap.log 2>&1 < /dev/null &
