#!/bin/sh

#python3 gdocsfetch.py

python3 database.py inbound > /etc/asterisk/extensions-inbound.conf
python3 database.py internal > /etc/asterisk/extensions-internal.conf
python3 database.py callout > /etc/asterisk/extensions-callout.conf

python3 database.py sipout > /etc/asterisk/sip-sipout.conf
python3 database.py sipout-register > /etc/asterisk/sip-sipout-register.conf
python3 database.py operators > /etc/asterisk/sip-operators.conf

asterisk -x reload
