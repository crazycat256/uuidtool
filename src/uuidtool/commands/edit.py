from uuidtool.utils import *
from argparse import Namespace
from uuid import UUID


def edit(args: Namespace):
    """Edit a UUID

    Args:
        args (Namespace): The arguments passed to the command
    """
    
    uuid = get_uuid(args.uuid)
    
    version = get_version(uuid)
    check_args(args, version)
        
    uuid_time: str = args.time
    clock_sequence: str = args.clock_sequence
    node: str = args.node
    local_id: str = args.local_id
    local_domain: str = args.local_domain
    custom_a: str = args.custom_a
    custom_b: str = args.custom_b
    custom_c: str = args.custom_c
    
    
    if uuid_time is not None:
        timestamp_ns = parse_time(uuid_time)
        uuid = set_time(uuid, timestamp_ns)
    
    if clock_sequence is not None:
        try:
            clock_sequence = int(clock_sequence)
        except ValueError:
            error("Clock sequence must be an integer")
        uuid = set_clock_sequence(uuid, clock_sequence)
        
    if node is not None:
        try:
            node = int(node.replace(":", ""), 16)
        except ValueError:
            error("Node must be a 6 byte hex string or a MAC address")
        uuid = set_node(uuid, node)
        
    if local_id is not None:
        try:
            local_id = int(local_id)
        except ValueError:
            error("Local ID must be a 4 byte integer (0-4294967295)")
        uuid = set_local_id(uuid, local_id)
        
    if local_domain is not None:
        try:
            local_domain = int(local_domain)
        except ValueError:
            error("Local domain must be a 1 byte integer (0-255)")
        uuid = set_local_domain(uuid, local_domain)
        
    if custom_a is not None:
        try:
            custom_a = int(custom_a, 16)
        except ValueError:
            error("Custom field A must be an 8 byte hex string")
        uuid = set_custom_a(uuid, custom_a)
        
    if custom_b is not None:
        try:
            custom_b = int(custom_b, 16)
        except ValueError:
            error("Custom field B must be a 12 bit hex string")
        uuid = set_custom_b(uuid, custom_b)
        
    if custom_c is not None:
        try:
            custom_c = int(custom_c, 16)
        except ValueError:
            error("Custom field C must be a 16 byte hex string")
        uuid = set_custom_c(uuid, custom_c)
            
    print(uuid)
    
    

def set_time(uuid: UUID, new_time_ns: int) -> UUID:
    """Set the time for a UUID

    Args:
        uuid (UUID): The UUID to set the time for
        time_str (str): The time to set in nanoseconds, seconds or iso format

    Returns:
        UUID: The UUID with the new time set
    """
    
    version = get_version(uuid)
    
    if version not in (1, 2, 6, 7):
        error(f"Time is not supported for UUID version {version}")
        
    uuid_int = uuid.int
        
    if version == 1:
        timestamp = new_time_ns // 100 + GREGORIAN_UNIX_OFFSET // 100
        time_low = timestamp & 0xffffffff
        time_mid = (timestamp >> 32) & 0xffff
        time_high = (timestamp >> 48) & 0x0fff
        
        uuid_int &= 0x00000000_0000_f000_ffff_ffffffffffff
        uuid_int |= (time_low << 96) | (time_mid << 80) | (time_high << 64)
                
    elif version == 2:
        timestamp = new_time_ns + GREGORIAN_UNIX_OFFSET
        timestamp = timestamp // int(V2_CLOCK_TICK * 1e9)
        time_low = timestamp & 0xffff
        time_high = (timestamp >> 16) & 0x0fff
                    
        uuid_int &= 0xffffffff_0000_f000_ffff_ffffffffffff
        uuid_int |= (time_low << 80) | (time_high << 64)
                
    elif version == 6:
        timestamp = new_time_ns // 100 + GREGORIAN_UNIX_OFFSET // 100
        timestamp = ((timestamp >> 12) << 16) | (timestamp & 0xfff)
        
        uuid_int &= 0x00000000_000_f000_ffff_ffffffffffff
        uuid_int |= timestamp << 64
                
    elif version == 7:
        timestamp = new_time_ns // 1_000_000
        
        uuid_int &= 0x00000000_000_ffff_ffff_ffffffffffff
        uuid_int |= timestamp << 80
                    
    return UUID(int=uuid_int)



def set_clock_sequence(uuid: UUID, clock_sequence: int) -> UUID:
    """Set the clock sequence for a UUID

    Args:
        uuid (UUID): The UUID to set the clock sequence for
        clock_sequence (str): The clock sequence to set, this can be an integer

    Returns:
        UUID: The UUID with the new clock sequence set
    """
    
    version = get_version(uuid)
    
    if version not in (1, 2, 6):
        error(f"Clock sequence is not supported for UUID version {version}")
        
    uuid_int = uuid.int
        
    if version in (1, 6):
        
        if clock_sequence < 0 or clock_sequence > 16383:
            error(f"Clock sequence of UUID v{version} must be a 14 bit integer (0-16383)")
            
        uuid_int &= 0xffffffff_ffff_ffff_c000_ffffffffffff
        uuid_int |= clock_sequence << 48
        
    elif version == 2:
            
        if clock_sequence < 0 or clock_sequence > 63:
            error("Clock sequence of UUID v2 must be a 6 bit integer (0-63)")
            
        uuid_int &= 0xffffffff_ffff_ffff_c0ff_ffffffffffff
        uuid_int |= clock_sequence << 56
        
        
    return UUID(int=uuid_int)
        
    

