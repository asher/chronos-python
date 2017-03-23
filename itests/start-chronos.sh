sudo /etc/init.d/zookeeper start
sleep 5
CMD rsyslogd ; sleep 1; (/usr/bin/chronos &) ; tail -f /var/log/syslog
