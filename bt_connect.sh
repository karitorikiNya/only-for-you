#!/bin/bash
MAC="41:42:19:98:2D:B7" # MAC адрес наушников
SERVICE="VictoriasSecret.service" # Сервис, который грузит видео у нас

WAS_CONNECTED=false

while true; do
    # Проверяем статус подключения
    if bluetoothctl info $MAC | grep -q "Connected: yes"; then
        # Если только что подключились (были False, стали True)
        if [ "$WAS_CONNECTED" = false ]; then
            # Наушники подключены - рестартим сервис, чтобы omxplayer смог перейти на них
            sudo systemctl restart $SERVICE
            WAS_CONNECTED=true
        fi
    else
        # Если связи нет
        if [ "$WAS_CONNECTED" = true ]; then
            # Наушники отключены - рестартим сервис, чтобы omxplayer смог перейти на динамики
            sudo systemctl restart $SERVICE
            WAS_CONNECTED=false
        fi
        # Пытаемся подключиться, если не подключены
        bluetoothctl connect $MAC
    fi

    sleep 10
done