def set_node(uuid: UUID, node: int) -> UUID:
    """Set the node for a UUID

    Args:
        uuid (UUID): The UUID to set the node for
        node (str): The node to set, this must be a MAC address or a 6 byte hex string

    Returns:
        UUID: The UUID with the new node set
    """
    
    version = get_version(uuid)
    
    if version not in (1, 2, 6):
        error(f"Node is not supported for UUID version {version}")
        
    uuid_int = uuid.int
        
    if node < 0 or node > 0xffffffffffff:
        error("Node must be 48 bits (6 bytes) long")
            
    uuid_int &= 0xffffffff_ffff_ffff_ffff_000000000000
    uuid_int |= node
        
    return UUID(int=uuid_int)

def set_local_id(uuid: UUID, local_id: int) -> UUID:
    """Set the local ID for a UUID v2

    Args:
        uuid (UUID): The UUID to set the local ID for
        local_id (int): The local ID to set

    Returns:
        UUID: The UUID with the new local ID set
    """
    
    version = get_version(uuid)
    
    if version != 2:
        error(f"Local ID is not supported for UUID version {version}")
        
    uuid_int = uuid.int
        
    if local_id < 0 or local_id > 0xffffffff:
        error("Local ID must be 32 bits (4 bytes) long")
            
    uuid_int &= 0x00000000_ffff_ffff_ffff_ffffffffffff
    uuid_int |= local_id << 96
        
    return UUID(int=uuid_int)

def set_local_domain(uuid: UUID, local_domain: int) -> UUID:
    """Set the local domain for a UUID v2

    Args:
        uuid (UUID): The UUID to set the local domain for
        local_domain (int): The local domain to set

    Returns:
        UUID: The UUID with the new local domain set
    """
    
    version = get_version(uuid)
    
    if version != 2:
        error(f"Local domain is not supported for UUID version {version}")
        
    uuid_int = uuid.int
    
    if local_domain < 0 or local_domain > 0xff:
        error("Local domain must be 8 bits (1 byte) long")
    
    uuid_int &= 0xffffffff_ffff_ffff_ff00_ffffffffffff
    uuid_int |= local_domain << 48
        
    return UUID(int=uuid_int)

def set_custom_a(uuid: UUID, custom_a: int) -> UUID:
    """Set the custom field A for a UUID v8

    Args:
        uuid (UUID): The UUID to set the custom field A for
        custom_a (int): The custom field A to set

    Returns:
        UUID: The UUID with the new custom field A set
    """
    
    version = get_version(uuid)
    
    if version != 8:
        error(f"Custom field A is not supported for UUID version {version}")
        
    uuid_int = uuid.int
    
    if custom_a < 0 or custom_a > 0xffffffffffff:
        error("Custom field A must be 48 bits (6 bytes) long")
    
    uuid_int &= 0x00000000_0000_ffff_ffff_ffffffffffff
    uuid_int |= custom_a << 80
        
    return UUID(int=uuid_int)

def set_custom_b(uuid: UUID, custom_b: int) -> UUID:
    """Set the custom field B for a UUID v8

    Args:
        uuid (UUID): The UUID to set the custom field B for
        custom_b (int): The custom field B to set

    Returns:
        UUID: The UUID with the new custom field B set
    """
    
    version = get_version(uuid)
    
    if version != 8:
        error(f"Custom field B is not supported for UUID version {version}")
        
    uuid_int = uuid.int
    
    if custom_b < 0 or custom_b > 0xfff:
        error("Custom field B must be 12 bits long")
    
    uuid_int &= 0xffffffff_ffff_f000_ffff_ffffffffffff
    uuid_int |= custom_b << 64
        
    return UUID(int=uuid_int)

def set_custom_c(uuid: UUID, custom_c: int) -> UUID:
    """Set the custom field C for a UUID v8

    Args:
        uuid (UUID): The UUID to set the custom field C for
        custom_c (int): The custom field C to set

    Returns:
        UUID: The UUID with the new custom field C set
    """
    
    version = get_version(uuid)
    
    if version != 8:
        error(f"Custom field C is not supported for UUID version {version}")
        
    uuid_int = uuid.int
    
    if custom_c < 0 or custom_c > 0x3fffffffffffffff:
        error("Custom field C must be 62 bits long")
    
    uuid_int &= 0xffffffff_ffff_ffff_c000_000000000000
    uuid_int |= custom_c
        
    return UUID(int=uuid_int)