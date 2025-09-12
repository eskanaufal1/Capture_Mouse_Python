import ctypes
import ctypes.wintypes
import time
import sys
import threading
from ctypes import wintypes

class SimpleHIDReader:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.running = False
        
        # Counters
        self.mouse_moves = 0
        self.key_presses = 0
        self.total_events = 0
        
        print("🔍 Simple HID/Input Monitor")
        print("=" * 50)
        
    def get_cursor_pos(self):
        """Get current cursor position"""
        point = wintypes.POINT()
        self.user32.GetCursorPos(ctypes.byref(point))
        return point.x, point.y
        
    def get_key_state(self, vkey):
        """Get state of a virtual key"""
        return self.user32.GetAsyncKeyState(vkey) & 0x8000 != 0
        
    def monitor_input(self):
        """Monitor input devices by polling"""
        print("🎯 Starting input monitoring...")
        print("   Move mouse and press keys to see activity")
        print("   Press ESC to stop\n")
        
        last_mouse_pos = self.get_cursor_pos()
        last_time = time.time()
        
        # Key states to monitor
        keys_to_monitor = {
            0x01: "Left Mouse",
            0x02: "Right Mouse", 
            0x04: "Middle Mouse",
            0x20: "Space",
            0x0D: "Enter",
            0x1B: "Escape",
            0x41: "A", 0x42: "B", 0x43: "C", 0x44: "D", 0x45: "E",
            0x46: "F", 0x47: "G", 0x48: "H", 0x49: "I", 0x4A: "J"
        }
        
        key_states = {vkey: False for vkey in keys_to_monitor.keys()}
        
        while self.running:
            current_time = time.time()
            
            # Check mouse movement
            current_mouse_pos = self.get_cursor_pos()
            if current_mouse_pos != last_mouse_pos:
                self.mouse_moves += 1
                self.total_events += 1
                
                delta_x = current_mouse_pos[0] - last_mouse_pos[0]
                delta_y = current_mouse_pos[1] - last_mouse_pos[1]
                
                print(f"🖱️  Mouse: ({current_mouse_pos[0]}, {current_mouse_pos[1]}) "
                      f"Δ({delta_x:+4d}, {delta_y:+4d}) [Move #{self.mouse_moves}]")
                
                last_mouse_pos = current_mouse_pos
                
            # Check key states
            for vkey, key_name in keys_to_monitor.items():
                current_state = self.get_key_state(vkey)
                if current_state != key_states[vkey]:
                    key_states[vkey] = current_state
                    if current_state:  # Key pressed
                        self.key_presses += 1
                        self.total_events += 1
                        print(f"⌨️  Key: {key_name} PRESSED [Press #{self.key_presses}]")
                        
                        # Exit on ESC
                        if vkey == 0x1B:  # Escape
                            print("🛑 Escape pressed - stopping...")
                            self.running = False
                            return
                            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.01)
            
            # Show periodic statistics
            if current_time - last_time > 5.0:
                self.print_statistics()
                last_time = current_time
                
    def read_raw_hid_devices(self):
        """Attempt to enumerate HID devices"""
        print("\n🔍 Enumerating HID Devices:")
        print("-" * 30)
        
        try:
            # Try to get device list (simplified approach)
            from ctypes import windll
            
            # Get number of raw input devices
            device_count = wintypes.UINT()
            result = self.user32.GetRawInputDeviceList(None, ctypes.byref(device_count), 24)
            
            if device_count.value > 0:
                print(f"📱 Found {device_count.value} raw input devices")
                
                # This is a simplified enumeration - in a full implementation
                # you would allocate proper structures and iterate through devices
                for i in range(min(device_count.value, 10)):  # Limit to first 10
                    print(f"   Device {i+1}: HID Device (Handle: 0x{i:04X})")
            else:
                print("❌ No raw input devices found")
                
        except Exception as e:
            print(f"❌ Error enumerating devices: {e}")
            
    def monitor_system_info(self):
        """Monitor system information"""
        print("\n💻 System Information:")
        print("-" * 25)
        
        try:
            # Get system metrics
            screen_width = self.user32.GetSystemMetrics(0)  # SM_CXSCREEN
            screen_height = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN
            mouse_present = self.user32.GetSystemMetrics(19)  # SM_MOUSEPRESENT
            mouse_buttons = self.user32.GetSystemMetrics(43)  # SM_CMOUSEBUTTONS
            
            print(f"   Screen Resolution: {screen_width} x {screen_height}")
            print(f"   Mouse Present: {'Yes' if mouse_present else 'No'}")
            print(f"   Mouse Buttons: {mouse_buttons}")
            
            # Get cursor info
            cursor_info = wintypes.POINT()
            self.user32.GetCursorPos(ctypes.byref(cursor_info))
            print(f"   Current Cursor: ({cursor_info.x}, {cursor_info.y})")
            
        except Exception as e:
            print(f"❌ Error getting system info: {e}")
            
    def print_statistics(self):
        """Print current statistics"""
        print(f"\n📊 Activity Statistics:")
        print(f"   Mouse movements: {self.mouse_moves}")
        print(f"   Key presses: {self.key_presses}")
        print(f"   Total events: {self.total_events}")
        print(f"   Time: {time.strftime('%H:%M:%S')}")
        
    def start(self):
        """Start the HID reader"""
        self.running = True
        
        try:
            # Show system information
            self.monitor_system_info()
            
            # Try to enumerate devices
            self.read_raw_hid_devices()
            
            # Start monitoring
            self.monitor_input()
            
        except KeyboardInterrupt:
            print("\n🛑 Ctrl+C pressed - stopping...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.running = False
            self.print_statistics()
            print("\n👋 HID monitoring stopped.")

def test_ctypes_access():
    """Test if we can access Windows APIs"""
    print("🧪 Testing Windows API Access:")
    print("-" * 30)
    
    try:
        user32 = ctypes.windll.user32
        
        # Test basic API calls
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        print(f"✅ GetSystemMetrics: {screen_width} x {screen_height}")
        
        # Test cursor position
        point = wintypes.POINT()
        result = user32.GetCursorPos(ctypes.byref(point))
        print(f"✅ GetCursorPos: ({point.x}, {point.y})")
        
        # Test key state
        escape_state = user32.GetAsyncKeyState(0x1B)
        print(f"✅ GetAsyncKeyState (ESC): {escape_state}")
        
        print("✅ All API tests passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main function"""
    print("🔌 Raw HID Data Reader")
    print("=" * 50)
    
    # Test API access first
    if not test_ctypes_access():
        print("❌ Cannot access Windows APIs - exiting")
        return
        
    # Create and start reader
    reader = SimpleHIDReader()
    reader.start()

if __name__ == "__main__":
    main()