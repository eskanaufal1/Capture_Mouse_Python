import ctypes
import ctypes.wintypes
import struct
import sys
import threading
import time
from ctypes import wintypes

# Windows API constants
WM_INPUT = 0x00FF
RIM_TYPEMOUSE = 0
RIM_TYPEKEYBOARD = 1
RIM_TYPEHID = 2

RIDEV_INPUTSINK = 0x00000100
RIDEV_NOLEGACY = 0x00000030

# Raw input device info flags
RIDI_PREPARSEDDATA = 0x20000005
RIDI_DEVICENAME = 0x20000007
RIDI_DEVICEINFO = 0x2000000b

# Mouse button flags
RI_MOUSE_LEFT_BUTTON_DOWN = 0x0001
RI_MOUSE_LEFT_BUTTON_UP = 0x0002
RI_MOUSE_RIGHT_BUTTON_DOWN = 0x0004
RI_MOUSE_RIGHT_BUTTON_UP = 0x0008
RI_MOUSE_MIDDLE_BUTTON_DOWN = 0x0010
RI_MOUSE_MIDDLE_BUTTON_UP = 0x0020
RI_MOUSE_WHEEL = 0x0400

# Define structures
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [
        ("usUsagePage", wintypes.USHORT),
        ("usUsage", wintypes.USHORT),
        ("dwFlags", wintypes.DWORD),
        ("hwndTarget", wintypes.HWND)
    ]

class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [
        ("dwType", wintypes.DWORD),
        ("dwSize", wintypes.DWORD),
        ("hDevice", wintypes.HANDLE),
        ("wParam", wintypes.WPARAM)
    ]

class RAWMOUSE(ctypes.Structure):
    _fields_ = [
        ("usFlags", wintypes.USHORT),
        ("usButtonFlags", wintypes.USHORT),
        ("usButtonData", wintypes.USHORT),
        ("ulRawButtons", wintypes.ULONG),
        ("lLastX", wintypes.LONG),
        ("lLastY", wintypes.LONG),
        ("ulExtraInformation", wintypes.ULONG)
    ]

class RAWKEYBOARD(ctypes.Structure):
    _fields_ = [
        ("MakeCode", wintypes.USHORT),
        ("Flags", wintypes.USHORT),
        ("Reserved", wintypes.USHORT),
        ("VKey", wintypes.USHORT),
        ("Message", wintypes.UINT),
        ("ExtraInformation", wintypes.ULONG)
    ]

class RAWHID(ctypes.Structure):
    _fields_ = [
        ("dwSizeHid", wintypes.DWORD),
        ("dwCount", wintypes.DWORD),
        ("bRawData", ctypes.c_byte * 1)
    ]

class RAWINPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mouse", RAWMOUSE),
        ("keyboard", RAWKEYBOARD),
        ("hid", RAWHID)
    ]

class RAWINPUT(ctypes.Structure):
    _fields_ = [
        ("header", RAWINPUTHEADER),
        ("data", RAWINPUT_UNION)
    ]

