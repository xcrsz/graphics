# Protocol Mismatch Resolution Backlog

This backlog tracks the work required to resolve protocol incompatibilities between drawfs and semadraw.

---

## Priority 1: Critical (Blocking Issues)

### 1.1 Remove Duplicate SURFACE_PRESENT Reply Struct
**Files**: `drawfs/sys/dev/drawfs/drawfs_proto.h`
**Effort**: Small
**Risk**: Low

**Problem**: Two conflicting struct definitions exist for SURFACE_PRESENT reply:
- `drawfs_surface_present_rep` (lines 176-181) - missing `cookie` field
- `drawfs_rpl_surface_present` (lines 199-203) - correct with `cookie` field

**Tasks**:
- [ ] Remove `struct drawfs_surface_present_rep` (lines 176-181)
- [ ] Grep codebase for any usage of the removed struct
- [ ] Update any code using the old struct name to use `drawfs_rpl_surface_present`
- [ ] Add comment explaining the `cookie` field semantics

---

### 1.2 Fix API_OVERVIEW.md Documentation
**Files**: `semadraw/docs/API_OVERVIEW.md`
**Effort**: Small
**Risk**: Low

**Problem**: Documentation lists incorrect message type values:
| Message | Documented | Correct (from protocol.zig) |
|---------|------------|----------------------------|
| HELLO_REPLY | `0x0002` | `0x8001` |
| ERROR | `0x00FF` | `0x80F0` |

**Tasks**:
- [ ] Update line 40: Change `HELLO_REPLY | 0x0002` to `HELLO_REPLY | 0x8001`
- [ ] Update line 51: Change `ERROR | 0x00FF` to `ERROR | 0x80F0`
- [ ] Add note about 0x8000 reply convention
- [ ] Review other message types for correctness
- [ ] Consider auto-generating docs from protocol.zig

---

### 1.3 Implement Missing SDCS Commands in drawfs Backend
**Files**: `semadraw/src/backend/drawfs.zig`
**Effort**: Medium
**Risk**: Medium

**Problem**: Only FILL_RECT (0x0010) and END (0x00F0) are implemented. Missing:
- RESET (0x0001)
- SET_BLEND (0x0004)
- SET_ANTIALIAS (0x0007)
- STROKE_RECT (0x0011)
- STROKE_LINE (0x0012)

**Tasks**:
- [ ] Implement STROKE_RECT (0x0011) - 36-byte payload: x, y, w, h, r, g, b, a, stroke_width
- [ ] Implement STROKE_LINE (0x0012) - 36-byte payload: x1, y1, x2, y2, r, g, b, a, stroke_width
- [ ] Implement SET_BLEND (0x0004) - blend mode state
- [ ] Implement SET_ANTIALIAS (0x0007) - antialias state
- [ ] Add render state struct to track blend/antialias modes
- [ ] Add tests for each new command

**Reference**: Check `semadraw/src/sdcs.zig` for exact payload formats.

---

### 1.4 Fix Hardcoded ioctl Encoding
**Files**: `semadraw/src/backend/drawfs.zig`
**Effort**: Medium
**Risk**: High (platform-specific)

**Problem**: Line 46 hardcodes the ioctl number:
```zig
const DRAWFSGIOC_MAP_SURFACE: u32 = 0xC0104402;
```
This assumes FreeBSD encoding with 16-byte struct size. Will fail on Linux or if struct changes.

**Tasks**:
- [ ] Create ioctl encoding function that computes at comptime
- [ ] Define platform-specific constants (`_IOC_*` values differ)
- [ ] Add validation that struct size matches expected
- [ ] Add comment documenting the encoding formula
- [ ] Consider build-time generation from kernel headers (longer term)

**Formula**: `_IOWR('D', 0x02, struct)` = `0xC0000000 | (sizeof(struct) << 16) | ('D' << 8) | 0x02`

---

## Priority 2: Moderate (May Cause Issues)

