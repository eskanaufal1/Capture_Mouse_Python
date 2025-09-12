#!/usr/bin/env python3
"""
Complete Raw Input Solution
==========================

This version uses proper Windows message handling to capture raw input.
It creates a minimal window and sets up a proper message loop.
"""

import ctypes
import ctypes.wintypes
import sys
import time
import threading
from ctypes import wintypes

# Additional type definitions not in wintypes
LRESULT = ctypes.c_long
HCURSOR = ctypes.c_void_p
WINFUNCTYPE = ctypes.WINFUNCTYPE

# Windows API constants
WM_INPUT = 0x00FF
WM_DESTROY = 0x0002
WM_CLOSE = 0x0010

RIM_TYPEMOUSE = 0
RIM_TYPEKEYBOARD = 1
RIM_TYPEHID = 2

RIDEV_INPUTSINK = 0x00000100
RIDEV_NOLEGACY = 0x00000030

# Mouse button flags
RI_MOUSE_LEFT_BUTTON_DOWN = 0x0001
RI_MOUSE_LEFT_BUTTON_UP = 0x0002
RI_MOUSE_RIGHT_BUTTON_DOWN = 0x0004
RI_MOUSE_RIGHT_BUTTON_UP = 0x0008
RI_MOUSE_MIDDLE_BUTTON_DOWN = 0x0010
RI_MOUSE_MIDDLE_BUTTON_UP = 0x0020
RI_MOUSE_WHEEL = 0x0400

# Define all required structures
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

class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT)
    ]

