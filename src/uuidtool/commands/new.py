import os, random, time
from typing import Literal
from uuid import *
from uuidtool.utils import *


def new_uuid(version: int=None, timestamp_ns: int=None, clock_seq: int=None, node: str=None,
        local_id: int=None, local_domain: int=None, namespace: str=None, name: str=None,
        custom_a: str=None,  custom_b: str=None,  custom_c: str=None):
    """Generate a new UUID

    :param version: The version of the new UUID
    :param uuid_time: Timestamp to set
    :param clock_seq: The clock sequence to use
    :param node: The node (mac address) to use
    :param local_id: The local id to use
    :param local_domain: The local domain to use
    :param namespace: The namespace to use
    :param name: The name to use
    :param custom_a: A custom field
    :param custom_b: A custom field
    :param custom_c: A custom field
    """
    
    check_args(version, timestamp_ns, clock_seq, node, local_id,
               local_domain, namespace, name, custom_a, custom_b,  custom_c)
    
    node = get_int(node, f"Invalid node: {node}", 16)
    custom_a = get_int(custom_a, f"Invalid custom A: {custom_a}", 16)
    custom_b = get_int(custom_b, f"Invalid custom B: {custom_b}", 16)
    custom_c = get_int(custom_c, f"Invalid custom C: {custom_c}", 16)

    uuid = None
    match version:
        case 1:
            uuid = uuid_v1(timestamp_ns, clock_seq, node)
        case 2:
            uuid = uuid_v2(timestamp_ns, local_id, local_domain, clock_seq, node)
        case 3:
            uuid = uuid_v3(namespace, name)
        case 4:
            uuid = uuid_v4()
        case 5:
            uuid = uuid_v5(namespace, name)
        case 6:
            uuid = uuid_v6(timestamp_ns, clock_seq, node)
        case 7:
            uuid = uuid_v7(timestamp_ns)
        case 8:
            uuid = uuid_v8(custom_a, custom_b, custom_c)
        case _:
            raise UUIDToolError("UUID version must be between 1 and 8")

    return uuid
    
    
def uuid_v1(timestamp_ns: int = None, clock_seq: int = None, node: int = None) -> UUID:
    """Generate a version 1 UUID
    
    :param timestamp_ns: The timestamp in nanoseconds since the Unix epoch
    :param clock_seq: The clock sequence (14 bits)
    :param node: The MAC address (48 bits)
    """
    
    if isinstance(timestamp_ns, float):
        timestamp_ns = int(timestamp_ns)
    if isinstance(clock_seq, float):
        clock_seq = int(clock_seq)
    if isinstance(node, float):
        node = int(node)
    elif isinstance(node, str):
        node = get_int(node, f"Invalid node: {node}", 16)
    
    if timestamp_ns is None:
        timestamp_ns = time.time_ns()
        
    if clock_seq is None:
        clock_seq = random.getrandbits(14)
        
    if node is None:
        node = getnode()
        
    if not isinstance(timestamp_ns, int):
        raise UUIDToolError(f"Invalid timestamp: Expected an integer, got {timestamp_ns}")
        
    if not isinstance(clock_seq, int) or not 0 <= clock_seq < 2**14:
        raise UUIDToolError(f"Clock sequence: Expected a 14 bits integer, got {clock_seq}")
        
    if not isinstance(node, int) or not 0 <= node < 2**48:
        raise UUIDToolError(f"Node: Expected a 48 bits integer, got {node}")
        
    timestamp = (timestamp_ns + GREGORIAN_UNIX_OFFSET) // 100
    time_low = timestamp & 0xffffffff
    time_mid = (timestamp >> 32) & 0xffff
    time_hi_version = (timestamp >> 48) & 0x0fff
    time_hi_version |= 0x1000
    
    clock_seq_var = (clock_seq & 0x3fff) | 0x8000
    
    return UUID(int=(
        (time_low << 96) |
        (time_mid << 80) |
        (time_hi_version << 64) |
        (clock_seq_var << 48) |
        node
    ))

