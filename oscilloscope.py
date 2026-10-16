"""Shrike-Fi USB oscilloscope laptop display.

Run on your COMPUTER (not Arduino IDE):
    python3 -m pip install pyserial matplotlib
    python3 oscilloscope.py

The app lists serial ports and asks you to choose if there is more than one.
Arduino Serial Monitor must be CLOSED before launching this script.
"""

from collections import deque
import statistics

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial
from serial.tools import list_ports

BAUD_RATE    = 115200
VIEW_SECONDS = 3.0
MAX_SAMPLES  = 5000


def choose_port():
    ports = list(list_ports.comports())
    if not ports:
        raise RuntimeError("No serial ports found. Connect Shrike-Fi using a data USB cable.")

    print("Available serial ports:")
    for index, port in enumerate(ports, start=1):
        print(f"  {index}. {port.device}  ({port.description})")

    if len(ports) == 1:
        selection = 1
        print("Using the only available port.")
    else:
        selection = int(input("Select Shrike-Fi port number: "))
    if not 1 <= selection <= len(ports):
        raise ValueError("Invalid port number")
    return ports[selection - 1].device


def main():
    port       = choose_port()
    connection = serial.Serial(port, BAUD_RATE, timeout=0)
    print(f"Connected to {port} at {BAUD_RATE} baud. Close the graph window to quit.")

    sample_times = deque(maxlen=MAX_SAMPLES)
    sample_volts = deque(maxlen=MAX_SAMPLES)
    incoming     = bytearray()

    fig, ax  = plt.subplots(figsize=(11, 5))
    (trace,) = ax.plot([], [], linewidth=1.4, label="GPIO1")
    info     = ax.text(0.015, 0.96, "Waiting for ESP32-S3 data...", transform=ax.transAxes,
                       va="top", fontsize=10,
                       bbox=dict(facecolor="white", alpha=0.8, edgecolor="lightgray"))

    ax.set_title("Shrike-Fi | ESP32-S3 USB Oscilloscope (GPIO1)")
    ax.set_xlabel("Time relative to newest sample (s)")
    ax.set_ylabel("Approximate voltage (V)")
    ax.set_xlim(-VIEW_SECONDS, 0)
    ax.set_ylim(-0.1, 3.2)
    ax.grid(True, alpha=0.35)
    ax.legend(loc="upper right")
    fig.tight_layout()

    def update(_frame):
        # Read all readily available serial bytes without blocking GUI refresh.
        if connection.in_waiting:
            incoming.extend(connection.read(min(connection.in_waiting, 16384)))

        # Process up to 2500 complete lines per frame; keep partial final line for next update.
        lines_processed = 0
        while b"\n" in incoming and lines_processed < 2500:
            line, _, remainder = incoming.partition(b"\n")
            incoming[:]        = remainder
            lines_processed   += 1
            try:
                t_str, mv_str = line.decode("ascii").strip().split(",")
                t     = int(t_str)  / 1_000_000.0
                volts = int(mv_str) / 1000.0
            except (ValueError, UnicodeDecodeError):
                continue

            if sample_times and t < sample_times[-1]:
                # ESP restarted or its 32-bit micros() counter wrapped.
                sample_times.clear()
                sample_volts.clear()
            sample_times.append(t)
            sample_volts.append(volts)

        if not sample_times:
            return (trace, info)

        # Trim samples outside the view window.
        most_recent    = sample_times[-1]
        threshold_time = most_recent - VIEW_SECONDS
        while len(sample_times) > 1 and sample_times[0] < threshold_time:
            sample_times.popleft()
            sample_volts.popleft()

        t_values = list(sample_times)
        y_values = list(sample_volts)
        trace.set_data([t - most_recent for t in t_values], y_values)

        minimum   = min(y_values)
        maximum   = max(y_values)
        amplitude = maximum - minimum
        frequency = None

        # Rough frequency estimate for repetitive signals with sufficient amplitude.
        if amplitude >= 0.15 and len(y_values) >= 30:
            middle    = (minimum + maximum) / 2
            crossings = [t_values[i] for i in range(1, len(y_values))
                         if y_values[i - 1] <= middle < y_values[i]]
            periods   = [crossings[i] - crossings[i - 1]
                         for i in range(1, len(crossings))]
            if periods:
                period = statistics.median(periods)
                if period > 0:
                    frequency = 1.0 / period

        display = (f"Now: {y_values[-1]:.3f} V    Min: {minimum:.3f} V    "
                   f"Max: {maximum:.3f} V    Vpp: {amplitude:.3f} V")
        if frequency is not None:
            display += f"    Frequency (approx.): {frequency:.1f} Hz"
        info.set_text(display)
        return (trace, info)

    # Keep a reference to the animation for as long as the window is open.
    animation = FuncAnimation(fig, update, interval=40, blit=False,
                              cache_frame_data=False)
    try:
        plt.show()
    finally:
        connection.close()
        del animation


if __name__ == "__main__":
    main()
