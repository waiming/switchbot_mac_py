import asyncio
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