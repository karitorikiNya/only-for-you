#!/bin/bash
MAC="41:42:19:98:2D:B7"
sleep 5
bluetoothctl power on
bluetoothctl agent on
bluetoothctl default-agent
WAS_CONNECTED=false

while true; do
    if bluetoothctl info $MAC | grep -q "Connected: yes"; then
        if [ "$WAS_CONNECTED" = false ]; then
            WAS_CONNECTED=true
        fi
    else
        if [ "$WAS_CONNECTED" = true ]; then
            WAS_CONNECTED=false
        fi
        bluetoothctl connect $MAC
    fi
    sleep 5
done
