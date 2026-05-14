import os
import time

def turn_off_computer():
    print("[!] Preparando para desligar o computador...")
    if os.name == 'nt':
        os.system('shutdown /s /t 30')
        print("    Desligamento em 30s. Para cancelar: 'shutdown /a'")
    else:
        print("    Desligamento em 1m. Para cancelar: 'shutdown -c'")
        os.system('sudo shutdown -h +1' if 'darwin' in os.sys.platform else 'shutdown -h +1')
    time.sleep(5)