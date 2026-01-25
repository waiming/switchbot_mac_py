# switchbot_mac_py

A Python utility for controlling SwitchBot devices using [pySwitchbot](https://github.com/Danielhiversen/pySwitchbot) on macOS.

**Tested with:** SwitchBot firmware 6.6

## Installation

```bash
python -m venv venv
source venv/bin/activate && pip install pySwitchbot
```

## Finding Your Device MAC Address

Before configuring, you need to find your SwitchBot device's MAC address. Use the included scanning utility:

```bash
python src/scanning.py
```

This will scan for nearby SwitchBot devices and display:
- Device model name
- MAC address (needed for configuration)
- Battery level
- Signal strength (RSSI)

## Configuration

1. Copy the example configuration file:
   ```bash
   cp config/config_example.py config/config.py
   ```

2. Edit `config/config.py` with your SwitchBot credentials:
   - `mac`: Your SwitchBot device MAC address (found using `scanning.py`)
   - `password`: 4-digit password set in the SwitchBot app

**Note:** `config/config.py` is gitignored to protect your credentials.

## Usage

Once configured, you can control your SwitchBot device. For example, to press the button three times:

```bash
python src/pressing3times.py
```

This script will:
1. Scan and connect to your configured SwitchBot device
2. Display device information (model, battery, signal strength)
3. Press the button three times with 5-second intervals between each press

## Acknowledgments

This project uses [pySwitchbot](https://github.com/Danielhiversen/pySwitchbot), a Python library for controlling SwitchBot devices via Bluetooth.

SwitchBot is a trademark of Wonderlabs, Inc. This project is not affiliated with or endorsed by SwitchBot.

## License

This project is for personal use only. Not intended for commercial use.
