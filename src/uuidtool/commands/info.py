from uuid import UUID
from uuidtool.utils import *

OUTPUT_BASE = """UUID: {formatted_uuid}
{RED}Version: {version}{RESET}
{YELLOW}Variant: {variant}{RESET}"""


def info(uuid: str | UUID):
    """Get information about a UUID
    
    :param str_uuid: The UUID to get information about
    """
    
    uuid = get_uuid(uuid)
    version = get_version(uuid)
    variant = get_variant(uuid)

    match version:
        case 1: ret = v1(uuid)
        case 2: ret = v2(uuid)
        case 3: ret = v3(uuid)
        case 4: ret = v4(uuid)
        case 5: ret = v5(uuid)
        case 6: ret = v6(uuid)
        case 7: ret = v7(uuid)
        case 8: ret = v8(uuid)
        case _: ret = other(uuid)
        
    if not 7 < variant < 12:
        ret = f"{YELLOW}{BOLD}Warning: This UUID is not compliant with RFC 9562, some information may be incorrect{RESET}\n" + ret
        
    return ret


V1_V6_OUTPUT = OUTPUT_BASE + """
{GREEN}Timestamp: {time} ({time_ns}){RESET}
{MAGENTA}Clock Sequence: {clock}{RESET}
{BLUE}Node: {node}{RESET}"""

def v1(uuid: UUID):
    
    s = str(uuid)
    formatted_uuid = (
        f"{GREEN}{s[:8]}{RESET}-"
        f"{GREEN}{s[9:13]}{RESET}-"
        f"{RED}{s[14]}{GREEN}{s[15:18]}{RESET}-"
        f"{YELLOW}{s[19]}{MAGENTA}{s[20:23]}{RESET}-"
        f"{BLUE}{s[24:]}{RESET}"
    )
    
    uuid_time_ns = get_timestamp(uuid)
    formatted_time = strftime(uuid_time_ns)

    return V1_V6_OUTPUT.format(
        **ALL_COLORS,
        **get_common_info(uuid),
        formatted_uuid=formatted_uuid,
        time=formatted_time,
        time_ns=uuid_time_ns,
        clock=uuid.clock_seq
    )
    
V2_OUTPUT = OUTPUT_BASE + """
{GREEN}Timestamp: {time} ({time_ns}){RESET}
{BRIGHT_CYAN}Local ID: {local_id}{RESET}
{CYAN}Local Domain: {local_domain}{RESET}
{MAGENTA}Clock Sequence: {clock}{RESET}
{BLUE}Node: {node}{RESET}

Note: Variant uses only 2 bits, the 2 least significant bits of the variant are part of the Clock Sequence"""

# https://laconsole.dev/blog/comprendre-uuid/
# https://playfulprogramming.com/posts/what-happened-to-uuid-v2#problems-with-uuidv2
def v2(uuid: UUID):
        
    local_id = uuid.int >> 96
    timestamp_ns = get_timestamp(uuid)
        
    clock_sequence = (uuid.int >> 56) & 0x3f
    
    local_domain = (uuid.int >> 48) & 0xff
    match local_domain:
        case 0: local_domain = f"{local_domain} (POSIX UID)"
        case 1: local_domain = f"{local_domain} (POSIX GID)"
        case 2: local_domain = f"{local_domain} (Organization)"
        case _: local_domain = f"{local_domain} (Unknown)"
    
    s = str(uuid)
    formatted_uuid = (
        f"{BRIGHT_CYAN}{s[:8]}{RESET}-"
        f"{GREEN}{s[9:13]}{RESET}-"
        f"{RED}{s[14]}{GREEN}{s[15:18]}{RESET}-"
        f"{YELLOW}{s[19]}{MAGENTA}{s[20]}{RESET}{CYAN}{s[21:23]}{RESET}-"
        f"{BLUE}{s[24:]}{RESET}"
    )
    formatted_time = strftime(timestamp_ns)
    
    return V2_OUTPUT.format(
        **ALL_COLORS,
        **get_common_info(uuid),
        formatted_uuid=formatted_uuid,
        time=formatted_time,
        time_ns=timestamp_ns,
        local_id=local_id,
        local_domain=local_domain,
        clock=clock_sequence
    )
    
