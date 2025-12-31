#!/bin/bash

# Запускаем сервер
jdas serve &
SERVER_PID=$!
sleep 3

# Проверяем API
curl -s http://localhost:8000/ | python -m json.tool
# Должен вернуть: {"service": "DAS Cleaning API", "endpoints": ...}

# Проверяем документацию
curl -s http://localhost:8000/docs -I | head -1
# Должен быть: HTTP/1.1 200 OK

kill $SERVER_PID
