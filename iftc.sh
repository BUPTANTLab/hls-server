#! /bin/bash
while true;do
    echo -n `date +%H:%M:%S` " " >> shellresult;echo $[`cat /sys/class/net/eth0/statistics/tx_bytes`-`awk '{sum+=$2}END{print sum}'  shellresult `]>>shellresult
    sleep 1
done
