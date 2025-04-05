from uuidtool.commands.edit import set_time
from uuidtool.utils import *


def range(str_uuid: str, count: int, sort: str="alt"):
    """Generate a range of UUIDs around the timestamp of a given UUID

    Args:
        args (Namespace): The arguments passed to the command
        :param str_uuid: The UUID to generate a range from. Will be in the middle of the range
        :param count: The number of UUIDs to generate
        :param sort: Way to sort the resulting UUIDs
    """
    
    uuid = get_uuid(str_uuid)

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
    
    if sort == "asc":
        it = timestamps
    if sort == "dsc":
        it = sorted(timestamps, reverse=True)
    elif sort == "alt":
        it = alt_sort(timestamps)

    return [set_time(uuid, timestamp) for timestamp in it]