#!/usr/bin/env python3
import serial
import time
import argparse
import sys

def send_values(port, values):
    """Send a line like "0,0,0,0,0\n" or "100,100,100,100,100\n" over serial."""
    if len(values) != 5 or any(v < 0 or v > 100 for v in values):
        raise ValueError("Need exactly five integers between 0 and 100")
    line = ','.join(str(v) for v in values) + '\n'
    port.write(line.encode('utf-8'))
    print(f"> sent: {line.strip()}")

def main():
    p = argparse.ArgumentParser(
        description="Continuously send 0s and 100s patterns to an ESP32 over USB-serial"
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

    # allow ESP32 to reset and print READY
    print(f"Opened {args.port} @ {args.baud} baud. Waiting for ESP32 to boot…")
    time.sleep(2)

    low = [0, 0, 0, 0, 0]
    high = [100, 100, 100, 100, 100]

    print("Starting continuous test: 100s ↔ 0s every 0.5 s")
    try:
        while True:
            send_values(ser, high)
            time.sleep(0.3)
            send_values(ser, low)
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        ser.close()
        print("Serial closed, exiting.")

if __name__ == "__main__":
    main()
