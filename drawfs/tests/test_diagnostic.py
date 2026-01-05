#!/usr/bin/env python3
"""
test_diagnostic.py - Simple diagnostic to check basic device communication

Run this first to verify the drawfs device is responding properly.
"""

import os
import struct
import select
from drawfs_test import (
    DEV, make_frame, make_msg, parse_first_msg,
    REQ_HELLO, RPL_HELLO, RPL_ERROR,
    FH_SIZE, MH_SIZE
)


def main():
    print("Drawfs Device Diagnostic")
    print("=" * 40)

    # Check device exists
    if not os.path.exists(DEV):
        print(f"FAIL: Device {DEV} does not exist")
        return 1

    print(f"[OK] Device {DEV} exists")

    # Open device
    try:
        fd = os.open(DEV, os.O_RDWR)
        print(f"[OK] Opened device (fd={fd})")
    except OSError as e:
        print(f"FAIL: Cannot open device: {e}")
        return 1

    try:
        # Build HELLO request
        hello_payload = struct.pack("<HHII", 1, 0, 0, 65536)
        frame = make_frame(1, [make_msg(REQ_HELLO, 1, hello_payload)])
        print(f"[OK] Built HELLO frame ({len(frame)} bytes)")
        print(f"     Frame hex: {frame[:40].hex()}...")

        # Write HELLO
        written = os.write(fd, frame)
        print(f"[OK] Wrote {written} bytes")

        # Wait for response with poll
        p = select.poll()
        p.register(fd, select.POLLIN | select.POLLRDNORM)
        print("     Waiting for response (5 sec timeout)...")

        events = p.poll(5000)
        if not events:
            print("FAIL: Timeout waiting for response")
            print("      The kernel module may not be processing requests")
            return 1

        print(f"[OK] Poll returned events: {events}")

        # Read response
        response = os.read(fd, 4096)
        print(f"[OK] Read {len(response)} bytes")
        print(f"     Response hex: {response[:40].hex()}...")

        # Parse response
        if len(response) < FH_SIZE + MH_SIZE:
            print(f"FAIL: Response too short ({len(response)} bytes)")
            return 1

        msg_type, msg_id, payload = parse_first_msg(response)
        print(f"[OK] Parsed response: msg_type=0x{msg_type:04x}, msg_id={msg_id}")

        if msg_type == RPL_HELLO:
            status, major, minor, flags, max_reply = struct.unpack_from("<iHHII", payload, 0)
            print(f"[OK] RPL_HELLO received!")
            print(f"     status={status}")
            print(f"     server_version={major}.{minor}")
            print(f"     flags=0x{flags:08x}")
            print(f"     max_reply_bytes={max_reply}")
            if status == 0:
                print("\nSUCCESS: Device is responding correctly!")
                return 0
            else:
                print(f"\nWARNING: HELLO returned non-zero status: {status}")
                return 1

        elif msg_type == RPL_ERROR:
            err_code, err_detail, err_offset = struct.unpack_from("<III", payload, 0)
            print(f"FAIL: Got RPL_ERROR")
            print(f"     err_code={err_code}")
            print(f"     err_detail={err_detail}")
            print(f"     err_offset={err_offset}")
            return 1

        else:
            print(f"FAIL: Unexpected message type 0x{msg_type:04x}")
            return 1

    finally:
        os.close(fd)
        print(f"[OK] Closed device")


if __name__ == "__main__":
    exit(main())
