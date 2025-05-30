from uuid import UUID

from uuidtool.utils import *


def edit_uuid(uuid: str | UUID, timestamp_ns: int=None, clock_seq: int=None, node: str=None, local_id: int=None,
         local_domain: int=None, custom_a: str=None, custom_b: str=None, custom_c: str=None):
    """Edit a UUID

    :param uuid: The UUID to edit
    :param timestamp_ns: Timestamp in nanoseconds
    :param clock_seq: The clock sequence
    :param node: The node (mac address)
    :param local_id: The local id
    :param local_domain: The local domain 
    :param custom_a: The custom field A
    :param custom_b: The custom field B
    :param custom_c: The custom field C
    """
    
    uuid = get_uuid(uuid)
    if isinstance(timestamp_ns, float):
        timestamp_ns = int(timestamp_ns)
    if isinstance(clock_seq, float):
        clock_seq = int(clock_seq)
    if isinstance(local_id, float):
        local_id = int(local_id)
    if isinstance(local_domain, float):
        local_domain = int(local_domain)
    
    version = get_version(uuid)
    check_args(version, timestamp_ns, clock_seq, node, local_id, local_domain, None, None, custom_a, custom_b, custom_c)
    
    
    if timestamp_ns is not None:
        uuid = set_time(uuid, timestamp_ns)
    
    if clock_seq is not None:
        uuid = set_clock_sequence(uuid, clock_seq)
        
    if node is not None:
        node = get_int(node, f"Invalid node: {node}", 16)
        uuid = set_node(uuid, node)
        
    if local_id is not None:
        uuid = set_local_id(uuid, local_id)
        
    if local_domain is not None:
        uuid = set_local_domain(uuid, local_domain)
        
    if custom_a is not None:
        custom_a = get_int(custom_a, f"Invalid custom A: {custom_a}", 16)
        uuid = set_custom_a(uuid, custom_a)
        
    if custom_b is not None:
        custom_b = get_int(custom_b, f"Invalid custom B: {custom_b}", 16)
        uuid = set_custom_b(uuid, custom_b)
        
    if custom_c is not None:
        custom_c = get_int(custom_c, f"Invalid custom C: {custom_c}", 16)
        uuid = set_custom_c(uuid, custom_c)
            
    return uuid
    
    

def set_time(uuid: UUID, new_time_ns: int) -> UUID:
    """Set the time for a UUID
    
    :param uuid: The UUID to set the time for
    :param new_time_ns: The time to set in nanoseconds, seconds or iso format
    """

    version = get_version(uuid)
        
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
        timestamp = timestamp // V2_CLOCK_TICK
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
        
    else:
        raise UUIDToolError(f"Time is not supported for UUID version {version}")
                    
    return UUID(int=uuid_int)



def set_clock_sequence(uuid: UUID, clock_seq: int) -> UUID:
    """Set the clock sequence for a UUID

    :param uuid: The UUID to set the clock sequence for
    :param clock_seq: The clock sequence to set, this can be an integer
    """
    
    version = get_version(uuid)
        
    uuid_int = uuid.int
        
    if version in (1, 6):
        
        if clock_seq < 0 or clock_seq > 16383:
            raise UUIDToolError(f"Clock sequence of UUID v{version} must be a 14 bit integer (0-16383), got {clock_seq}")
            
        uuid_int &= 0xffffffff_ffff_ffff_c000_ffffffffffff
        uuid_int |= clock_seq << 48
        
    elif version == 2:
            
        if clock_seq < 0 or clock_seq > 63:
            raise UUIDToolError(f"Clock sequence of UUID v2 must be a 6 bit integer (0-63), got {clock_seq}")
            
        uuid_int &= 0xffffffff_ffff_ffff_c0ff_ffffffffffff
        uuid_int |= clock_seq << 56
        
    else:
        raise UUIDToolError(f"Clock sequence is not supported for UUID version {version}")
        
        
    return UUID(int=uuid_int)
        
    