V3_V5_OUTPUT = OUTPUT_BASE + """
{GREEN}Hash ({hash_type}): {hash}{RESET}

Note: Variant uses only 2 bits, the 2 least significant bits of the variant are part of the hash"""


def v3(uuid: UUID):
    
    s = str(uuid)
    formatted_uuid = (
        f"{GREEN}{s[:8]}{RESET}-"
        f"{GREEN}{s[9:13]}{RESET}-"
        f"{RED}{s[14]}{GREEN}{s[15:18]}{RESET}-"
        f"{YELLOW}{s[19]}{GREEN}{s[20:23]}{RESET}-"
        f"{GREEN}{s[24:]}{RESET}"
    )
    
    x = f"{RESET}{BRIGHT_WHITE}x{GREEN}"
    
    uuid_hash = uuid.hex[:12] + x + uuid.hex[13:16] + x + uuid.hex[17:]
        
    return V3_V5_OUTPUT.format(
        **ALL_COLORS,
        **get_common_info(uuid),
        formatted_uuid=formatted_uuid,
        hash_type="MD5",
        hash=uuid_hash
    )

V4_OUTPUT = OUTPUT_BASE + """
Random bits: 122{RESET}"""

def v4(uuid: UUID):
    
    s = str(uuid)
    formatted_uuid = (
        f"{s[:8]}-"
        f"{s[9:13]}-"
        f"{RED}{s[14]}{RESET}{s[15:18]}-"
        f"{YELLOW}{s[19]}{RESET}{s[20:23]}-"
        f"{s[24:]}"
    )
    
    return V4_OUTPUT.format(
        **ALL_COLORS,
        **get_common_info(uuid),
        formatted_uuid=formatted_uuid
    )

def v5(uuid: UUID):
    
    s = str(uuid)
    formatted_uuid = (
        f"{GREEN}{s[:8]}{RESET}-"
        f"{GREEN}{s[9:13]}{RESET}-"
        f"{RED}{s[14]}{GREEN}{s[15:18]}{RESET}-"
        f"{YELLOW}{s[19]}{GREEN}{s[20:23]}{RESET}-"
        f"{GREEN}{s[24:]}{RESET}"
    )
    
    x = f"{RESET}{BRIGHT_WHITE}x{GREEN}"
    uuid_hash = uuid.hex[:12] + x + uuid.hex[13:16] + x + uuid.hex[17:] + RESET + 32 * "x"
        
    return V3_V5_OUTPUT.format(
        **ALL_COLORS,
        **get_common_info(uuid),
        formatted_uuid=formatted_uuid,
        hash_type="SHA1",
        hash=uuid_hash,
    )


def v6(uuid: UUID):
    
    s = str(uuid)
    formatted_uuid = (
        f"{GREEN}{s[:8]}{RESET}-"
        f"{GREEN}{s[9:13]}{RESET}-"
        f"{RED}{s[14]}{GREEN}{s[15:18]}{RESET}-"
        f"{YELLOW}{s[19]}{MAGENTA}{s[20:23]}{RESET}-"
        f"{BLUE}{s[24:]}{RESET}"
    )
    
    # https://github.com/stevesimmons/pyuuid6/blob/main/uuid6.py
    time_val = ((uuid.int >> 80) << 12) + ((uuid.int >> 64) & 4095)
    timestamp_ns = time_val * 100 - GREGORIAN_UNIX_OFFSET
    formatted_time = strftime(timestamp_ns)
    
    return V1_V6_OUTPUT.format(
        **ALL_COLORS,
        **get_common_info(uuid),
        formatted_uuid=formatted_uuid,
        time=formatted_time,
        time_ns=timestamp_ns,
        clock=uuid.clock_seq
    )

V7_OUTPUT = OUTPUT_BASE + """
{GREEN}Timestamp: {time} ({time_ns}){RESET}
Random bits: 74{RESET}
"""


def v7(uuid: UUID):
    
    timestamp_ms = uuid.int >> 80
    timestamp_ns = timestamp_ms * 1_000_000
    formatted_time = strftime(timestamp_ns)
    
    s = str(uuid)
    
    formatted_uuid = (
        f"{GREEN}{s[:8]}{RESET}-"
        f"{GREEN}{s[9:13]}{RESET}-"
        f"{RED}{s[14]}{RESET}{s[15:18]}-"
        f"{YELLOW}{s[19]}{RESET}{s[20:23]}-"
        f"{s[24:]}"
    )
    
    return V7_OUTPUT.format(
        **ALL_COLORS,
        **get_common_info(uuid),
        formatted_uuid=formatted_uuid,
        time=formatted_time,
        time_ns=timestamp_ns
    )
    
    
