from datetime import datetime, timedelta
from uuid import UUID

# https://uuid6.github.io/uuid6-ietf-draft/
GREGORIAN_UNIX_OFFSET = 12219292800000000000

# https://uuid.ramsey.dev/en/stable/rfc4122/version2.html#lossy-timestamps
V2_CLOCK_TICK = 429496729500
    
def check_args(version: int, uuid_time=None, clock_seq=None, node=None,
               local_id=None,local_domain=None, namespace=None, name=None,
               custom_a=None, custom_b=None, custom_c=None):
    
    if uuid_time is not None and version not in (1, 2, 6, 7):
        raise UUIDToolError("Timestamp is only available for UUID versions 1, 2, 6, and 7, not", version)
    if clock_seq is not None and version not in (1, 2, 6):
        raise UUIDToolError("Clock sequence is only available for UUID versions 1, 2 and 6, not", version)
    if node is not None and version not in (1, 2, 6):
        raise UUIDToolError("Node is only available for UUID versions 1, 2 and 6, not", version)
    if local_id is not None and version != 2:
        raise UUIDToolError("Local ID is only available for UUID version 2, not", version)
    if local_domain is not None and version != 2:
        raise UUIDToolError("Local domain is only available for UUID version 2, not", version)
    if namespace is not None and version not in (3, 5):
        raise UUIDToolError("Namespace is only available for UUID versions 3 and 5, not", version)
    if name is not None and version not in (3, 5):
        raise UUIDToolError("Name is only available for UUID versions 3 and 5, not", version)
    if custom_a is not None and version != 8:
        raise UUIDToolError("Custom field A is only available for UUID version 8, not", version)
    if custom_b is not None and version != 8:
        raise UUIDToolError("Custom field B is only available for UUID version 8, not", version)
    if custom_c is not None and version != 8:
        raise UUIDToolError("Custom field C is only available for UUID version 8, not", version)

def is_uuid(uuid_str: str) -> bool:
    """Check if a string is a valid UUID

    Args:
        uuid_str (str): The string to check

    Returns:
        bool: True if the string is a valid UUID, False otherwise
    """
    
    if not isinstance(uuid_str, str):
        return False
    
    uuid_str = uuid_str.replace("-", "")
    return len(uuid_str) == 32 and all(c in "0123456789abcdef" for c in uuid_str.lower())

def get_uuid(uuid: str | UUID) -> UUID:
    """Get a UUID

    Args:
        uuid (str | UUID): The string to convert to a UUID

    Returns:
        UUID: The UUID
    """
    
    if isinstance(uuid, UUID):
        return uuid
    
    if not is_uuid(uuid):
        raise UUIDToolError(f"{uuid} is not a valid UUID")
    return UUID(uuid)

def get_version(uuid: UUID) -> int:
    """Get the version of a UUID

    Args:
        uuid (UUID): The UUID to get the version from

    Returns:
        int: The version of the UUID
    """
    return (uuid.int >> 76) & 0xf

def get_variant(uuid: UUID) -> int:
    """Get the variant of a UUID

    Args:
        uuid (UUID): The UUID to get the variant from

    Returns:
        int: The variant of the UUID
    """
    return (uuid.int  >> 60) & 0xf

def get_timestamp(uuid: UUID) -> int:
    """Get the timestamp from a UUID

    Args:
        uuid (UUID): The UUID to get the timestamp from

    Returns:
        int: The timestamp in nanoseconds
    """
    version = get_version(uuid)
    
    if version == 1:
        return (uuid.time * 100) - GREGORIAN_UNIX_OFFSET
    elif version == 2:
        timestamp_low = (uuid.int >> 80) & 0xffff
        timestamp_high = (uuid.int >> 64) & 0x0fff
        return ((timestamp_high << 16) | timestamp_low) * V2_CLOCK_TICK - GREGORIAN_UNIX_OFFSET
    elif version == 6:
        return ((uuid.int >> 80) << 12) + ((uuid.int >> 64) & 4095) * 100 - GREGORIAN_UNIX_OFFSET
    elif version == 7:
        return (uuid.int >> 80) * 1_000_000

    
def alt_sort(timestamps: list[int]) -> list[int]:
    """Sort a list of timestamps in an alternating pattern.
    This function assumes that the timestamps are already sorted in ascending order.

    Args:
        timestamps (list[int]): The timestamps to sort

    Returns:
        list[int]: The sorted timestamps
    """
    out = []
    size = len(timestamps)
    if len(timestamps) % 2 != 0:
        idx = size // 2
        out.append(timestamps[idx])
        i1, i2 = idx - 1, idx + 1
    else:
        idx = size // 2
        i1, i2 = idx - 1, idx
        
    while i1 >= 0:
        out.append(timestamps[i1])
        if i2 < size:
            out.append(timestamps[i2])
        i1 -= 1
        i2 += 1
        
    return out

def parse_time(time_str: str | None) -> int:
    """Parse a string representing a time into an integer

    Args:
        time_str (str | None): The time string to parse

    Returns:
        int: The time in nanoseconds
    """
    
    if time_str is None:
        return None
    
    try:
        return int(datetime.fromisoformat(time_str).timestamp() * 1e9)
    except ValueError:
        pass
    
    try:
        time = float(time_str)
        if time > 0xffffffff:
            return int(time_str) 
        else:
            return int(time * 1e9)
    except ValueError:
        raise UUIDToolError(f"Invalid time format: {time_str}. It must be an integer (unix timestamp in nanoseconds) or an ISO 8601 formatted string")
        
def get_int(arg: str, error_message: str, base: int = 10) -> int:
    """Util function tu get an integer from a string

    Args:
        arg (str): The string to convert to an integer
        error_message (str): The error message to display if the conversion fails
        base (int, optional): The base to use for the conversion. Defaults to 10.

    Returns:
        int: The integer
    """
    
    if arg is None:
        return None
    
    if base == 16:
        arg = arg.replace(":", "")
    
    try:
        return int(arg, base)
    except ValueError:
        raise UUIDToolError(error_message)

def strftime(timestamp_ns: int) -> str:
    """Format a timestamp into a string

    Args:
        timestamp_ns (int): The timestamp to format

    Returns:
        str: The formatted string
    """
    
    try:
        dt = datetime(1970, 1, 1) + timedelta(seconds=timestamp_ns / 1e9)
        return dt.strftime("%Y-%m-%d %H:%M:%S %Z UTC")
    except (OSError, OverflowError, ValueError):
        return "Invalid timestamp"

class UUIDToolError(Exception):
    """Exception raised for errors in UUIDTool"""
    pass

RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
REVERSED = "\033[7m"

BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

BRIGHT_BLACK = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# This also includes other constants but we don't care
ALL_COLORS = {k: v for k, v in locals().items() if k.isupper() and not k.startswith("__")} 