class WNDCLASSEX(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("style", wintypes.UINT),
        ("lpfnWndProc", WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", HCURSOR),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
        ("hIconSm", wintypes.HICON)
    ]

class CompleteRawInputCapture:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Window management
        self.hwnd = None
        self.running = False
        self.class_name = "RawInputWindow"
        self.window_proc = None
        
        # Statistics
        self.mouse_moves = 0
        self.mouse_clicks = 0
        self.key_presses = 0
        self.total_x = 0
        self.total_y = 0
        
        # Callback
        self.callback = None
        
        # Setup window procedure
        self.setup_window_proc()
        
    def set_callback(self, callback_func):
        """Set callback function for raw input events"""
        self.callback = callback_func
        
    def setup_window_proc(self):
        """Setup the window procedure to handle messages"""
        def window_proc(hwnd, msg, wParam, lParam):
            if msg == WM_INPUT:
                self.handle_raw_input(lParam)
                return 0
            elif msg == WM_CLOSE or msg == WM_DESTROY:
                print("🛑 Window closing...")
                self.running = False
                self.user32.PostQuitMessage(0)
                return 0
            else:
                return self.user32.DefWindowProcW(hwnd, msg, wParam, lParam)
                
        self.window_proc = WINFUNCTYPE(
            LRESULT, 
            wintypes.HWND, 
            wintypes.UINT, 
            wintypes.WPARAM, 
            wintypes.LPARAM
        )(window_proc)
        
    def create_window_class(self):
        """Register a window class for our raw input window"""
        wc = WNDCLASSEX()
        wc.cbSize = ctypes.sizeof(WNDCLASSEX)
        wc.style = 0
        wc.lpfnWndProc = self.window_proc
        wc.cbClsExtra = 0
        wc.cbWndExtra = 0
        wc.hInstance = self.kernel32.GetModuleHandleW(None)
        wc.hIcon = None
        wc.hCursor = self.user32.LoadCursorW(None, 32512)  # IDC_ARROW
        wc.hbrBackground = ctypes.c_void_p(6)  # COLOR_WINDOW + 1
        wc.lpszMenuName = None
        wc.lpszClassName = self.class_name
        wc.hIconSm = None
        
        atom = self.user32.RegisterClassExW(ctypes.byref(wc))
        if not atom:
            error = ctypes.get_last_error()
            print(f"❌ Failed to register window class. Error: {error}")
            return False
            
        print("✅ Window class registered successfully")
        return True
        
    def create_window(self):
        """Create the window for receiving raw input"""
        if not self.create_window_class():
            return False
            
        # Create window
        self.hwnd = self.user32.CreateWindowExW(
            0,                          # Extended style
            self.class_name,            # Class name
            "Raw Input Capture",        # Window title
            0x00CF0000,                 # WS_OVERLAPPEDWINDOW
            100, 100, 500, 400,         # Position and size
            None,                       # Parent window
            None,                       # Menu
            self.kernel32.GetModuleHandleW(None),  # Instance
            None                        # Additional data
        )
        
        if not self.hwnd:
            error = ctypes.get_last_error()
            print(f"❌ Failed to create window. Error: {error}")
            return False
            
        print(f"✅ Window created with handle: 0x{self.hwnd:08X}")
        
        # Show window
        self.user32.ShowWindow(self.hwnd, 1)  # SW_SHOWNORMAL
        self.user32.UpdateWindow(self.hwnd)
        
        return True
        
    def register_raw_input(self):
        """Register for raw input devices"""
        print("🔧 Registering raw input devices...")
        
        # Mouse
        mouse_device = RAWINPUTDEVICE()
        mouse_device.usUsagePage = 0x01  # Generic Desktop
        mouse_device.usUsage = 0x02      # Mouse
        mouse_device.dwFlags = RIDEV_INPUTSINK
        mouse_device.hwndTarget = self.hwnd
        
        # Keyboard
        keyboard_device = RAWINPUTDEVICE()
        keyboard_device.usUsagePage = 0x01  # Generic Desktop
        keyboard_device.usUsage = 0x06      # Keyboard
        keyboard_device.dwFlags = RIDEV_INPUTSINK
        keyboard_device.hwndTarget = self.hwnd
        
        # Register both devices
        devices = (RAWINPUTDEVICE * 2)(mouse_device, keyboard_device)
        result = self.user32.RegisterRawInputDevices(
            devices, 2, ctypes.sizeof(RAWINPUTDEVICE)
        )
        
        if result:
            print("✅ Successfully registered mouse and keyboard for raw input")
            return True
        else:
            error = ctypes.get_last_error()
            print(f"❌ Failed to register devices. Error: {error}")
            return False
            
    def handle_raw_input(self, lParam):
        """Handle raw input message"""
        try:
            # Get the size of raw input data
            size = wintypes.UINT()
            self.user32.GetRawInputData(
                lParam, 
                0x10000003,  # RID_INPUT
                None, 
                ctypes.byref(size), 
                ctypes.sizeof(RAWINPUTHEADER)
            )
            
            # Get the actual data
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
                self.handle_mouse_input(raw_input.data.mouse)
            elif raw_input.header.dwType == RIM_TYPEKEYBOARD:
                self.handle_keyboard_input(raw_input.data.keyboard)
                
        except Exception as e:
            print(f"❌ Error handling raw input: {e}")
            
    def handle_mouse_input(self, mouse_data):
        """Handle raw mouse input"""
        if mouse_data.lLastX != 0 or mouse_data.lLastY != 0:
            self.mouse_moves += 1
            self.total_x += mouse_data.lLastX
            self.total_y += mouse_data.lLastY
            
            data = {
                'type': 'mouse_move',
                'delta_x': mouse_data.lLastX,
                'delta_y': mouse_data.lLastY,
                'total_x': self.total_x,
                'total_y': self.total_y,
                'move_count': self.mouse_moves,
                'timestamp': time.time()
            }
            
            if self.callback:
                self.callback(data)
            else:
                print(f"🖱️  Mouse: Δ({mouse_data.lLastX:+4d}, {mouse_data.lLastY:+4d}) → Total({self.total_x:6d}, {self.total_y:6d}) [Move #{self.mouse_moves}]")
                
        if mouse_data.usButtonFlags:
            self.mouse_clicks += 1
            button_info = self.decode_mouse_button(mouse_data.usButtonFlags, mouse_data.usButtonData)
            
            data = {
                'type': 'mouse_button',
                'button': button_info['button'],
                'action': button_info['action'],
                'data': button_info.get('data', 0),
                'click_count': self.mouse_clicks,
                'timestamp': time.time()
            }
            
            if self.callback:
                self.callback(data)
            else:
                if button_info['button'] == 'wheel':
                    print(f"🖱️  Mouse: {button_info['button'].title()} {button_info['action']} (Δ{button_info['data']}) [Click #{self.mouse_clicks}]")
                else:
                    print(f"🖱️  Mouse: {button_info['button'].title()} {button_info['action']} [Click #{self.mouse_clicks}]")
                    
    def decode_mouse_button(self, button_flags, button_data):
        """Decode mouse button information"""
        if button_flags & RI_MOUSE_LEFT_BUTTON_DOWN:
            return {'button': 'left', 'action': 'down'}
        elif button_flags & RI_MOUSE_LEFT_BUTTON_UP:
            return {'button': 'left', 'action': 'up'}
        elif button_flags & RI_MOUSE_RIGHT_BUTTON_DOWN:
            return {'button': 'right', 'action': 'down'}
        elif button_flags & RI_MOUSE_RIGHT_BUTTON_UP:
            return {'button': 'right', 'action': 'up'}
        elif button_flags & RI_MOUSE_MIDDLE_BUTTON_DOWN:
            return {'button': 'middle', 'action': 'down'}
        elif button_flags & RI_MOUSE_MIDDLE_BUTTON_UP:
            return {'button': 'middle', 'action': 'up'}
        elif button_flags & RI_MOUSE_WHEEL:
            delta = ctypes.c_short(button_data).value
            direction = "up" if delta > 0 else "down"
            return {'button': 'wheel', 'action': direction, 'data': delta}
        else:
            return {'button': 'unknown', 'action': 'unknown'}
            
    def handle_keyboard_input(self, keyboard_data):
        """Handle raw keyboard input"""
        self.key_presses += 1
        key_state = "down" if not (keyboard_data.Flags & 0x01) else "up"
        
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
        else:
            key_name = self.get_key_name(keyboard_data.VKey)
            print(f"⌨️  Keyboard: {key_name} {key_state} (Scan: {keyboard_data.MakeCode}) [Key #{self.key_presses}]")
            
    def get_key_name(self, vkey):
        """Get a readable name for a virtual key code"""
        key_names = {
            0x08: "Backspace", 0x09: "Tab", 0x0D: "Enter", 0x10: "Shift",
            0x11: "Ctrl", 0x12: "Alt", 0x1B: "Escape", 0x20: "Space",
            0x25: "Left", 0x26: "Up", 0x27: "Right", 0x28: "Down",
            0x2E: "Delete", 0x70: "F1", 0x71: "F2", 0x72: "F3", 0x73: "F4"
        }
        
        if vkey in key_names:
            return key_names[vkey]
        elif 0x30 <= vkey <= 0x39:  # Numbers 0-9
            return chr(vkey)
        elif 0x41 <= vkey <= 0x5A:  # Letters A-Z
            return chr(vkey)
        else:
            return f"VK_{vkey:02X}"
            
    def run_message_loop(self):
        """Run the Windows message loop"""
        print("🎯 Starting message loop...")
        print("   Move mouse or press keys to see raw input")
        print("   Close the window to stop")
        
        msg = MSG()
        self.running = True
        
        while self.running:
            bRet = self.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            
            if bRet == 0:  # WM_QUIT
                break
            elif bRet == -1:  # Error
                error = ctypes.get_last_error()
                print(f"❌ GetMessage error: {error}")
                break
            else:
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
                
        print("👋 Message loop ended")
        
    def run(self):
        """Main run method"""
        print("🚀 Complete Raw Input Capture")
        print("   Using proper Windows message handling")
        print()
        
        try:
            # Create window
            if not self.create_window():
                return False
                
            # Register for raw input
            if not self.register_raw_input():
                print("⚠️  Registration failed, but continuing anyway...")
                
            # Run message loop
            self.run_message_loop()
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources"""
        if self.hwnd:
            self.user32.DestroyWindow(self.hwnd)
        print("🧹 Cleanup completed")

def main():
    """Main function"""
    capture = CompleteRawInputCapture()
    capture.run()

if __name__ == "__main__":
    main()