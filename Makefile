
deb: copy
	dpkg-deb -b debian
	mv debian.deb callcontrol.deb

repo:
#	cd  /var/www/repos/apt/debian &&  reprepro includedeb stretch /home/fastery/callcontrol/callcontrol.deb
	cd  /var/www/repos/apt/ubuntu &&  reprepro includedeb xenial /home/fastery/callcontrol/callcontrol.deb

i18n/ru/LC_MESSAGES/callcontrol.mo: i18n/ru/LC_MESSAGES/callcontrol.po
	msgfmt $< -o $@

copy: i18n/ru/LC_MESSAGES/callcontrol.mo *.py
	cp callcontrol.py debian/usr/bin/
	chmod +x debian/usr/bin/callcontrol.py
	cp browserwindow.py callcontrol.py channels.py ccconf.py config.py dial.py leadswindow.py order.py scheduler.py statuswindow.py sipclients.py debian/usr/lib/python3/dist-packages/
	cp i18n/ru/LC_MESSAGES/callcontrol.mo debian/usr/share/locale/ru/LC_MESSAGES
