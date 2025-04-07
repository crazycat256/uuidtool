
# UUIDTool - Usage Guide

## Cli Usage

## Usage

**Commands:**

- [info](#info) - Get information about a UUID
- [edit](#edit) - Edit a UUID
- [new](#new) - Generate a new UUID
- [range](#range) - Generate all UUIDs whose timestamps are close to that of a given UUID
- [sandwich](#sandwich) - Generate all UUIDs whose timestamps are between those of two given UUIDs

**Options:**

Timestamps (`-t` / `--time`):

This options supports seconds and nanoseconds since the Unix epoch as well as iso8601 timestamps

```bash
-t 1732723900169486375
-t 1732723900
-t 2024-11-27T17:11:40
```

Sorting modes (`-s` / `--sort`):

- `asc`: Sort in ascending order (`[t-3, t-2, t-1, t, t+1, t+2, t+3]`)
- `desc`: Sort in descending order (`[t+3, t+2, t+1, t, t-1, t-2, t-3]`)
- `alt`: Sort in alternating order (`[t, t+1, t-1, t+2, t-2, t+3, t-3]`)

By default, `alt` is used

### Info

#### Usage

```bash
uuidtool info <uuid>
```

#### Examples

![Command output with a UUIDv1](doc/info_uuid1.png)
![Command output with a UUIDv4](doc/info_uuid4.png)
![Command output with a UUIDv6](doc/info_uuid6.png)

### Edit

#### Usage

```bash
uuidtool edit <uuid> [options]
```

#### Options

```bash
  -t TIME, --time TIME  Time to use for the UUID v1, v2, v6 or v7
  -c CLOCK_SEQUENCE, --clock-sequence CLOCK_SEQUENCE
                        Clock sequence to use for UUID v1 or v2
  -n NODE, --node NODE  Node (MAC address) to use for UUID v1, v2 or v6
  --local-id LOCAL_ID   Local ID to use for UUID v2
  --local-domain LOCAL_DOMAIN
                        Local domain to use for UUID v2
  --custom-a CUSTOM_A   Custom field A to use for UUID v8
  --custom-b CUSTOM_B   Custom field B to use for UUID v8
  --custom-c CUSTOM_C   Custom field C to use for UUID v8
```

#### Examples

```bash
$ uuidtool edit e63034d3-acc1-11ef-8aaf-e63af2894db7 -t 1732713730 -n 11:22:33:44:55:66
9b3eed00-acc2-11ef-8aaf-112233445566

$ uuidtool edit 01936dc5-a16a-7d24-b038-dd8b3e962c8c -t 0
00000000-0000-7d24-b038-dd8b3e962c8c

$ uuidtool edit 000003e8-acc2-21ef-b100-e63af2894db7 --local-id 1001 --local-domain 1
000003e9-acc2-21ef-b101-e63af2894db7
```

### New

#### Usage

```bash
uuidtool new [options]
```

#### Options

```bash
  -v VERSION, --version VERSION
                        UUID version
  -t TIME, --time TIME  Time to use for UUID v1, v2, v6 or v7
  -c CLOCK_SEQUENCE, --clock-sequence CLOCK_SEQUENCE
                        Clock sequence for UUID v1 or v2
  -n NODE, --node NODE  Node (MAC address) for UUID v1, v2 or v6
  --local-id LOCAL_ID   Local ID for UUID v2
  --local-domain LOCAL_DOMAIN
                        Local domain for UUID v2
  --name NAME           Name for UUID v3 or v5
  --namespace NAMESPACE
                        Namespace for UUID v3 or v5
  --custom-a CUSTOM_A   Custom field A for UUID v8
  --custom-b CUSTOM_B   Custom field B for UUID v8
  --custom-c CUSTOM_C   Custom field C for UUID v8
```

#### Examples

```bash
$ uuidtool new
ee505478-a4fc-4c7d-9361-10f6a261f404

$ uuidtool new -v 1 -t 1732718667 -c 0
19ed5780-acce-11ef-8000-e63af2894db7

$ uuidtool new -v 5 --namespace @dns --name HelloWorld
013a3dd2-e0e8-5595-891b-2135ce7321c3
```

### Range

#### Usage

```bash
uuidtool range <uuid> <count> [options]
```

#### Options

```bash
  -s {asc,desc,alt}, --sort {asc,desc,alt}
                        Sort mode for the UUID range
```

#### Example

```bash
$ uuidtool range e3aa7ac2-acd6-11ef-b995-e63af2894db7 5
e3aa7ac2-acd6-11ef-b995-e63af2894db7
e3aa7ac1-acd6-11ef-b995-e63af2894db7
e3aa7ac3-acd6-11ef-b995-e63af2894db7
e3aa7ac0-acd6-11ef-b995-e63af2894db7
e3aa7ac4-acd6-11ef-b995-e63af2894db7

$ uuidtool range 000003e8-acd7-21ef-9e00-e63af2894db7 5 -s asc
000003e8-acd5-21ef-9e00-e63af2894db7
000003e8-acd6-21ef-9e00-e63af2894db7
000003e8-acd7-21ef-9e00-e63af2894db7
000003e8-acd8-21ef-9e00-e63af2894db7
000003e8-acd9-21ef-9e00-e63af2894db7
```

### Sandwich

#### Usage

```bash
uuidtool sandwich <uuid1> <uuid2> [options]
```

#### Options

```bash
  -s {asc,desc,alt}, --sort {asc,desc,alt}
                        Sort mode for the UUID range
```

#### Example

```bash
$ uuidtool sandwich 4977ce85-acd9-11ef-801a-e63af2894db7 4977ce8b-acd9-11ef-801a-e63af2894db7
4977ce88-acd9-11ef-801a-e63af2894db7
4977ce87-acd9-11ef-801a-e63af2894db7
4977ce89-acd9-11ef-801a-e63af2894db7
4977ce86-acd9-11ef-801a-e63af2894db7
4977ce8a-acd9-11ef-801a-e63af2894db7
```

## Usage as a Library

### Creating a new UUID

```py
import uuidtool, time, os, random

uuid1 = uuidtool.uuid_v1(
    timestamp_ns=time.time_ns(),
    clock_seq=random.getrandbits(14),
    node=random.getrandbits(48)
)

uuid2 = uuidtool.uuid_v2(
    timestamp_ns=time.time_ns(),
    local_id=os.getuid(),
    local_domain=0, # 0=POSIX UID, 1=POSIX GID, 2=Organization
    clock_seq=random.getrandbits(6),
    node=random.getrandbits(48)
)

uuid3 = uuidtool.uuid_v3(
    namespace="@dns",
    name="example.com"
)

uuid4 = uuidtool.uuid_v4()

uuid5 = uuidtool.uuid_v5(
    namespace="@url",
    name="https://example.com"
)

uuid6 = uuidtool.uuid_v6(
    timestamp_ns=time.time_ns(),
    clock_seq=random.getrandbits(14),
    node=random.getrandbits(48)
)

uuid7 = uuidtool.uuid_v7(
    timestamp_ns=time.time_ns(),
    clock_seq=random.getrandbits(14)
)

uuid8 = uuidtool.uuid_v8(
    custom_a=random.getrandbits(48),
    custom_b=random.getrandbits(12),
    custom_c=random.getrandbits(62)
)
```

## Editing a UUID

```py
import uuidtool, time

uuid = uuidtool.edit_uuid(
    "a0b0314a-13a0-11f0-97aa-644ed7120002",
    timestamp_ns=(uuid.time - 3600) * 1e9, # 1 hour ago
)
```

## Sandwiching 2 UUIDs

```py
import uuidtool, time

t = time.time_ns()

uuid1 = uuidtool.uuid_v1(timestamp_ns=t)
uuid2 = uuidtool.uuid_v1(timestamp_ns=t + 1e3) # 1ms later

uuids = uuidtool.sandwich(uuid1, uuid2, sort="asc")
```

## Generating a range of UUIDs

```py
import uuidtool, time

t = time.time_ns()

uuid = uuidtool.uuid_v1()

uuids = uuidtool.uuid_range(uuid, 100, sort="desc")
```