# https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_2_(date-time_and_MAC_address,_DCE_security_version)
# https://pubs.opengroup.org/onlinepubs/9696989899/chap5.htm#tagcjh_08_02_01_01
def uuid_v2(timestamp_ns: int = None, local_id: int = None, local_domain: int = None, clock_seq = None, node: int = None) -> UUID:
    """Generate a version 2 UUID

    :param timestamp_ns: The timestamp in nanoseconds since the Unix epoch
    :param local_id: The local ID (32 bits)
    :param local_domain: The local domain (8 bits)
    :param clock_seq: The clock sequence (6 bits)
    :param node: The MAC address (48 bits)
    """
    
    if isinstance(local_id, float):
        local_id = int(local_id)
    if isinstance(local_domain, float):
        local_domain = int(local_domain)
    if isinstance(clock_seq, float):
        clock_seq = int(clock_seq)
    if isinstance(node, float):
        node = int(node)
    if isinstance(node, str):
        node = get_int(node, f"Invalid node: {node}", 16)
    if isinstance(timestamp_ns, float):
        timestamp_ns = int(timestamp_ns)
    
    if local_domain is None:
        local_domain = 0
    
    if local_id is None:
        try:
            match local_domain:
                case 0:
                    local_id = os.getuid()
                case 1:
                    local_id = os.getgid()
                case _:
                    local_id = 1000
        except AttributeError:
            local_id = 1000
        
    if timestamp_ns is None:
        timestamp_ns = time.time_ns()
        
    if clock_seq is None:
        clock_seq = random.getrandbits(6)
        
    if node is None:
        node = getnode()
    
    if not isinstance(timestamp_ns, int):
        raise UUIDToolError(f"Invalid timestamp: Expected an integer, got {timestamp_ns}")
    
    if not isinstance(local_id, int) or not 0 <= local_id < 2**32:
        raise UUIDToolError(f"Invalid local ID: Expected a 32 bits integer, got {local_id}")
    
    if not isinstance(local_domain, int) or not 0 <= local_domain < 2**8:
        raise UUIDToolError(f"Invalid local domain: Expected a 8 bits integer, got {local_domain}")
    
    if not isinstance(clock_seq, int) or not 0 <= clock_seq < 2**6:
        raise UUIDToolError(f"Invalid clock sequence: Expected a 6 bits integer, got {clock_seq}")
    
    if not isinstance(node, int) or not 0 <= node < 2**48:
        raise UUIDToolError(f"Invalid node: Expected a 48 bits integer, got {node}")
    
    timestamp = (timestamp_ns + GREGORIAN_UNIX_OFFSET) // V2_CLOCK_TICK
    time_low = timestamp & 0xffff
    time_hi = (timestamp >> 16) & 0xfff
    time_hi_version = time_hi | 0x2000
    
    clock_seq_variant = clock_seq | 0x80
    
    return UUID(int=(
        (local_id << 96) |
        (time_low << 80) |
        (time_hi_version << 64) |
        (clock_seq_variant << 56) |
        (local_domain << 48) |
        node
    ))
    

namespaces = {
    "@dns": NAMESPACE_DNS,
    "@url": NAMESPACE_URL,
    "@oid": NAMESPACE_OID,
    "@x500": NAMESPACE_X500
}

def uuid_v3(namespace: str | Literal["@dns", "@url", "@oid", "@x500"], name: str) -> UUID:
    """Generate a version 3 UUID
    
    :param namespace: The namespace, this can be a UUID or one of the following: @dns, @url, @oid, @x500
    :param name: The name
    """
    
    if namespace is None:
        raise UUIDToolError("Namespace is required for UUID v3")
    if name is None:
        raise UUIDToolError("Name is required for UUID v3")
        
    if not is_uuid(namespace) and namespace not in namespaces:
        raise UUIDToolError(f"Invalid namespace: Expected a UUID or one of {namespaces.keys()}, got {namespace}")
    
    namespace = UUID(namespace) if is_uuid(namespace) else namespaces[namespace]
    
    return uuid3(namespace, name)


def uuid_v4() -> UUID:
    """Generate a version 4 UUID"""
    return uuid4()


def uuid_v5(namespace: str | Literal["@dns", "@url", "@oid", "@x500"], name: str) -> UUID:
    """Generate a version 5 UUID
    
    :param namespace: The namespace, this can be a UUID or one of the following: @dns, @url, @oid, @x500
    :param name: The name
    """
    
    if namespace is None:
        raise UUIDToolError("Namespace is required for UUID v5")
    if name is None:
        raise UUIDToolError("Name is required for UUID v5")
        
    if not is_uuid(namespace) and namespace not in namespaces:
        raise UUIDToolError(f"Invalid namespace: Expected a UUID or one of {namespaces.keys()}, got {namespace}")
    
    namespace = UUID(namespace) if is_uuid(namespace) else namespaces[namespace]
    
    return uuid5(namespace, name)