class RawInputReader:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.running = False
        self.callback = None
        
        # Mouse tracking
        self.total_mouse_x = 0
        self.total_mouse_y = 0
        self.mouse_clicks = 0
        self.mouse_wheel_delta = 0
        
        # Keyboard tracking
        self.key_presses = 0
        self.last_key = None
        
        # HID device tracking
        self.hid_data_count = 0
        
    def set_callback(self, callback_func):
        """Set callback function to handle raw input data"""
        self.callback = callback_func
        
    def register_devices(self):
        """Register for raw input from mouse, keyboard, and HID devices"""
        devices = (RAWINPUTDEVICE * 2)()
        
        # Mouse
        devices[0].usUsagePage = 0x01  # Generic Desktop
        devices[0].usUsage = 0x02      # Mouse
        devices[0].dwFlags = RIDEV_INPUTSINK
        devices[0].hwndTarget = None
        
        # Keyboard  
        devices[1].usUsagePage = 0x01  # Generic Desktop
        devices[1].usUsage = 0x06      # Keyboard
        devices[1].dwFlags = RIDEV_INPUTSINK
        devices[1].hwndTarget = None
        
        result = self.user32.RegisterRawInputDevices(devices, 2, ctypes.sizeof(RAWINPUTDEVICE))
        if not result:
            error_code = ctypes.get_last_error()
            print(f"⚠️  Warning: Failed to register raw input devices. Error: {error_code}")
            print("   Trying simplified registration...")
            
            # Try with simplified approach - just mouse
            simple_device = RAWINPUTDEVICE()
            simple_device.usUsagePage = 0x01
            simple_device.usUsage = 0x02
            simple_device.dwFlags = 0x00000100  # RIDEV_INPUTSINK
            simple_device.hwndTarget = None
            
            result = self.user32.RegisterRawInputDevices(
                ctypes.byref(simple_device), 1, ctypes.sizeof(RAWINPUTDEVICE)
            )
            
            if not result:
                error_code = ctypes.get_last_error()
                print(f"❌ Failed simplified registration. Error: {error_code}")
                print("   Will continue with Windows message monitoring...")
            else:
                print("✅ Successfully registered for mouse raw input")
        else:
            print("✅ Successfully registered for raw input from:")
            print("   - Mouse devices")
            print("   - Keyboard devices")
        
    def process_raw_input(self, lParam):
        """Process raw input message"""
        # Get the size of raw input data
        size = wintypes.UINT()
        self.user32.GetRawInputData(
            lParam, 
            0x10000003,  # RID_INPUT
            None, 
            ctypes.byref(size), 
            ctypes.sizeof(RAWINPUTHEADER)
        )
        
        # Allocate buffer and get the data
        buffer = ctypes.create_string_buffer(size.value)
        result = self.user32.GetRawInputData(
            lParam,
            0x10000003,  # RID_INPUT
            buffer,
            ctypes.byref(size),
            ctypes.sizeof(RAWINPUTHEADER)
        )
        
        if result != size.value:
            return
            
        # Parse the raw input
        raw_input = ctypes.cast(buffer, ctypes.POINTER(RAWINPUT)).contents
        
        if raw_input.header.dwType == RIM_TYPEMOUSE:
            self.process_mouse_data(raw_input.data.mouse)
        elif raw_input.header.dwType == RIM_TYPEKEYBOARD:
            self.process_keyboard_data(raw_input.data.keyboard)
        elif raw_input.header.dwType == RIM_TYPEHID:
            self.process_hid_data(raw_input.data.hid, raw_input.header.hDevice)
            
    def process_mouse_data(self, mouse_data):
        """Process raw mouse input data"""
        # Mouse movement
        if mouse_data.lLastX != 0 or mouse_data.lLastY != 0:
            self.total_mouse_x += mouse_data.lLastX
            self.total_mouse_y += mouse_data.lLastY
            
            data = {
                'type': 'mouse_move',
                'delta_x': mouse_data.lLastX,
                'delta_y': mouse_data.lLastY,
                'total_x': self.total_mouse_x,
                'total_y': self.total_mouse_y,
                'flags': mouse_data.usFlags,
                'timestamp': time.time()
            }
            
            if self.callback:
                self.callback(data)
                
        # Mouse buttons
        button_flags = mouse_data.usButtonFlags
        if button_flags:
            self.mouse_clicks += 1
            button_name = "Unknown"
            button_state = "Unknown"
            
            if button_flags & RI_MOUSE_LEFT_BUTTON_DOWN:
                button_name, button_state = "Left", "Down"
            elif button_flags & RI_MOUSE_LEFT_BUTTON_UP:
                button_name, button_state = "Left", "Up"
            elif button_flags & RI_MOUSE_RIGHT_BUTTON_DOWN:
                button_name, button_state = "Right", "Down"
            elif button_flags & RI_MOUSE_RIGHT_BUTTON_UP:
                button_name, button_state = "Right", "Up"
            elif button_flags & RI_MOUSE_MIDDLE_BUTTON_DOWN:
                button_name, button_state = "Middle", "Down"
            elif button_flags & RI_MOUSE_MIDDLE_BUTTON_UP:
                button_name, button_state = "Middle", "Up"
            elif button_flags & RI_MOUSE_WHEEL:
                wheel_delta = ctypes.c_short(mouse_data.usButtonData).value
                self.mouse_wheel_delta += wheel_delta
                data = {
                    'type': 'mouse_wheel',
                    'delta': wheel_delta,
                    'total_delta': self.mouse_wheel_delta,
                    'timestamp': time.time()
                }
                if self.callback:
                    self.callback(data)
                return
                
            data = {
                'type': 'mouse_button',
                'button': button_name,
                'state': button_state,
                'click_count': self.mouse_clicks,
                'timestamp': time.time()
            }
            
            if self.callback:
                self.callback(data)
                
    def process_keyboard_data(self, keyboard_data):
        """Process raw keyboard input data"""
        self.key_presses += 1
        self.last_key = keyboard_data.VKey
        
        key_state = "Down" if not (keyboard_data.Flags & 0x01) else "Up"
        
        data = {
            'type': 'keyboard',
            'vkey': keyboard_data.VKey,
            'scan_code': keyboard_data.MakeCode,
            'flags': keyboard_data.Flags,
            'state': key_state,
            'key_count': self.key_presses,
            'timestamp': time.time()
        }
        
        if self.callback:
            self.callback(data)
            
    def process_hid_data(self, hid_data, device_handle):
        """Process raw HID device data"""
        self.hid_data_count += 1
        
        # Extract raw bytes
        raw_bytes = []
        for i in range(min(hid_data.dwSizeHid * hid_data.dwCount, 64)):  # Limit to prevent overflow
            raw_bytes.append(hid_data.bRawData[i])
            
        data = {
            'type': 'hid',
            'device_handle': device_handle,
            'size': hid_data.dwSizeHid,
            'count': hid_data.dwCount,
            'raw_bytes': raw_bytes,
            'hex_data': ' '.join(f'{b:02X}' for b in raw_bytes),
            'data_count': self.hid_data_count,
            'timestamp': time.time()
        }
        
        if self.callback:
            self.callback(data)
            
    def get_device_name(self, device_handle):
        """Get the name of a HID device"""
        try:
            size = wintypes.UINT()
            self.user32.GetRawInputDeviceInfoW(
                device_handle,
                RIDI_DEVICENAME,
                None,
                ctypes.byref(size)
            )
            
            if size.value > 0:
                buffer = ctypes.create_unicode_buffer(size.value)
                self.user32.GetRawInputDeviceInfoW(
                    device_handle,
                    RIDI_DEVICENAME,
                    buffer,
                    ctypes.byref(size)
                )
                return buffer.value
        except:
            pass
        return "Unknown Device"
        
    def print_statistics(self):
        """Print current statistics"""
        print(f"\n📊 Raw Input Statistics:")
        print(f"   Mouse: Total movement X={self.total_mouse_x}, Y={self.total_mouse_y}")
        print(f"   Mouse: Clicks={self.mouse_clicks}, Wheel={self.mouse_wheel_delta}")
        print(f"   Keyboard: Key presses={self.key_presses}, Last key={self.last_key}")
        print(f"   HID: Data packets={self.hid_data_count}")
        
    def start_message_loop(self):
        """Start the Windows message loop to capture raw input"""
        self.running = True
        print("🎯 Starting raw input capture...")
        print("   Move mouse, press keys, or use other HID devices")
        print("   Press Ctrl+C to stop")
        print("   Note: This monitors low-level Windows messages\n")
        
        # Alternative: Hook into low-level mouse proc if raw input fails
        def low_level_mouse_proc(nCode, wParam, lParam):
            if nCode >= 0:
                if wParam == 0x0200:  # WM_MOUSEMOVE
                    # Simulate mouse movement data
                    data = {
                        'type': 'mouse_move',
                        'delta_x': 1,  # Can't get actual delta easily
                        'delta_y': 0,
                        'total_x': self.total_mouse_x,
                        'total_y': self.total_mouse_y,
                        'flags': 0,
                        'timestamp': time.time()
                    }
                    if self.callback:
                        self.callback(data)
            return self.user32.CallNextHookExW(None, nCode, wParam, lParam)
        
        # Message loop
        msg = wintypes.MSG()
        message_count = 0
        
        while self.running:
            result = self.user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1)  # PM_REMOVE
            if result:
                message_count += 1
                if msg.message == WM_INPUT:
                    self.process_raw_input(msg.lParam)
                elif msg.message == 0x0012:  # WM_QUIT
                    break
                    
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
            else:
                time.sleep(0.001)  # Small delay to prevent CPU spinning
                
            # Show periodic activity
            if message_count % 1000 == 0 and message_count > 0:
                print(f"📨 Processed {message_count} messages...")
                
    def stop(self):
        """Stop the raw input capture"""
        self.running = False
        self.user32.PostQuitMessage(0)

