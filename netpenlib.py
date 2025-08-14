import sys
import os
import requests
import platform
from concurrent.futures import ThreadPoolExecutor
import subprocess
import time

# To people that will use this lib
# all functions: netpenlib.ndscan() scans all devices in local network
# netpenlib.ping(IP) pings ip adress and returns True or False based if host responded
# netpenlib.swarm(IP,how much times, "one"/"infect") pings ip fastly. you can precise how much times it will ping the ip. ONE - only your device swarms the ip. INFECT - tries to remotely force pinging IP on other devices
# thx

def ndscan(base_ip="192.168.1", start=1, end=255, timeout_ms=100, max_threads=50):
    def ping(ip):
        system = platform.system().lower()
        param = f"-n 1 -w {timeout_ms}" if system == "windows" else f"-c 1 -W {timeout_ms//1000}"
        command = f"ping {param} {ip} > {'nul' if system == 'windows' else '/dev/null'}"
        return ip if os.system(command) == 0 else None

    ips = [f"{base_ip}.{i}" for i in range(start, end + 1)]
    active_devices = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        results = executor.map(ping, ips)
        active_devices = [ip for ip in results if ip is not None]

    return active_devices

def ping(ip):
    system = platform.system().lower()
    command = (
        f"ping -n 1 -w 1000 {ip} > nul"  
        if system == "windows" 
        else f"ping -c 1 -W 1 {ip} > /dev/null"  
    )
    return os.system(command) == 0

def swarm(ip, times, option):
    try:
        ifworks=ping(ip)
    except:
        return print("""It seems that... 	( • ⩊ •' )
        netpenlib function swarm doesn't work. Please contact the author of the lib.""")
    if ifworks==True:
        if option=="one":
            i = 0
            while i < times:
                i = i + 1
                print(i)
                return ping(ip)
        elif option=="infect":
            print("nothing")
            i = 0
            while i < times:
                infect("ping ",ip)
                i += 1
                time.sleep(1250)
    elif ifworks==False:
        return print("It seems that host doesn't respond.")
    

def infect(command, base_ip="192.168.1", start=1, end=255, max_threads=250, timeout_ms=50):
    def ping(ip):
        system = platform.system().lower()
        param = f"-n 1 -w {timeout_ms}" if system == "windows" else f"-c 1 -W {timeout_ms//1000}"
        cmd = f"ping {param} {ip} > {'nul' if system == 'windows' else '/dev/null'}"
        return ip if os.system(cmd) == 0 else None
    def execute_command(ip):
        try:
            system = platform.system().lower()
            
            if system == 'windows':
                process = subprocess.Popen(
                    ['powershell', '-Command', command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                process = subprocess.Popen(
                    ['ssh', ip, command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
            stdout, stderr = process.communicate()
            output = stdout.decode('utf-8', errors='replace')
            error = stderr.decode('utf-8', errors='replace')
            
            print(f"\n[{ip}] final:")
            print(output)
            if error:
                print(f"[{ip}] error:", error)
                
            return process.returncode == 0
            
        except Exception as e:
            print(f"[{ip}] warning: {str(e)}")
            return False
    print(f"scanning {base_ip}.{start}-{end}...")
    ips = [f"{base_ip}.{i}" for i in range(start, end + 1)]
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        active_ips = [ip for ip in executor.map(ping, ips) if ip is not None]
        
        if not active_ips:
            print("didnt found any devices compatible")
            return
            
        print("\nactive devices:")
        for ip in active_ips:
            print(ip)
        
        print(f"\nsending command: '{command}'")
        results = list(executor.map(execute_command, active_ips))
    print(f"success executions: {sum(results)}/{len(results)}")