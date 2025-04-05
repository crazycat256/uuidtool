import os
import random
import time
from uuid import *

from uuidtool.utils import *


def new(version: int=None, uuid_time: str=None, clock_sequence: str=None, node: str=None,
        local_id: str=None, local_domain: str=None, namespace: str=None, name: str=None,
        custom_a: str=None,  custom_b: str=None,  custom_c: str=None):
    """Generate a new UUID

    Args:
        :param version: The version of the new UUID
        :param uuid_time: Timestamp to set
        :param clock_sequence: The clock sequence to use
        :param node: The node (mac address) to use
        :param local_id: The local id to use
        :param local_domain: The local domain to use
        :param namespace: The namespace to use
        :param name: The name to use
        :param custom_a: A custom field
        :param custom_b: A custom field
        :param custom_c: A custom field
    """
    
    check_args(version, uuid_time, clock_sequence, node, local_id,
               local_domain, namespace, name,custom_a,  custom_b,  custom_c)
    
    timestamp_ns = None
    if uuid_time is not None:
        timestamp_ns = parse_time(uuid_time)
    
    clock_sequence = get_int(clock_sequence, "Clock sequence must be an integer")
    node = get_int(node, "Node must be a hex string or a MAC address", 16)
    local_id = get_int(local_id, "Local ID must be an integer")
    local_domain = get_int(local_domain, "Local domain must be an integer")
    namespace: str = namespace
    name: str = name
    custom_a = get_int(custom_a, "Custom field A must be a hex string", 16)
    custom_b = get_int(custom_b, "Custom field B must be a hex string", 16)
    custom_c = get_int(custom_c, "Custom field C must be a hex string", 16)

    uuid = None
    match version:
        case 1:
            uuid = uuid_v1(timestamp_ns, clock_sequence, node)
        case 2:
            uuid = uuid_v2(local_id, timestamp_ns, local_domain, clock_sequence, node)
        case 3:
            uuid = uuid_v3(namespace, name)
        case 4:
            uuid = uuid4()
        case 5:
            uuid = uuid_v5(namespace, name)
        case 6:
            uuid = uuid_v6(timestamp_ns, clock_sequence, node)
        case 7:
            uuid = uuid_v7(timestamp_ns, clock_sequence)
        case 8:
            uuid = uuid_v8(custom_a, custom_b, custom_c)
        case _:
            error("UUID version must be between 1 and 8")

    return uuid
    
    
def uuid_v1(timestamp_ns: int = None, clock_seq: int = None, node: int = None) -> UUID:
    """Generate a version 1 UUID
    
    Args:
        timestamp_ns (int): The timestamp in nanoseconds since the Unix epoch (60 bits)
        clock_seq (int): The clock sequence (14 bits)
        node (int): The MAC address (48 bits)
        
    Returns:
        UUID: The generated UUID
        
    """
    
    if timestamp_ns is None:
        timestamp_ns = time.time_ns()
        
    if clock_seq is None:
        clock_seq = random.getrandbits(14)
        
    if node is None:
        node = getnode()
        
    if not 0 <= timestamp_ns < 2**64:
        error("Timestamp must be 64 bits long")
        
    if not 0 <= clock_seq < 2**14:
        error("Clock sequence must be 14 bits long")
        
    if not 0 <= node < 2**48:
        error("Node must be 48 bits long")
    
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
def uuid_v2(local_id: int = None, timestamp_ns: int = None, local_domain: int = None, clock_sequence = None, node: int = None) -> UUID:
    """Generate a version 2 UUID
    
    Args:
        local_id (int): The local ID (32 bits)
        timestamp (int): The timestamp (32 bits)
        local_domain (int): The local domain (8 bits)
        mac (int): The MAC address (48 bits)
        
    Returns:
        UUID: The generated UUID
        
    """
    
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
        
    if clock_sequence is None:
        clock_sequence = random.getrandbits(6)
        
    if node is None:
        node = getnode()
        
    if not 0 <= local_id < 2**32:
        error("Local ID must be 32 bits long")
    
    if not 0 <= local_domain < 2**8:
        error("Local domain must be 8 bits long")
    
    if not 0 <= clock_sequence < 2**6:
        error("Clock sequence must be 6 bits long")
    
    timestamp = (timestamp_ns + GREGORIAN_UNIX_OFFSET) // int(V2_CLOCK_TICK * 1e9)
    time_low = timestamp & 0xffff
    time_hi = (timestamp >> 16) & 0xfff
    time_hi_version = time_hi | 0x2000
    
    clock_seq_variant = clock_sequence | 0x80
    
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

