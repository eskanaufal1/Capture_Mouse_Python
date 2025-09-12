#!/usr/bin/env python3
"""
HID Device Test - Windows Compatible Version
============================================

This script tests HID device enumeration and communication.
It includes fallback methods for Windows systems.
"""

import sys
import time

def test_hid_with_hidapi():
    """Test HID using the hidapi library"""
    try:
        import hid
        print("✅ HID library imported successfully")
        
        print("🔍 Enumerating HID devices...")
        devices = hid.enumerate()
        print(f"Found {len(devices)} HID devices:")

        for i, d in enumerate(devices[:10]):  # Show first 10 devices
            print(f"  {i+1}. VID: 0x{d['vendor_id']:04X}, PID: 0x{d['product_id']:04X}, "
                  f"Product: {d.get('product_string', 'Unknown')}, "
                  f"Manufacturer: {d.get('manufacturer_string', 'Unknown')}")

        print("\n🎯 Looking for mouse devices...")
        
        # Look for mouse devices
        mouse_devices = []
        for d in devices:
            product_name = d.get('product_string', '').lower()
            manufacturer = d.get('manufacturer_string', '').lower()
            
            # Check if it's likely a mouse
            if ('mouse' in product_name or 'mouse' in manufacturer or 
                (d.get('usage_page') == 1 and d.get('usage') == 2)):  # Generic Desktop, Mouse
                mouse_devices.append(d)
                
        if mouse_devices:
            print(f"Found {len(mouse_devices)} mouse device(s):")
            for i, d in enumerate(mouse_devices):
                print(f"  {i+1}. VID: 0x{d['vendor_id']:04X}, PID: 0x{d['product_id']:04X}, "
                      f"Product: {d.get('product_string', 'Unknown')}")
                      
            # Try to connect to the first mouse
            mouse_device = mouse_devices[0]
            try:
                print(f"\n🔧 Attempting to connect to first mouse device...")
                # Use the correct HID API
                h = hid.Device(mouse_device['vendor_id'], mouse_device['product_id'])
                
                print(f"✅ Successfully connected!")
                print(f"   Manufacturer: {h.manufacturer or 'Unknown'}")
                print(f"   Product: {h.product or 'Unknown'}")
                print(f"   Serial: {h.serial or 'Unknown'}")
                
                print(f"\n📡 Reading mouse data (testing 10 reads)...")
                
                for i in range(10):
                    try:
                        # Read with timeout
                        data = h.read(64, timeout=100)  # 100ms timeout
                        if data:
                            hex_data = ' '.join(f'{b:02X}' for b in data)
                            print(f"📦 Report #{i+1}: {hex_data}")
                            
                            # Basic mouse report parsing
                            if len(data) >= 3:
                                buttons = data[0]
                                delta_x = data[1] if data[1] < 128 else data[1] - 256
                                delta_y = data[2] if data[2] < 128 else data[2] - 256
                                
                                if buttons or delta_x or delta_y:
                                    print(f"   🖱️  Buttons: {buttons:02X}, ΔX: {delta_x:+4d}, ΔY: {delta_y:+4d}")
                        else:
                            print(f"📦 Report #{i+1}: No data (timeout)")
                            
                        time.sleep(0.1)
                        
                    except Exception as e:
                        print(f"❌ Error reading report #{i+1}: {e}")
                        
                h.close()
                print("✅ HID test completed successfully")
                return True
                
            except Exception as e:
                print(f"❌ Failed to connect to mouse device: {e}")
                print("   This may be due to:")
                print("   - Device already in use")
                print("   - Insufficient permissions (try running as Administrator)")
                print("   - Device driver issues")
                return False
                
        else:
            print("❌ No mouse devices found")
            print("   Available device types:")
            
            usage_pages = {}
            for d in devices[:20]:
                up = d.get('usage_page', 0)
                usage = d.get('usage', 0)
                key = f"UP:{up:02X} U:{usage:02X}"
                if key not in usage_pages:
                    usage_pages[key] = []
                usage_pages[key].append(f"VID:0x{d['vendor_id']:04X}")
            
            for up_usage, devices_list in sorted(usage_pages.items()):
                print(f"   {up_usage}: {', '.join(devices_list[:3])}")
            return False
            
    except ImportError as e:
        print(f"❌ HID library not available: {e}")
        print("   Try installing: uv add hidapi")
        return False
    except Exception as e:
        print(f"❌ HID test failed: {e}")
        return False

def test_with_raw_input():
    """Test using the Raw Input system instead"""
    print("\n🔄 Falling back to Raw Input test...")
    try:
        from rawInput import RawInputReader
        
        def test_callback(data):
            if data['type'] == 'mouse_move':
                print(f"🖱️  Raw Input Mouse: Δ({data['delta_x']:+4d}, {data['delta_y']:+4d})")
            elif data['type'] == 'mouse_button':
                print(f"🖱️  Raw Input Button: {data['button']} {data['state']}")
        
        print("✅ Raw Input system available")
        print("📡 Testing Raw Input mouse capture (5 seconds)...")
        
        reader = RawInputReader()
        reader.set_callback(test_callback)
        
        # Run for 5 seconds only
        import threading
        import time
        
        def stop_after_delay():
            time.sleep(5)
            reader.stop()
            
        stop_thread = threading.Thread(target=stop_after_delay)
        stop_thread.daemon = True
        stop_thread.start()
        
        reader.run()
        print("✅ Raw Input test completed")
        return True
        
    except ImportError:
        print("❌ Raw Input system not available")
        return False
    except Exception as e:
        print(f"❌ Raw Input test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 HID Device Test")
    print("==================")
    print()
    
    # Try HID first
    if test_hid_with_hidapi():
        print("\n✅ HID test completed successfully!")
        return
        
    # Fall back to Raw Input
    if test_with_raw_input():
        print("\n✅ Raw Input test completed successfully!")
        return
        
    print("\n❌ All tests failed!")
    print("Possible solutions:")
    print("1. Install HID library: uv add hidapi")
    print("2. Run as Administrator for better device access")
    print("3. Use the Raw Input system (rawInput.py) instead")

if __name__ == "__main__":
    main()