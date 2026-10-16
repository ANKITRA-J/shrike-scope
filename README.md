# Shrike-Scope

A laptop-based oscilloscope built with the **Vicharak Shrike-Fi (ESP32-S3)**.

The ESP32-S3 samples an analog signal on GPIO1 and streams timestamped voltage readings over USB serial. A Python application on the laptop plots the live waveform and calculates voltage and frequency measurements in real time.

---

## How it works

```
GPIO1 ──► ESP32-S3 ADC ──► USB Serial (CSV) ──► Python ──► Matplotlib plot
```

- **Firmware** samples GPIO1 every 2 ms (≈500 samples/s), formats each reading as `timestamp_us,voltage_mV`, and sends it over USB serial at 115200 baud.
- **Python app** reads the serial stream, maintains a 3-second sliding window, and updates a live waveform plot every ~40 ms.
- A built-in **10 Hz square-wave generator** on GPIO4 lets you verify the full signal path without any external hardware — just connect GPIO4 to GPIO1 with a jumper wire.

---

## Hardware

| | |
|---|---|
| Board | Vicharak Shrike-Fi (ESP32-S3) |
| Analog input | GPIO1 / ESP_IO1 |
| Test signal output | GPIO4 / ESP_IO4 |
| Connection | USB-C data cable |

**Safe input range:** 0 – ~3.1 V, ground-referenced signals only.  
**Do not connect:** 5 V, negative voltages, mains, motor outputs, or unknown circuits directly to GPIO1.

---

## Quick start

### 1. Flash the firmware

1. Open `ShrikeFi_Oscilloscope.ino` in Arduino IDE.
2. Select your ESP32-S3 board profile and serial port.
3. Under **Tools**, enable **USB CDC On Boot** (required for native USB serial output).
4. Upload the sketch.

### 2. Run the Python display

```bash
python3 -m pip install pyserial matplotlib
python3 oscilloscope.py
```

Select the Shrike-Fi serial port when prompted.

> **Note:** Close Arduino Serial Monitor before running the Python app — both cannot hold the port at the same time.

### 3. Self-test with the built-in square wave

Connect a jumper wire between **GPIO4** and **GPIO1**. The display should show a repeating rectangular waveform at approximately 10 Hz.

---

## Files

| File | Description |
|---|---|
| `ShrikeFi_Oscilloscope.ino` | Arduino firmware for the ESP32-S3 |
| `oscilloscope.py` | Python waveform display application |

---

## Key parameters

| Parameter | Value |
|---|---|
| Sampling rate | ≈500 samples/s (2 ms interval) |
| ADC resolution | 12-bit |
| ADC attenuation | 11 dB (~0.15–3.1 V range) |
| Serial baud rate | 115200 |
| Display window | Last 3 seconds |
| Test signal | 10 Hz square wave on GPIO4 |

---

## Measurements displayed

- Instantaneous, minimum, and maximum voltage
- Peak-to-peak amplitude (Vpp)
- Approximate frequency (for clean repetitive signals ≥ 0.15 V amplitude)

---

## Limitations

- Single channel (GPIO1) only.
- No probe attenuation, buffering, or isolation — learning tool, not a lab instrument.
- Useful bandwidth is well below the 250 Hz Nyquist limit due to sampling jitter.
- ADC accuracy is not independently calibrated.

---

## References

- [Vicharak Shrike hardware overview](https://vicharak-in.github.io/shrike/hardware_overview.html)
- [Vicharak Shrike getting started guide](https://vicharak-in.github.io/shrike/getting_started.html)
- [Vicharak Shrike board pinouts](https://vicharak-in.github.io/shrike/shrike_pinouts.html)

---

*Built as part of the [Vicharak Campus Fellowship](https://github.com/nilangwork17/vicharak-fellowship-tracker).*
