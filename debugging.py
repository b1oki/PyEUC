#!python3
import sys
sys.path.append('/snap/pycharm-professional/current/debug-eggs/pydevd-pycharm.egg')
import pydevd


def breakpoint(port=12345, suspend=False, ip='127.0.0.1'):
    # sshpass -p password ssh -p 22 -R 12345:127.0.0.1:12345 root@host
    # from debugging import breakpoint; breakpoint()
    pydevd.settrace(ip, port=port, stdoutToServer=True, stderrToServer=True, suspend=suspend)
    return True
