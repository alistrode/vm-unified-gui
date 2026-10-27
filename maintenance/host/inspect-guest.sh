xpra --version
dpkg-query -W xpra-html5
rg_cmd=grep
grep -nE '(var|let|const) client|client = init_client' /usr/share/xpra/www/index.html | head
grep -nE 'send_configure_window|geometry_cb' /usr/share/xpra/www/js/{Client,Window}.js | head
tail -8 /home/workspace/xpra-upgrade.log
tail -8 /home/workspace/build.log
