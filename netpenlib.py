import os
import platform
from concurrent.futures import ThreadPoolExecutor
import subprocess
import time
import nmap

# To people that will use this lib
# all functions: netpenlib.ndscan() scans all devices in local network
# netpenlib.ping(IP) pings ip adress and returns True or False based if host responded
# netpenlib.swarm(IP,how much times, "one"/"infect") pings ip fastly. you can precise how much times it will ping the ip. ONE - only your device swarms the ip. INFECT - tries to remotely force pinging IP on other devices
# netpenlib.osscan() scans and returns device OS, version and details   \
# netpenlib.lnscan() same as ndscan but scans and gets details about ip / doesnt work good. stfu, it just doesn't work
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


def osscan(ip):
    try:
        nm = nmap.PortScanner()
        nm.scan(hosts=ip, arguments='-O -sV')
        
        if ip not in nm.all_hosts():
            return None
        
        host = nm[ip]
        os_info = host.get('osmatch', [])
        if not os_info:
            return None
        
        best_os_guess = os_info[0]
        os_name = best_os_guess['name']
        
        version = "none"
        service_info = host.get('tcp', {})
        for port in service_info:
            service = service_info[port]
            if 'product' in service and 'version' in service:
                version = f"{service['product']} {service['version']}"
                break
        
        return {
            "ip": ip,
            "os": os_name,
            "version": version,
            "details": host.get('osfingerprint', 'no data')
        }
    
    except Exception as e:
        print(f"error while scanning {ip}: {e}")
        return None

def lnscan(ip_list):
    results = []
    for ip in ip_list:
        print(f"\nscanning {ip}...")
        result = osscan(ip)
        
        if result:
            print(f"found host: {ip}")
            print(f"   os: {result['os']}")
            print(f"   version: {result['version']}")
            results.append(result)
        else:
            print(f"Host {ip} does not respond or is offline.")
        
        time.sleep(0.05)
    
    return results