def uuid_v6(timestamp_ns: int = None, clock_seq: int = None, node: int = None) -> UUID:
    """Generate a version 6 UUID
    
    :param timestamp_ns: The timestamp in nanoseconds since the Unix epoch
    :param clock_seq: The clock sequence (14 bits)
    :param node: The MAC address (48 bits)
    """
    
    if isinstance(timestamp_ns, float):
        timestamp_ns = int(timestamp_ns)
    if isinstance(clock_seq, float):
        clock_seq = int(clock_seq)
    if isinstance(node, float):
        node = int(node)
    elif isinstance(node, str):
        node = get_int(node, f"Invalid node: {node}", 16)
    
    if timestamp_ns is None:
        timestamp_ns = time.time_ns()
        
    if clock_seq is None:
        clock_seq = random.getrandbits(14)
        
    if node is None:
        node = getnode()
        
    if not isinstance(timestamp_ns, int):
        raise UUIDToolError(f"Invalid timestamp: Expected an integer, got {timestamp_ns}")
        
    if not isinstance(clock_seq, int) or not 0 <= clock_seq < 2**14:
        raise UUIDToolError(f"Invalid clock sequence: Expected a 14 bits integer, got {clock_seq}")
        
    if not isinstance(node, int) or not 0 <= node < 2**48:
        raise UUIDToolError(f"Invalid node: Expected a 48 bits integer, got {node}")
    
    timestamp = (timestamp_ns + GREGORIAN_UNIX_OFFSET) // 100
    time_high_and_time_mid = (timestamp >> 12) & 0xffffffffffff
    time_low_and_version = (timestamp & 0x0fff) | 0x6000
    clock_seq_variant = (clock_seq & 0x3fff) | 0x8000
    
    return UUID(int=(
        (time_high_and_time_mid << 80) |
        (time_low_and_version << 64) |
        (clock_seq_variant << 48) |
        node
    ))

def uuid_v7(timestamp_ns: int = None) -> UUID:
    """Generate a version 7 UUID
    
    :param timestamp_ns: The timestamp in nanoseconds since the Unix epoch
    """
    
    if isinstance(timestamp_ns, float):
        timestamp_ns = int(timestamp_ns)
    
    if timestamp_ns is None:
        timestamp_ns = time.time_ns()
        
    if not isinstance(timestamp_ns, int):
        raise UUIDToolError(f"Invalid timestamp: Expected an integer, got {timestamp_ns}")
    
    timestamp = (timestamp_ns // 1_000_000) & 0xffffffffffff
    
    return UUID(int=(
        (timestamp << 80) |
        (0x7 << 76) |
        random.getrandbits(12) << 64 |
        0x8 << 60 |
        random.getrandbits(62)
    ))


def uuid_v8(custom_a: int = None, custom_b: int = None, custom_c: int = None) -> UUID:
    """Generate a version 8 UUID
    
    :param custom_a: Custom field A (48 bits)
    :param custom_b: Custom field B (12 bits)
    :param custom_c: Custom field C (62 bits)
    """
    
    if isinstance(custom_a, float):
        custom_a = int(custom_a)
    if isinstance(custom_b, float):
        custom_b = int(custom_b)
    if isinstance(custom_c, float):
        custom_c = int(custom_c)
    
    if custom_a is None:
        custom_a = random.getrandbits(48)
        
    if custom_b is None:
        custom_b = random.getrandbits(12)
        
    if custom_c is None:
        custom_c = random.getrandbits(62)
        
    if not 0 <= custom_a < 2**48:
        raise UUIDToolError(f"Invalid custom field A: Expected a 48 bits integer, got {custom_a}")
        
    if not 0 <= custom_b < 2**12:
        raise UUIDToolError(f"Invalid custom field B: Expected a 12 bits integer, got {custom_b}")
        
    if not 0 <= custom_c < 2**62:
        raise UUIDToolError(f"Invalid custom field C: Expected a 62 bits integer, got {custom_c}")
    
    return UUID(int=(
        (custom_a << 80) |
        (0x8000 << 64) |
        (custom_b << 64) |
        (0x8000 << 48) |
        custom_c
    ))
    


