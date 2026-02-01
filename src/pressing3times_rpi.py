import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import config module
sys.path.insert(0, str(Path(__file__).parent.parent))

from bleak import BleakScanner
from bleak_retry_connector import establish_connection, BleakClientWithServiceCache
from config.config import mac, password

# Switchbot UUIDs
SWITCHBOT_SERVICE_UUID = "cba20d00-224d-11e6-9fb8-0002a5d5c51b"
SWITCHBOT_TX_UUID = "cba20002-224d-11e6-9fb8-0002a5d5c51b"  # Write
SWITCHBOT_RX_UUID = "cba20003-224d-11e6-9fb8-0002a5d5c51b"  # Notify

# Connection management settings
DISCONNECT_DELAY = 9.0  # Keep connection alive for 9 seconds after operation


class SwitchbotController:
    """Switchbot controller with persistent connection management."""
    
    def __init__(self, mac_address, password=None):
        self.mac_address = mac_address
        self.password = password
        self._client = None
        self._device = None
        self._disconnect_timer = None
        self._operation_lock = asyncio.Lock()
        self._connect_lock = asyncio.Lock()
        self._notify_future = None
        
    def _notification_handler(self, _sender, data: bytearray):
        """Handle notification responses from device."""
        if self._notify_future and not self._notify_future.done():
            self._notify_future.set_result(data)
    
    def _cancel_disconnect_timer(self):
        """Cancel the disconnect timer."""
        if self._disconnect_timer:
            self._disconnect_timer.cancel()
            self._disconnect_timer = None
    
    def _reset_disconnect_timer(self):
        """Reset disconnect timer to keep connection alive."""
        self._cancel_disconnect_timer()
        loop = asyncio.get_running_loop()
        self._disconnect_timer = loop.call_later(
            DISCONNECT_DELAY, 
            lambda: asyncio.create_task(self._execute_disconnect())
        )
    
    async def _execute_disconnect(self):
        """Disconnect from device after timeout."""
        if self._operation_lock.locked():
            # Operation in progress, reset timer
            self._reset_disconnect_timer()
            return
            
        async with self._connect_lock:
            self._cancel_disconnect_timer()
            if self._client and self._client.is_connected:
                await self._client.disconnect()
            self._client = None
    
    async def _ensure_connected(self):
        """Ensure connection to device is established."""
        if self._client and self._client.is_connected:
            self._reset_disconnect_timer()
            return
        
        async with self._connect_lock:
            # Check again while holding lock
            if self._client and self._client.is_connected:
                self._reset_disconnect_timer()
                return
            
            # Establish connection with retry logic
            self._client = await establish_connection(
                BleakClientWithServiceCache,
                self._device,
                f"Switchbot_{self.mac_address}",
                disconnected_callback=lambda client: None,
                use_services_cache=True,
                ble_device_callback=lambda: self._device,
            )
            
            # Start notifications
            await self._client.start_notify(SWITCHBOT_RX_UUID, self._notification_handler)
            
            # Reset disconnect timer
            self._reset_disconnect_timer()
    
    async def discover_and_connect(self, scan_timeout=15, max_retries=3):
        """Discover device and establish connection with retries."""
        for attempt in range(max_retries):
            if attempt > 0:
                print(f"\n🔄 Retry attempt {attempt + 1}/{max_retries}...")
                print(f"  💡 Press the Switchbot button NOW and keep it close!")
                await asyncio.sleep(2)
            
            print(f"  Scanning for {scan_timeout} seconds...")
            
            # Use detection callback for immediate connection
            found_device = None
            
            def detection_callback(device, adv_data):
                nonlocal found_device
                if device.address.upper() == self.mac_address.upper():
                    if not found_device:  # Only report once
                        print(f"  ✓ Device found!")
                        print(f"    Name: {device.name or 'Unknown'}")
                        print(f"    RSSI: {adv_data.rssi} dBm")
                    found_device = (device, adv_data)
            
            scanner = BleakScanner(detection_callback=detection_callback)
            await scanner.start()
            
            # Wait up to scan_timeout for device to appear
            start_time = asyncio.get_event_loop().time()
            while not found_device and (asyncio.get_event_loop().time() - start_time) < scan_timeout:
                await asyncio.sleep(0.5)
            
            await scanner.stop()
            
            if not found_device:
                if attempt < max_retries - 1:
                    print(f"  ⚠ Device not found, retrying...")
                    continue
                return False
            
            device, adv_data = found_device
            self._device = device
            
            # Connect immediately while device is still active
            print(f"  🔗 Connecting (RSSI: {adv_data.rssi} dBm)...")
            try:
                await self._ensure_connected()
                print(f"  ✓ Connection established!")
                return True
            except Exception as e:
                error_msg = str(e).split(':')[0] if ':' in str(e) else str(e)
                print(f"  ⚠ Connection failed: {error_msg}")
                if attempt < max_retries - 1:
                    print(f"  💡 Retrying... Move device closer if possible")
                    # Keep scanner stopped briefly before retry
                    await asyncio.sleep(1)
        
        return False
    
    async def press(self):
        """Press the Switchbot button with persistent connection."""
        # Build press command
        if self.password:
            import binascii
            password_crc = binascii.crc32(self.password.encode()) & 0xFFFFFFFF
            command = bytearray([0x57, 0x11])
            command.extend(password_crc.to_bytes(4, byteorder='little'))
        else:
            command = bytearray([0x57, 0x01])
        
        # Use operation lock to prevent concurrent operations
        async with self._operation_lock:
            # Ensure we're connected
            await self._ensure_connected()
            
            # Create future for notification response
            loop = asyncio.get_running_loop()
            self._notify_future = loop.create_future()
            
            try:
                # Send command
                await self._client.write_gatt_char(SWITCHBOT_TX_UUID, command)
                
                # Wait for response with timeout
                response = await asyncio.wait_for(self._notify_future, timeout=5.0)
                
                # Check response (expecting byte 1 or 5)
                if response and len(response) > 0 and response[0] in {1, 5}:
                    return True
                return False
                
            except asyncio.TimeoutError:
                print(f"    ⚠ No response from device")
                return False
            except Exception as e:
                print(f"    ⚠ Error: {e}")
                # Force disconnect on error to reset state
                await self._execute_disconnect()
                raise
    
    async def close(self):
        """Close connection and cleanup."""
        self._cancel_disconnect_timer()
        if self._client:
            await self._client.disconnect()


