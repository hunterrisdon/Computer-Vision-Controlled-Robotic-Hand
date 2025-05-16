#!/usr/bin/env python3
import serial
import time
import argparse
import sys

def send_values(port, values):
    """Send a line like "20,35,50,75,100\n" over serial."""
    if len(values) != 5 or any(v < 0 or v > 100 for v in values):
        raise ValueError("Need exactly five integers between 0 and 100")
    line = ','.join(str(v) for v in values) + '\n'
    port.write(line.encode('utf-8'))
    print(f"> sent: {line.strip()}")

def main():
    p = argparse.ArgumentParser(
        description="Send 5-finger positions (0–100) to an ESP32 over USB-serial"
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

    # give the ESP32 a moment to reset and print READY
    print(f"Opened {args.port} @ {args.baud} baud. Waiting for ESP32 to boot…")
    time.sleep(2)

    # demo: send all zeros
    demo = [0, 0, 0, 0, 0]
    print("Demo send:", demo)
    send_values(ser, demo)

    # interactive loop
    print("\nEnter five positions (0–100), separated by spaces or commas.")
    print("Type 'q' to quit.")
    try:
        while True:
            raw = input("> ").strip()
            if raw.lower() in ('q', 'quit', 'exit'):
                break

            parts = raw.replace(',', ' ').split()
            if len(parts) != 5:
                print("? Please enter exactly 5 numbers.")
                continue

            try:
                vals = [int(p) for p in parts]
                send_values(ser, vals)
            except ValueError as e:
                print("?", e)

    finally:
        ser.close()
        print("Serial closed, exiting.")

if __name__ == "__main__":
    main()
