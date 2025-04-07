# UUIDTool - A tool to manipulate UUIDs

UUIDTool is a command-line utility designed to work with Universally Unique Identifiers (UUIDs). It allows users to generate, analyze, and manipulate UUIDs in several ways

## Disclaimer

This tool is intended to be used in CTF challenges, penetration testing, and other ethical hacking activities. Do not use it for illegal or malicious purposes.

## Installation

```bash
pip install uuidtool
```

If you use an [externally managed environment](https://packaging.python.org/en/latest/specifications/externally-managed-environments/):

```bash
sudo apt install pipx
pipx install uuidtool
```

Or

```bash
git clone https://github.com/crazycat256/uuidtool.git
cd uuidtool
pipx install .
```

## Usage

### CLI Usage

```bash
$ uuidtool info e63034d3-acc1-11ef-8aaf-e63af2894db7                                    
UUID: e63034d3-acc1-11ef-8aaf-e63af2894db7
Version: 1 (Time-based)
Variant: 8 (RFC 9562)
Timestamp: 2024-11-27 13:17:06 GMT (1732713426235925100)
Clock Sequence: 2735
Node: e6:3a:f2:89:4d:b7

$ uuidtool edit e63034d3-acc1-11ef-8aaf-e63af2894db7 -t 1732713730 -n 11:22:33:44:55:66
9b3eed00-acc2-11ef-8aaf-112233445566

$ uuidtool new -v 1 -t 1732718667 -c 0
19ed5780-acce-11ef-8000-e63af2894db7

$ uuidtool range e3aa7ac2-acd6-11ef-b995-e63af2894db7 5
e3aa7ac2-acd6-11ef-b995-e63af2894db7
e3aa7ac1-acd6-11ef-b995-e63af2894db7
e3aa7ac3-acd6-11ef-b995-e63af2894db7
e3aa7ac0-acd6-11ef-b995-e63af2894db7
e3aa7ac4-acd6-11ef-b995-e63af2894db7

$ uuidtool sandwich 4977ce85-acd9-11ef-801a-e63af2894db7 4977ce8b-acd9-11ef-801a-e63af2894db7
4977ce88-acd9-11ef-801a-e63af2894db7
4977ce87-acd9-11ef-801a-e63af2894db7
4977ce89-acd9-11ef-801a-e63af2894db7
4977ce86-acd9-11ef-801a-e63af2894db7
4977ce8a-acd9-11ef-801a-e63af2894db7
```

More examples can be found in [USAGE.md](USAGE.md#cli-usage).

### Usage as a Library

```python
import uuidtool, time

# Generate a UUID
uuidtool.uuid_v1(time.time_ns())

# Edit a UUID
uuidtool.edit_uuid("a0b0314a-13a0-11f0-97aa-644ed7120002", (time.time_ns() - 3600) * 1e9)

# Generate a range of UUIDs
uuidtool.uuid_range("a0b0314a-13a0-11f0-97aa-644ed7120002", 10, "asc")

# Generate a sandwich of UUIDs
uuidtool.sandwich("2e9d7ae1-13a6-11f0-86ee-644ed7120002", "2e9d7aeb-13a6-11f0-a54c-644ed7120002", "asc")
```

More examples can be found in [USAGE.md](USAGE.md#usage-as-a-library).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
