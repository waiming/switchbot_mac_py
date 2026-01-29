import asyncio
from switchbot import GetSwitchbotDevices

async def main():
    """Scan for Switchbot devices."""
    devices = await GetSwitchbotDevices().discover(retry=3, scan_timeout=10)
    
    if not devices:
        print("No Switchbot devices found")
        return
    
    print(f"Found {len(devices)} device(s):\n")
    for mac_address, device_info in devices.items():
        model = device_info.data.get('modelFriendlyName', 'Unknown')
        battery = device_info.data.get('data', {}).get('battery', 'N/A')
        rssi = device_info.rssi
        print(f"Device: {model}")
        print(f"  MAC Address: {mac_address}")
        print(f"  Battery: {battery}%")
        print(f"  Signal (RSSI): {rssi} dBm")
        print()

if __name__ == "__main__":
    asyncio.run(main())