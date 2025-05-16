#!/usr/bin/env python3
import serial
import time
import argparse
import sys

def send_states(port, states):
    """Send a line like "0,1,2,1,0\n" over serial."""
    if len(states) != 5 or any(s not in (0,1,2) for s in states):
        raise ValueError("Need exactly five integers 0,1,2")
    line = ','.join(str(s) for s in states) + '\n'
    port.write(line.encode('utf-8'))
    print(f"> sent: {line.strip()}")

def main():
    p = argparse.ArgumentParser(
        description="Send 5-finger states to an ESP32 over USB-serial"
    )
    p.add_argument(
        '-p','--port',
        default='/dev/ttyUSB0',
        help="Serial device for the ESP32 (e.g. /dev/ttyUSB1 or /dev/ttyACM0)"
    )
    p.add_argument(
        '-b','--baud',
        type=int,
        default=115200,
        help="Baud rate (must match the ESP32 sketch)"
    )
    args = p.parse_args()

    try:
        ser = serial.Serial(args.port, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"ERROR: cannot open {args.port}: {e}")
        sys.exit(1)

    # give the ESP32 a moment to reset and print ?READY?
    print(f"Opened {args.port} @ {args.baud} baud. Waiting for ESP32 to boot?")
    time.sleep(2)

    # demo: send one sample frame
    demo = [0,1,2,1,0]
    print("Demo send:", demo)
    send_states(ser, demo)

    # interactive loop
    print("\nEnter five states (0=open,1=mid,2=closed), separated by spaces or commas.")
    print("Type 'q' to quit.")
    try:
        while True:
            raw = input("> ").strip()
            if raw.lower() in ('q','quit','exit'):
                break
            parts = raw.replace(',', ' ').split()
            if len(parts) != 5:
                print("? Please enter exactly 5 numbers.")
                continue
            try:
                vals = [int(p) for p in parts]
                send_states(ser, vals)
            except ValueError as e:
                print("?", e)
    finally:
        ser.close()
        print("Serial closed, exiting.")

if __name__ == "__main__":
    main()
