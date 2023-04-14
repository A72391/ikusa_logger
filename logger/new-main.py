from src import config
from src.options import status_check, open, sniff, record

import time
from time import localtime, strftime
from configparser import ConfigParser
from argparse import ArgumentParser, BooleanOptionalAction
from datetime import date
import os.path
import os


parser = ArgumentParser()
parser.add_argument("-f", "--file", dest="filename",
                    help="Instead of sniffing for bdo packages, it will use the given *.pcap file", metavar="FILE")
parser.add_argument("-o", "--output",
                    default=f"{date.today()}.log",
                    help="custom output file")
parser.add_argument("-r", "--record",
                    help="Record all of BDO's traffic and save it to a pcap file", action= BooleanOptionalAction)
parser.add_argument("-s", "--status",
                    help="Check the status of all requirements", action= BooleanOptionalAction)

args = parser.parse_args()

config.init("../config.ini")

if args.status:
    status_check.check_health()
    exit()
elif args.record:
    record.record()
    exit()
elif args.filename != None:
    open.open(args.filename, args.output)
    exit()
else:
    sniff.start_sniff(args.output)
    exit()
    
    
