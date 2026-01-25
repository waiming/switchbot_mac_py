import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import config module
sys.path.insert(0, str(Path(__file__).parent.parent))

from switchbot import Switchbot, GetSwitchbotDevices
from config.config import mac, password

async def main():
    """Press the SwitchBot."""
    print("Scanning for SwitchBot devices...")
    
    # Use GetSwitchbotDevices for better discovery
    devices = await GetSwitchbotDevices().discover(retry=5, scan_timeout=15)
    
    if mac not in devices:
        print(f"✗ Device {mac} not found!")
        print(f"\nAvailable devices:")
        for addr, info in devices.items():
            model = info.data.get('modelFriendlyName', 'Unknown')
            print(f"  - {addr} ({model})")
        return
    
    device_info = devices[mac]
    print(f"Found device: {device_info.data.get('modelFriendlyName', 'SwitchBot')}")
    

    for mac_address, device_info in devices.items():
        model = device_info.data.get('modelFriendlyName', 'Unknown')
        battery = device_info.data.get('data', {}).get('battery', 'N/A')
        rssi = device_info.rssi
        print(f"Device: {model}")
        print(f"  MAC Address: {mac_address}")
        print(f"  Battery: {battery}%")
        print(f"  Signal (RSSI): {rssi} dBm")
        print()

    await asyncio.sleep(5)

    # Create a bot instance
    bot = Switchbot(device=device_info.device, password=password)
    
    # Press the button
    print(f"Pressing SwitchBot...")
    result = await bot.press()
    if result:
        print("✓ Successfully pressed the button!")
    else:
        print("✗ Failed to press the button")
    
    await asyncio.sleep(5)

    # Press the button
    print(f"Pressing SwitchBot...")
    result = await bot.press()
    if result:
        print("✓ Successfully pressed the button!")
    else:
        print("✗ Failed to press the button")

    await asyncio.sleep(5)

    # Press the button
    print(f"Pressing SwitchBot...")
    result = await bot.press()
    if result:
        print("✓ Successfully pressed the button!")
    else:
        print("✗ Failed to press the button")

if __name__ == "__main__":
    asyncio.run(main())