def set_node(uuid: UUID, node: int) -> UUID:
    """Set the node for a UUID

    :param uuid: The UUID to set the node for
    :param node: The node to set, this must be a MAC address or a 6 byte hex string
    """
    
    version = get_version(uuid)
    
    if version not in (1, 2, 6):
        raise UUIDToolError(f"Node is not supported for UUID version {version}")
        
    uuid_int = uuid.int
        
    if node < 0 or node > 0xffffffffffff:
        raise UUIDToolError(f"Node must be 48 bits (6 bytes) long, got {node}")
            
    uuid_int &= 0xffffffff_ffff_ffff_ffff_000000000000
    uuid_int |= node
        
    return UUID(int=uuid_int)

def set_local_id(uuid: UUID, local_id: int) -> UUID:
    """Set the local ID for a UUID v2
    
    :param uuid: The UUID to set the local ID for
    :param local_id: The local ID to set
    """
    
    version = get_version(uuid)
    
    if version != 2:
        raise UUIDToolError(f"Local ID is not supported for UUID version {version}")
        
    uuid_int = uuid.int
        
    if local_id < 0 or local_id > 0xffffffff:
        raise UUIDToolError(f"Local ID must be 32 bits (4 bytes) long, got {local_id}")
            
    uuid_int &= 0x00000000_ffff_ffff_ffff_ffffffffffff
    uuid_int |= local_id << 96
        
    return UUID(int=uuid_int)

def set_local_domain(uuid: UUID, local_domain: int) -> UUID:
    """Set the local domain for a UUID v2
    
    :param uuid: The UUID to set the local domain for
    :param local_domain: The local domain to set
    """
    
    version = get_version(uuid)
    
    if version != 2:
        raise UUIDToolError(f"Local domain is not supported for UUID version {version}")
        
    uuid_int = uuid.int
    
    if local_domain < 0 or local_domain > 0xff:
        raise UUIDToolError(f"Local domain must be 8 bits (1 byte) long, got {local_domain}")
    
    uuid_int &= 0xffffffff_ffff_ffff_ff00_ffffffffffff
    uuid_int |= local_domain << 48
        
    return UUID(int=uuid_int)

def set_custom_a(uuid: UUID, custom_a: int) -> UUID:
    """Set the custom field A for a UUID v8
    
    :param uuid: The UUID to set the custom field A for
    :param custom_a: The custom field A to set
    """
    
    version = get_version(uuid)
    
    if version != 8:
        raise UUIDToolError(f"Custom field A is not supported for UUID version {version}")
        
    uuid_int = uuid.int
    
    if custom_a < 0 or custom_a > 0xffffffffffff:
        raise UUIDToolError(f"Custom field A must be 48 bits (6 bytes) long, got {custom_a}")
    
    uuid_int &= 0x00000000_0000_ffff_ffff_ffffffffffff
    uuid_int |= custom_a << 80
        
    return UUID(int=uuid_int)

def set_custom_b(uuid: UUID, custom_b: int) -> UUID:
    """Set the custom field B for a UUID v8
    
    :param uuid: The UUID to set the custom field B for
    :param custom_b: The custom field B to set
    """
    
    version = get_version(uuid)
    
    if version != 8:
        raise UUIDToolError(f"Custom field B is not supported for UUID version {version}")
        
    uuid_int = uuid.int
    
    if custom_b < 0 or custom_b > 0xfff:
        raise UUIDToolError(f"Custom field B must be 12 bits long, got {custom_b}")
    
    uuid_int &= 0xffffffff_ffff_f000_ffff_ffffffffffff
    uuid_int |= custom_b << 64
        
    return UUID(int=uuid_int)

def set_custom_c(uuid: UUID, custom_c: int) -> UUID:
    """Set the custom field C for a UUID v8
    
    :param uuid: The UUID to set the custom field C for
    :param custom_c: The custom field C to set
    """
    
    version = get_version(uuid)
    
    if version != 8:
        raise UUIDToolError(f"Custom field C is not supported for UUID version {version}")
        
    uuid_int = uuid.int
    
    if custom_c < 0 or custom_c > 0x3fffffffffffffff:
        raise UUIDToolError(f"Custom field C must be 62 bits long, got {custom_c}")
    
    uuid_int &= 0xffffffff_ffff_ffff_c000_000000000000
    uuid_int |= custom_c
        
    return UUID(int=uuid_int)