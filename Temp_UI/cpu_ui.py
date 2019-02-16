import cpuinfo
import psutil


print(cpuinfo.get_cpu_info()['hz_actual'])
print(psutil.cpu_freq())
