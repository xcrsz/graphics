# Shared Protocol Constants

This directory contains the canonical specification for protocol constants used across the graphics stack.

## Files

### protocol_constants.json

Single source of truth for all protocol constants across:
- **drawfs protocol** - Kernel interface for display/surface management
- **semadraw IPC** - Daemon-client communication protocol
- **SDCS** - Semantic Draw Command Stream format

## Usage

### Current State

The JSON specification documents all constants but code is not yet auto-generated. Implementers should:
1. Reference this file when adding new message types or error codes
2. Ensure new constants don't conflict with existing ones
3. Update this file when changing protocol constants

### Future: Code Generation

The specification is designed to support auto-generation of:
- `drawfs/sys/dev/drawfs/drawfs_proto.h` (C enums)
- `semadraw/src/ipc/protocol.zig` (Zig enums)
- `semadraw/src/sdcs.zig` (SDCS opcodes)

A generator script could produce language-specific headers from this JSON.

## Protocol Conventions

### Message Type Ranges

| Range | Purpose |
|-------|---------|
| 0x0001-0x0FFF | Requests (client → server) |
| 0x8000-0x8FFF | Replies (server → client) |
| 0x9000-0x9FFF | Events (async server → client) |

### Reply Convention

Reply types set the high bit: `reply = request | 0x8000`

Example: `HELLO (0x0001)` → `HELLO_REPLY (0x8001)`

### Error Codes

Error codes are numeric, starting at 0 (success). Each protocol layer has its own error code namespace to allow layer-specific errors.

## Validation

To validate constants match implementations:

```bash
# Check drawfs constants
grep -E "DRAWFS_(REQ|RPL|ERR|EVT)_" drawfs/sys/dev/drawfs/drawfs_proto.h

# Check semadraw IPC constants
grep -E "(hello|create_surface|error)" semadraw/src/ipc/protocol.zig

# Check SDCS opcodes
grep "pub const.*0x00" semadraw/src/sdcs.zig
```
