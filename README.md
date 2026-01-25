# switchbot_mac_py



## Installation

```bash
python -m venv venv
source venv/bin/activate && pip install pySwitchbot
```

## Configuration

1. Copy the example configuration file:
   ```bash
   cp config/config_example.py config/config.py
   ```

2. Edit `config/config.py` with your SwitchBot credentials:
   - `mac`: Your SwitchBot device MAC address
   - `password`: 4-digit password set in the SwitchBot app

**Note:** `config/config.py` is gitignored to protect your credentials.
