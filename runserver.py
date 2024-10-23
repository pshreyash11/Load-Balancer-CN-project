import subprocess

# Ports to run the servers on
ports = range(8080, 8085)  # 8080 to 8084

# Loop through the port numbers and start a server for each
for port in ports:
    subprocess.run(['start', 'cmd', '/K', f'python server.py {port}'], shell=True)
