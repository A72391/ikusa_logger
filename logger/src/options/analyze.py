import os
import re
from scapy.all import sniff, rdpcap, wrpcap
from time import localtime, strftime
from .. import config


def dec(bytes):
    message = str(bytes, "latin-1")
    message = message.replace("\x00", "")
    return message


def extract_string(hex, offset, length):
    if hex[offset:offset+2] == "00":
        return -1
    try:
        length = min(len(hex)-offset, length)
        if length < 0:
            raise ValueError('Package too short')

        return dec(bytes.fromhex(hex[offset:offset+length]))
    except ValueError as e:
        #print(e, flush=True)
        return -1


last_payload = ""
current_position = 0

identifier_regex = r"[56][0-9a-f]0100[0-9a-f]{4}"
name_regex = r"^[A-Z][a-zA-Z0-9]{2,64}$"


def package_handler(package, output, record=False):

    global last_payload

    if "IP" not in package:
        return

    package_src = package["IP"].src

    # checks if the package derives from bdo
    is_bdo_ip = len(([ip for ip in ["20.76.13", "20.76.14"] if ip in package_src])) > 0

    # chckes if the packages comes from a tcp stream
    uses_tcp = "TCP" in package and hasattr(package["TCP"].payload, "load")
    if is_bdo_ip and uses_tcp:

        # loads the payload as raw hex
        payload = bytes(package["TCP"].payload).hex()
        
        # iterate through the payload and try to find the identifier + player names + guild name + kill
        payload = last_payload + payload
        position = 0
        while(len(payload) >= 600):
            payload = payload[position:]
            match = re.match(identifier_regex, payload[0:20])
            if(match):
                possible_log = payload[0:600]
                i = 0
                names = []
                while i < 600:
                    name = extract_string(possible_log, i, 64)
                    if(name == -1):
                        i += 1
                        continue
                    is_valid = re.match(name_regex, name)
                    if is_valid:
                        names.append(name + " " + str(i))
                        i += 64
                    else:
                        i += 1
                if len(names) == 5:
                    print(match.group(0)+","+','.join(names)+","+possible_log, flush=True)
                position = 600
            else:
                position = 1
        
        last_payload = payload  

def open_pcap(file, output):
    if file != None and not os.path.isfile(file):
        print("Invalid file", flush=True)
        return
    print("Reading " + file, flush=True)
    if os.name == "nt":
        print("Loading file into ram. This may take a while.", flush=True)
        cap = rdpcap(file)
        index = 0
        for package in cap:
            package_handler(package, output)
            if index % 10000 == 0:
                print(f"{index}/{len(cap)} packages analyzed.", flush=True)
            index += 1
    else:
        sniff(offline=file, filter="tcp", prn=package_handler, store=0)

    print(
        f"Logs saved under: {output}\nYou can close this window now.", flush=True)
