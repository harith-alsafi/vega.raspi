import psutil
from gpiozero import InputDevice
from tabulate import tabulate
import time

def get_cpu_temp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = f.read().strip()
            return f'{float(temp) / 1000:.2f} °C'
    except FileNotFoundError:
        return 'N/A'

def get_cpu_usage():
    return f'{psutil.cpu_percent(interval=1):.2f} %'

def get_ram_usage():
    ram = psutil.virtual_memory()
    return f'{ram.percent:.2f} %'

def get_disk_usage():
    disk = psutil.disk_usage('/')
    return f'{disk.percent:.2f} %'

def get_system_uptime():
    uptime = psutil.boot_time()
    return f'Uptime: {round(time.time() - uptime)} seconds'

# Collect data
cpu_temp = get_cpu_temp()
cpu_usage = get_cpu_usage()
ram_usage = get_ram_usage()
disk_usage = get_disk_usage()
uptime = get_system_uptime()

# Create Markdown table
table_data = [
    ['CPU Temperature', cpu_temp],
    ['CPU Usage', cpu_usage],
    ['RAM Usage', ram_usage],
    ['Disk Usage', disk_usage],
    ['Uptime', uptime]
]

# Display table in Markdown format
markdown_table = tabulate(table_data, headers=['Metric', 'Value'], tablefmt='pipe')
print(markdown_table)