def uuid_v3(namespace_str: str, name: str) -> UUID:
    """Generate a version 3 UUID
    
    Args:
        namespace (str): The namespace
        name (str): The name
    
    Returns:
        UUID: The generated UUID
    """
    
    if namespace_str is None or name is None:
        error("Namespace and name are required for UUID v3")
        
    if not is_uuid(namespace_str) and namespace_str not in namespaces:
        error("Namespace must be a UUID")
    
    namespace = UUID(namespace_str) if is_uuid(namespace_str) else namespaces[namespace_str]
    
    return uuid3(namespace, name)


def uuid_v5(namespace_str: str, name: str) -> UUID:
    """Generate a version 5 UUID
    
    Args:
        namespace (str): The namespace
        name (str): The name
    
    Returns:
        UUID: The generated UUID
    """
    
    if namespace_str is None or name is None:
        error("Namespace and name are required for UUID v5")
        
    if not is_uuid(namespace_str) and namespace_str not in namespaces:
        error("Namespace must be a UUID")
    
    namespace = UUID(namespace_str) if is_uuid(namespace_str) else namespaces[namespace_str]
    
    return uuid5(namespace, name)


def uuid_v6(timestamp_ns: int = None, clock_seq: int = None, node: int = None) -> UUID:
    """Generate a version 6 UUID
    
    Args:
        timestamp_ns (int): The timestamp in nanoseconds since the Unix epoch (60 bits)
        clock_seq (int): The clock sequence (14 bits)
        node (int): The MAC address (48 bits)
        
    Returns:
        UUID: The generated UUID
        
    """
    
    if timestamp_ns is None:
        timestamp_ns = time.time_ns()
        
    if clock_seq is None:
        clock_seq = random.getrandbits(14)
        
    if node is None:
        node = getnode()
        
    if not 0 <= timestamp_ns < 2**64:
        error("Timestamp must be 64 bits long")
        
    if not 0 <= clock_seq < 2**14:
        error("Clock sequence must be 14 bits long")
        
    if not 0 <= node < 2**48:
        error("Node must be 48 bits long")
    
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

def uuid_v7(timestamp_ns: int = None, clock_seq: int = None) -> UUID:
    """Generate a version 7 UUID
    
    Args:
        timestamp_ns (int): The timestamp in nanoseconds since the Unix epoch (60 bits)
        clock_seq (int): The clock sequence (14 bits)
        node (int): The MAC address (48 bits)
        
    Returns:
        UUID: The generated UUID
        
    """
    
    if timestamp_ns is None:
        timestamp_ns = time.time_ns()
        
    if clock_seq is None:
        clock_seq = random.getrandbits(14)
        
    if not 0 <= timestamp_ns < 2**64:
        error("Timestamp must be 64 bits long")
        
    if not 0 <= clock_seq < 2**14:
        error("Clock sequence must be 14 bits long")
    
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
    
    Args:
        custom_a (int): Custom field A (48 bits)
        custom_b (int): Custom field B (12 bits)
        custom_c (int): Custom field C (62 bits)
        
    Returns:
        UUID: The generated UUID
        
    """
    
    if custom_a is None:
        custom_a = random.getrandbits(48)
        
    if custom_b is None:
        custom_b = random.getrandbits(12)
        
    if custom_c is None:
        custom_c = random.getrandbits(62)
        
    if not 0 <= custom_a < 2**48:
        error("Custom field A must be 48 bits long")
        
    if not 0 <= custom_b < 2**12:
        error("Custom field B must be 12 bits long")
        
    if not 0 <= custom_c < 2**62:
        error("Custom field C must be 62 bits long")
    
    return UUID(int=(
        (custom_a << 80) |
        (0x8000 << 64) |
        (custom_b << 64) |
        (0x8000 << 48) |
        custom_c
    ))
    


