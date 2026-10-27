set -eu
systemctl stop unified-desktop-a unified-desktop-b unified-desktop-c
for cid in a b c; do
 config=/srv/unified/state/desktops/$cid/home/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml
 cp -a "$config" /srv/unified/backups/native-panel-$cid-before-$(date -u +%Y%m%d_%H%M%S).xml
 install -o workspace -g workspace -m 644 /etc/xdg/xfce4/panel/default.xml "$config"
done
systemctl start unified-desktop-a unified-desktop-b unified-desktop-c
runuser -u workspace -- env DISPLAY=:100 XAUTHORITY=/srv/unified/state/auth/host python3 /srv/unified/modes/controller.py mode 1
systemctl is-active unified-desktop-a unified-desktop-b unified-desktop-c
