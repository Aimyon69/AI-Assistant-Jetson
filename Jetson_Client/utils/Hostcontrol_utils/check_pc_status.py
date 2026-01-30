import os
import time


def is_pc_online(IP):
    response=os.system(f'ping -c 1 -W 1 {IP} > /dev/null 2>&1')
    return response==0


