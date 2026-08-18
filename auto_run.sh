#!/bin/bash
# Esperar a que la IA responda y termine su turno
sleep 2

# Detener cualquier bot de remoat previo y Antigravity
killall Antigravity
killall node

# Esperar a que se cierren por completo
sleep 2

# Iniciar el bot de remoat en segundo plano de manera persistente
nohup remoat start > /tmp/remoat_bot.log 2>&1 &

# Esperar un segundo
sleep 1

# Iniciar Antigravity con el puerto de depuración habilitado
/Applications/Antigravity.app/Contents/MacOS/Antigravity --remote-debugging-port=9222 &
