#!/bin/bash 
tc qdisc del dev eth0 root 

tc qdisc add dev eth0 root handle 1:0 cbq bandwidth 100Mbit avpkt 1000 cell 8

tc class add dev eth0 parent 1:0 classid 1:1 cbq bandwidth 100Mbit rate 1Mbit weight 100kbit prio 8 allot 1514 cell 8 maxburst 20 avpkt 1000 bounded

tc class add dev eth0 parent 1:1 classid 1:3 cbq bandwidth 1Mbit rate 1Mbit weight 100kbit prio 5 allot 1514 cell 8 maxburst 20 avpkt 1000 bounded
tc class add dev eth0 parent 1:1 classid 1:4 cbq bandwidth 1Mbit rate 1Mbit weight 100kbit prio 5 allot 1514 cell 8 maxburst 20 avpkt 1000 bounded
tc class add dev eth0 parent 1:1 classid 1:5 cbq bandwidth 1Mbit rate 1Mbit weight 100kbit prio 5 allot 1514 cell 8 maxburst 20 avpkt 1000 bounded
tc class add dev eth0 parent 1:1 classid 1:6 cbq bandwidth 1Mbit rate 1Mbit weight 100kbit prio 5 allot 1514 cell 8 maxburst 20 avpkt 1000 bounded
tc class add dev eth0 parent 1:1 classid 1:7 cbq bandwidth 1Mbit rate 1Mbit weight 100kbit prio 5 allot 1514 cell 8 maxburst 20 avpkt 1000 bounded

tc qdisc add dev eth0 parent 1:3 handle 30: sfq
tc qdisc add dev eth0 parent 1:4 handle 40: sfq
tc qdisc add dev eth0 parent 1:5 handle 50: sfq
tc qdisc add dev eth0 parent 1:6 handle 60: sfq
tc qdisc add dev eth0 parent 1:7 handle 70: sfq

tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 match ip sport 8000 0xffff match ip dst 10.105.37.121/32 flowid 1:3
tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 match ip sport 8000 0xffff match ip dst 10.105.38.60/32 flowid 1:3
tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 match ip sport 8000 0xffff match ip dst 10.105.38.236/32 flowid 1:3
tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 match ip sport 8000 0xffff match ip dst 10.105.36.123/32 flowid 1:3
tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 match ip sport 8000 0xffff match ip dst 10.105.39.100/32 flowid 1:3
tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 match ip sport 8000 0xffff match ip dst 10.105.36.82/32 flowid 1:3
tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 match ip sport 8000 0xffff match ip dst 10.210.62.202/32 flowid 1:3
tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 match ip sport 8000 0xffff match ip dst 10.210.62.206/32 flowid 1:3
