from typing import Literal
from uuidtool.commands.edit import set_time
from uuidtool.utils import *



def uuid_range(uuid: str | UUID, count: int, sort: Literal["asc", "desc", "alt"] = "alt"):
    """Generate a range of UUIDs around the timestamp of a given UUID

    :param uuid: The UUID to generate a range from. Will be in the middle of the range
    :param count: The number of UUIDs to generate
    :param sort: Way to sort the resulting UUIDs
    """
    
    uuid = get_uuid(uuid)
    if isinstance(count, float): count = int(count)
    
    if not isinstance(count, int):
        raise UUIDToolError(f"Invalid count: Expected an integer, got {count}")
    
    version = get_version(uuid)
        
    if count <= 1:
        raise UUIDToolError(f"Count must be greater than 1, got {count}")
    
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
            raise UUIDToolError(f"This version of UUID ({version}) has no timestamp, so it can't be ranged")
    
    t = get_timestamp(uuid)
    
    low = max(lowest, t - clock_tick * (count // 2))
    high = min(highest, t + clock_tick * (count // 2 + count % 2))
    timestamps = range(low, high, clock_tick)
    
    if sort == "asc":
        it = timestamps
    elif sort == "desc":
        it = reversed(timestamps)
    elif sort == "alt":
        it = alt_sort(timestamps)
    else:
        raise UUIDToolError(f"Unknown sort mode: {sort}")

    return [set_time(uuid, timestamp) for timestamp in it]