V8_OUTPUT = OUTPUT_BASE + """
{GREEN}Custom A: {custom_a:x}{RESET}
{MAGENTA}Custom B: {custom_b:x}{RESET}
{CYAN}Custom C: {custom_c:x}{RESET}

Possible timestamp: {possible_timestamp}"""

def v8(uuid: UUID):
    
    custom_a = uuid.int >> 80
    custom_b = (uuid.int >> 64) & 0x0fff
    custom_c = uuid.int & ((1 << 62) - 1)
    
    # It was originally planned that UUIDv8s would have a timestamp as specified here:
    # https://datatracker.ietf.org/doc/draft-peabody-dispatch-new-uuid-format/02/   4.5.  UUIDv8 Layout and Bit Order
    # But it was finally decided that they would only have custom fields (https://mailarchive.ietf.org/arch/msg/dispatch/mzWUPpHU9IS6NECdJWzUIdKKAeA/)
    # However, there are still some implementations that have it, like this one:
    # https://github.com/oittaa/uuid6-python/blob/abd320e3b03fc5bc54d2f37649ac84cf45a06193/src/uuid6/__init__.py#L150
    time_high = uuid.int >> 80
    time_mid = (uuid.int >> 64) & 0x0fff
    time_low = (uuid.int >> 54) & 0xff
    time_high_ns = time_high * 10**6
    time_mid_low_ns = ((time_mid << 8) | time_low) * 10**6 // 2**20
    possible_timestamp_ns = time_high_ns - time_mid_low_ns
    
    formatted_possible_timestamp = strftime(possible_timestamp_ns)
    
    s = str(uuid)
    
    formatted_uuid = (
        f"{GREEN}{s[:8]}{RESET}-"
        f"{GREEN}{s[9:13]}{RESET}-"
        f"{RED}{s[14]}{MAGENTA}{s[15:18]}{RESET}-"
        f"{YELLOW}{s[19]}{CYAN}{s[20:23]}{RESET}-"
        f"{CYAN}{s[24:]}{RESET}"
    )
    
    return V8_OUTPUT.format(
        **ALL_COLORS,
        **get_common_info(uuid),
        formatted_uuid=formatted_uuid,
        custom_a=custom_a,
        custom_b=custom_b,
        custom_c=custom_c,
        possible_timestamp=formatted_possible_timestamp
    )
    

OTHER_OUTPUT = """
UUID: {formatted_uuid}
{RED}Version: {version}{RESET}
{YELLOW}Variant: {variant}{RESET}

No additional information is available for this UUID"""

def other(uuid: UUID):
    
    s = str(uuid)
    formatted_uuid = (
        f"{s[:8]}-"
        f"{s[9:13]}-"
        f"{RED}{s[14]}{RESET}{s[15:18]}-"
        f"{YELLOW}{s[19]}{RESET}{s[20:23]}-"
        f"{s[24:]}"
    )
    
    return OTHER_OUTPUT.format(
        **ALL_COLORS,
        **get_common_info(uuid),
        formatted_uuid=formatted_uuid
    )



VERSIONS = {
    1: "Time-based",
    2: "DCE Security",
    3: "Name-based, MD5",
    4: "Random",
    5: "Name-based, SHA1",
    6: "Reordered Time",
    7: "Unix Epoch-based",
    8: "Custom"
}

def get_common_info(uuid: UUID) -> dict:
    
    version = get_version(uuid)
    version = f"{version} ({VERSIONS.get(version, 'Unknown')})"
    
    # https://datatracker.ietf.org/doc/html/rfc9562#name-variant-field
    variant = get_variant(uuid)
    
    if variant < 0x8:    variant = f"{variant:x} (NCS)"
    elif variant < 0xc: variant = f"{variant:x} (RFC 9562)"
    elif variant < 0xe: variant = f"{variant:x} (Microsoft)"
    else:              variant = f"{variant:x} (Future)"
    
    return {
        "version": version,
        "variant": variant,
        "node": ":".join(f"{b:02x}" for b in uuid.node.to_bytes(6))
    }
    