def default_callback(data):
    """Default callback function to display raw input data"""
    if data['type'] == 'mouse_move':
        print(f"🖱️  Mouse: Δ({data['delta_x']:+4d}, {data['delta_y']:+4d}) → Total({data['total_x']:6d}, {data['total_y']:6d})")
    elif data['type'] == 'mouse_button':
        print(f"🖱️  Mouse: {data['button']} {data['state']} (Click #{data['click_count']})")
    elif data['type'] == 'mouse_wheel':
        print(f"🖱️  Mouse: Wheel Δ{data['delta']:+4d} → Total{data['total_delta']:+6d}")
    elif data['type'] == 'keyboard':
        key_name = f"VK_{data['vkey']:02X}" if data['vkey'] < 256 else "Unknown"
        print(f"⌨️  Keyboard: {key_name} {data['state']} (Scan: {data['scan_code']}, Press #{data['key_count']})")
    elif data['type'] == 'hid':
        device_name = "HID Device"
        if len(data['raw_bytes']) > 0:
            print(f"🎮 HID: {device_name} → Size:{data['size']}, Count:{data['count']}")
            print(f"    Raw: {data['hex_data'][:50]}{'...' if len(data['hex_data']) > 50 else ''}")

def main():
    """Main function to run the raw input reader"""
    reader = RawInputReader()
    
    try:
        # Set up callback
        reader.set_callback(default_callback)
        
        # Register for raw input
        reader.register_devices()
        
        # Start statistics thread
        def stats_worker():
            while reader.running:
                time.sleep(5)
                if reader.running:
                    reader.print_statistics()
                    
        stats_thread = threading.Thread(target=stats_worker, daemon=True)
        stats_thread.start()
        
        # Start message loop
        reader.start_message_loop()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping raw input capture...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        reader.stop()
        reader.print_statistics()
        print("👋 Raw input capture stopped.")

if __name__ == "__main__":
    main()
