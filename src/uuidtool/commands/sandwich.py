import argparse
from uuidtool.utils import *
from uuidtool.commands.edit import set_time




def sandwich(args: argparse.Namespace):
    
    uuid1 = get_uuid(args.uuid1)
    uuid2 = get_uuid(args.uuid2)
    
    version = get_version(uuid1)
    version2 = get_version(uuid2)
    
    if version not in (1, 2, 6, 7):
        error(f"This version of UUID ({version}) has no timestamp, so it can't be sandwiched")
    
    if version != version2:
        error(f"These 2 UUIDs have different versions ({version} and {version2})")
        

    t1 = get_timestamp(uuid1)
    t2 = get_timestamp(uuid2)
    
    if t1 == t2:
        error("These 2 UUIDs have the same timestamp")
    
    if t1 > t2:
        t1, t2 = t2, t1
    
    match version:
        case 1 | 6:
            clock_tick = 100
            highest = 0x5966c59f06182ff9c
            lowest = -GREGORIAN_UNIX_OFFSET
        case 2:
            clock_tick = int(V2_CLOCK_TICK * 1e9)
            highest = 0x5966c598621830000
            lowest = -GREGORIAN_UNIX_OFFSET
        case 7:
            clock_tick = 1_000_000
            highest = (2**48 - 1) * 1_000_000
            lowest = 0
    
    low = max(lowest, t1 + clock_tick)
    high = min(highest, t2)
    timestamps = range(low, high, clock_tick)
    
    if args.sort == "asc":
        it = timestamps
    if args.sort == "dsc":
        it = sorted(timestamps, reverse=True)
    elif args.sort == "alt":
        it = alt_sort(timestamps)
        
    for timestamp in it:
        print(set_time(uuid1, timestamp))


    
