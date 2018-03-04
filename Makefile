
deb: copy
	dpkg-deb -b debian

i18n/ru/LC_MESSAGES/callcontrol.mo: i18n/ru/LC_MESSAGES/callcontrol.po
	msgfmt $< -o $@

copy: i18n/ru/LC_MESSAGES/callcontrol.mo *.py
	cp callcontrol.py debian/usr/bin/
	chmod +x debian/usr/bin/callcontrol.py
	cp browserwindow.py callcontrol.py channels.py config.py dial.py leadswindow.py order.py scheduler.py statuswindow.py debian/usr/lib/python3/dist-packages/
	cp i18n/ru/LC_MESSAGES/callcontrol.mo debian/usr/share/locale/ru/LC_MESSAGES
