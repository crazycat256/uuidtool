import argparse
from uuidtool.utils import *
from uuidtool.commands.info import info
from uuidtool.commands.edit import edit
from uuidtool.commands.sandwich import sandwich
from uuidtool.commands.range import range
from uuidtool.commands.new import new


EPILOG = """some documentation about UUIDs:
- RCF 9562: https://datatracker.ietf.org/doc/html/rfc9562
- RFC 4122: https://datatracker.ietf.org/doc/html/rfc4122 (obsolete)
- UUIDv2 documentation: ttps://pubs.opengroup.org/onlinepubs/9696989899/chap5.htm#tagcjh_08_02_01_01
"""

def main():
    parser = argparse.ArgumentParser(
        prog="uuidtool",
        description="UUIDTool - A tool to manipulate UUIDs",
        epilog=EPILOG,
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")
    
    parser_info = subparsers.add_parser("info", help="Display information about a UUID")
    parser_info.add_argument("uuid", help="UUID to display information about")

    parser_edit = subparsers.add_parser("edit", help="Edit a UUID")
    parser_edit.add_argument("uuid", help="UUID to edit")
    parser_edit.add_argument("-t", "--time", help="Time to use for the UUID v1, v2, v6 or v7")
    parser_edit.add_argument("-c", "--clock-sequence", help="Clock sequence to use for UUID v1 or v2")
    parser_edit.add_argument("-n", "--node", help="Node (MAC address) to use for UUID v1, v2 or v6")
    parser_edit.add_argument("--local-id", help="Local ID to use for UUID v2")
    parser_edit.add_argument("--local-domain", help="Local domain to use for UUID v2")
    parser_edit.add_argument("--custom-a", help="Custom field A to use for UUID v8")
    parser_edit.add_argument("--custom-b", help="Custom field B to use for UUID v8")
    parser_edit.add_argument("--custom-c", help="Custom field C to use for UUID v8")

    parser_sandwich = subparsers.add_parser("sandwich", help="Print all UUIDs whose timestamp is between those of the two given UUIDs")
    parser_sandwich.add_argument("uuid1", help="First UUID")
    parser_sandwich.add_argument("uuid2", help="Second UUID")
    parser_sandwich.add_argument("-s", "--sort", choices=["asc", "desc", "alt"], default="alt", help="Sort mode for the UUID range")
    
    parser_range = subparsers.add_parser("range", help="Generate a range of UUIDs whose timestamp is close to the timestamp of a given UUID")
    parser_range.add_argument("uuid", help="UUID to start the range")
    parser_range.add_argument("count", type=int, help="Number of UUIDs to generate")
    parser_range.add_argument("-s", "--sort", choices=["asc", "desc", "alt"], default="alt", help="Sort mode for the UUID range")

    parser_new = subparsers.add_parser("new", help="Generate a new UUID")
    parser_new.add_argument("-v", "--version", default=4, type=int, help="UUID version")
    parser_new.add_argument("-t", "--time", help="Time to use for UUID v1, v2, v6 or v7")
    parser_new.add_argument("-c", "--clock-sequence", help="Clock sequence for UUID v1 or v2")
    parser_new.add_argument("-n", "--node", help="Node (MAC address) for UUID v1, v2 or v6")
    parser_new.add_argument("--local-id", help="Local ID for UUID v2")
    parser_new.add_argument("--local-domain", help="Local domain for UUID v2")
    parser_new.add_argument("--name", help="Name for UUID v3 or v5")
    parser_new.add_argument("--namespace", help="Namespace for UUID v3 or v5")
    
    parser_new.add_argument("--custom-a", help="Custom field A for UUID v8")
    parser_new.add_argument("--custom-b", help="Custom field B for UUID v8")
    parser_new.add_argument("--custom-c", help="Custom field C for UUID v8")

    

    args = parser.parse_args()
    
    command: str = args.command
        
    match command:
        case "info":
            info(args)
        case "edit":
            edit(args)
        case "sandwich":
            sandwich(args)
        case "range":
            range(args)
        case "new":
            new(args)
        case None:
            parser.print_help()
        case _:
            error(f"Invalid command: {command}")
    



if __name__ == "__main__":
    main()