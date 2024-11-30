from uuidtool.utils import *
from argparse import Namespace
from uuidtool.commands.edit import set_time


def range(args: Namespace):
    """Generate a range of UUIDs whose timestamp is close to the timestamp of a given UUID

    Args:
        args (Namespace): The arguments passed to the command
    """
    
    uuid = get_uuid(args.uuid)
    
    count = args.count
    version = get_version(uuid)
    
    if version not in (1, 2, 6, 7):
        error(f"This version of UUID ({version}) has no timestamp, so it can't be used with this command")
        
    if count <= 1:
        error("Count must be greater than 1")
    
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
    
    t = get_timestamp(uuid)
    
    low = max(lowest, t - clock_tick * (count // 2))
    high = min(highest, t + clock_tick * (count // 2 + count % 2))
    timestamps = range(low, high, clock_tick)
    
    if args.sort == "asc":
        it = timestamps
    if args.sort == "dsc":
        it = sorted(timestamps, reverse=True)
    elif args.sort == "alt":
        it = alt_sort(timestamps)
            
    for timestamp in it:
        uuid = set_time(uuid, timestamp)
        print(uuid)