### 2.1 Document Version Compatibility Matrix
**Files**: New file `docs/VERSION_COMPAT.md` or add to existing docs
**Effort**: Small
**Risk**: Low

**Problem**: Version mismatch between components:
| Component | Version |
|-----------|---------|
| drawfs | v1.0 (0x0100) |
| semadraw IPC | v0.1 |
| SDCS | v0.1 |

**Tasks**:
- [ ] Document current version matrix
- [ ] Define version negotiation behavior during HELLO
- [ ] Decide: bump semadraw to v1.0, or document v0.1 as compatible with drawfs v1.0
- [ ] Add protocol version constants to shared location

---

### 2.2 Fix Field Naming Inconsistency
**Files**: `drawfs/sys/dev/drawfs/drawfs_proto.h` OR `drawfs/docs/PROTOCOL.md`
**Effort**: Small
**Risk**: Low

**Problem**: HELLO reply field naming differs:
- Header: `caps_bytes` (line 76)
- Spec: `max_reply_bytes`

**Tasks**:
- [ ] Decide canonical name (prefer `max_reply_bytes` to match request field)
- [ ] Update header or spec to use consistent name
- [ ] Add documentation comment explaining the field's purpose

---

### 2.3 Document Alignment Requirements
**Files**: `docs/ALIGNMENT.md` or add to protocol docs
**Effort**: Small
**Risk**: Low

**Problem**: Different alignment requirements:
- drawfs: 4-byte alignment
- SDCS: 8-byte alignment

**Tasks**:
- [ ] Document alignment requirements for each protocol
- [ ] Document padding requirements at protocol boundaries
- [ ] Review existing code for alignment issues
- [ ] Add alignment helpers if needed

---

## Priority 3: Improvements (Nice to Have)

### 3.1 Add Magic to semadraw IPC Header
**Files**: `semadraw/src/ipc/protocol.zig`, `semadraw/docs/API_OVERVIEW.md`
**Effort**: Small
**Risk**: Low (but breaks existing clients)

**Problem**: API_OVERVIEW.md mentions magic `0x53454D41` ("SEMA") but protocol.zig header has no magic field.

**Tasks**:
- [ ] Verify if magic is actually used in IPC
- [ ] Either remove from docs or add to protocol
- [ ] Consider for v1.0 protocol update

---

### 3.2 Consolidate Protocol Constants
**Files**: Multiple
**Effort**: Medium
**Risk**: Low

**Tasks**:
- [ ] Create shared constants file for message types
- [ ] Create shared constants file for error codes
- [ ] Auto-generate language bindings from single source of truth

---

### 3.3 Add Protocol Validation Tests
**Files**: New test files
**Effort**: Medium
**Risk**: Low

**Tasks**:
- [ ] Add roundtrip tests for all message types
- [ ] Add interop tests between drawfs and semadraw
- [ ] Add fuzz tests for protocol parsing
- [ ] CI integration for protocol validation

---

## Dependency Graph

```
1.1 (Remove duplicate struct)
     └── No dependencies

1.2 (Fix docs)
     └── No dependencies

1.3 (Implement SDCS commands)
     └── No dependencies, but review sdcs.zig first

1.4 (Fix ioctl encoding)
     └── No dependencies

2.1 (Version compat)
     └── After 1.1-1.4 are done, verify versions

2.2 (Field naming)
     └── After 1.1 (struct cleanup)

2.3 (Alignment docs)
     └── After 1.3 (SDCS commands)
```

---

## Acceptance Criteria

### For Critical Issues (P1)
- [ ] All P1 items implemented and tested
- [ ] No compilation errors in either codebase
- [ ] Existing tests pass
- [ ] drawfs backend can render all documented SDCS commands

### For Moderate Issues (P2)
- [ ] Documentation updated and consistent
- [ ] Version negotiation documented
- [ ] No ambiguity in field names

### For Improvements (P3)
- [ ] Tests added for protocol validation
- [ ] Shared constants reduce duplication
