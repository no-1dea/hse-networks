#!/usr/bin/env python
import argparse
import platform
import validators
import subprocess
import time


ICMP_HEADER_SIZE = 8
IP_HEADER_SIZE = 20


def parse_args():
    parser = argparse.ArgumentParser(description='Scripy for finding min MTU between localhost and host')
    parser.add_argument('host', type=str, help='Hostname or IPv4 address')
    return parser.parse_args()


def validate_args(args):
    assert validators.domain(args.host) or validators.ipv4(args.host), 'Invalid hostname or IPv4 address'
    assert find_mtu(args.host).returncode == 0, 'Host is not reachable'


def find_mtu(host, mtu=56):
    return subprocess.run(['ping', host, '-c', '1', '-t', '100', '-D', '-s', str(mtu)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# https://www.comparitech.com/net-admin/determine-mtu-size-using-ping/
def find_min_mtu(host):
    l = 0
    r = 2001
    while r - l > 1:
        m = l + (r - l) // 2
        ping = find_mtu(host, m)
        if platform.system() == 'Darwin' and ping.returncode == 1:
            raise RuntimeError('Timeout reached: {}'.format(ping.error))
        
        if ping.returncode == 0:
            l = m
        else:
            r = m
        
        time.sleep(0.1)
    return l + ICMP_HEADER_SIZE + IP_HEADER_SIZE


def main():
    args = parse_args()
    validate_args(args)
    min_mtu = find_min_mtu(args.host)
    print('Min MTU:', min_mtu)


if __name__ == '__main__':
    main()