async def main():
    """Press Switchbot 3 times on Raspberry Pi 5 with persistent connection."""
    print("=" * 70)
    print("Switchbot Bot Controller for Raspberry Pi 5")
    print("(Using persistent connection management)")
    print("=" * 70)
    print(f"Target MAC: {mac}")
    print(f"Password: {'Set' if password else 'None'}")
    print()
    
    print("📌 Press the physical button on your Switchbot NOW!")
    print()
    
    # Create controller
    controller = SwitchbotController(mac, password)
    
    # Discover device
    print("🔍 Discovering device...")
    if not await controller.discover_and_connect(scan_timeout=10, max_retries=3):
        print("\n❌ Unable to connect to device")
        print("\nTroubleshooting:")
        print("   1. Move Switchbot within 0.5 meter of Raspberry Pi")
        print("   2. Press and HOLD the button for 2-3 seconds")
        print("   3. Remove obstacles (walls, metal) between devices")
        print("   4. Verify MAC address in config.py")
        return
    
    print()
    print("=" * 70)
    print("Starting 3 button presses...")
    print("(Connection will be kept alive between presses)")
    print("=" * 70)
    
    success_count = 0
    
    try:
        for i in range(3):
            print(f"\n[{i+1}/3] Pressing SwitchBot...")
            try:
                result = await controller.press()
                if result:
                    success_count += 1
                    print(f"  ✅ Press #{i+1} successful!")
                else:
                    print(f"  ❌ Press #{i+1} failed - no valid response")
            except Exception as e:
                error_msg = str(e) if str(e) else type(e).__name__
                print(f"  ❌ Press #{i+1} failed: {error_msg}")
            
            if i < 2:
                print(f"  ⏳ Waiting 8 seconds (connection stays alive)...")
                await asyncio.sleep(8)
        
    finally:
        # Clean up connection
        print("\n🔌 Closing connection...")
        await controller.close()
    
    print(f"\n{'='*70}")
    print(f"Results: {success_count}/3 presses completed")
    print('='*70)
    
    if success_count == 0:
        print("\n❌ No presses succeeded")
    elif success_count < 3:
        print(f"\n⚠ Partial success ({success_count}/3)")
    else:
        print("\n✅ All presses completed successfully!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
