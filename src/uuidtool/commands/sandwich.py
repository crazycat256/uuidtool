from typing import Literal
from uuidtool.commands.edit import set_time
from uuidtool.utils import *


def sandwich(uuid1: str | UUID, uuid2: str | UUID, sort: Literal["asc", "desc", "alt"] = "alt"):
    """Perform a sandwich attack

        :param uuid1: The first UUID
        :param uuid2: The second UUID
        :param sort: Way to sort the resulting UUIDs
    """
    uuid1 = get_uuid(uuid1)
    uuid2 = get_uuid(uuid2)
    
    version = get_version(uuid1)
    version2 = get_version(uuid2)
    
    if version != version2:
        raise UUIDToolError(f"These 2 UUIDs have different versions ({version} and {version2})")
        
    t1 = get_timestamp(uuid1)
    t2 = get_timestamp(uuid2)
    
    if t1 == t2:
        raise UUIDToolError(f"These 2 UUIDs have the same timestamp")
    
    if t1 > t2:
        t1, t2 = t2, t1
    
    match version:
        case 1 | 6:
            clock_tick = 100
            highest = 0x5966c59f06182ff9c
            lowest = -GREGORIAN_UNIX_OFFSET
        case 2:
            clock_tick = V2_CLOCK_TICK
            highest = 0x5966c598621830000
            lowest = -GREGORIAN_UNIX_OFFSET
        case 7:
            clock_tick = 1_000_000
            highest = (2**48 - 1) * 1_000_000
            lowest = 0
        case _:
            raise UUIDToolError(f"UUID version {version} has no timestamp, so it can't be sandwiched")
    
    low = max(lowest, t1 + clock_tick)
    high = min(highest, t2)
    timestamps = range(low, high, clock_tick)
    
    if sort == "asc":
        it = timestamps
    elif sort == "desc":
        it = sorted(timestamps, reverse=True)
    elif sort == "alt":
        it = alt_sort(timestamps)
    else:
        raise UUIDToolError(f"Unknown sort mode: {sort}")

    return [set_time(uuid1, timestamp) for timestamp in it]


    
