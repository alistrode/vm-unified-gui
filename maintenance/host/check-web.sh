head -55 /srv/unified/web/display/index.html
ls -l /srv/unified/web/display/css /srv/unified/web/display/js | head -20
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/display/css/client.css
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8081/css/client.css
tail -15 /var/log/nginx/error.log
journalctl -u unified-display --no-pager -n 10
