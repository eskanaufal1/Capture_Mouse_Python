# Advanced Mouse Tracker with Raw Input Integration

## Project Overview

This project contains multiple mouse tracking applications that demonstrate different levels of input capture precision and visual effects. The latest addition integrates raw Windows input algorithms for maximum precision.

## File Structure

```
Capture_Mouse_Python/
├── main.py                              # Original simple mouse tracker
├── modern_mouse_tracker_pl_animation.py # Full-featured GUI tracker
├── rawInput.py                         # Raw Windows input capture system
├── simple_hid_reader.py               # Simplified polling-based input reader
├── advanced_mouse_tracker.py          # NEW: Enhanced tracker with raw input
├── demo_advanced_tracker.py           # Demo and comparison script
├── pyproject.toml                      # Project dependencies
├── uv.lock                            # Lock file
└── README.md                          # This file
```

## Applications Comparison

| Feature        | Original     | Modern         | **Advanced**          |
| -------------- | ------------ | -------------- | --------------------- |
| Input Method   | Basic events | Tkinter events | **Raw Windows API**   |
| Precision      | Low          | Standard       | **High-precision**    |
| History Points | None         | 300            | **5000**              |
| Frame Rate     | N/A          | 30 FPS         | **60 FPS**            |
| Velocity Info  | No           | No             | **Yes**               |
| Raw Deltas     | No           | No             | **Yes**               |
| Statistics     | No           | Basic          | **Comprehensive**     |
| Threading      | No           | No             | **Yes**               |
| Plinko Effects | No           | Basic          | **Velocity-enhanced** |

## Advanced Mouse Tracker Features

### 🔧 Technical Enhancements

- **Raw Windows Input API** integration via `rawInput.py`
- **High-precision** mouse movement capture
- **Real-time velocity** and direction calculations
- **Enhanced plinko collision** system with velocity effects
- **Advanced statistics** tracking and display
- **60 FPS rendering** for smoother animations

### 📊 Data Capture

- **Raw delta movements** (precise pixel-level changes)
- **Movement velocity** and direction vectors
- **Click counting** with button identification
- **Mouse wheel** delta tracking
- **Movement statistics** (total distance, average velocity)

### 🎨 Visual Enhancements

- **Velocity-based color changes** in pointer and trails
- **Dynamic trail radius** based on movement speed
- **Enhanced plinko bounce effects** with velocity scaling
- **Real-time coordinate display** with raw input data
- **Multi-ring click effects** with button-specific colors

### ⌨️ Enhanced Controls

- **V** - Toggle velocity information display
- **R** - Toggle raw delta movement display
- **O** - Toggle coordinate information
- All original shortcuts still available

## Quick Start

### Prerequisites

```bash
# Install UV package manager (if not installed)
pip install uv

# Install project dependencies
uv sync
```

### Running the Applications

#### 1. Advanced Mouse Tracker (Recommended)

```bash
uv run advanced_mouse_tracker.py
```

**Features:**

- Raw input precision
- Velocity-based effects
- Comprehensive statistics
- All visual enhancements

#### 2. Demo and Comparison

```bash
uv run demo_advanced_tracker.py
```

**Features:**

- Feature comparison table
- Detailed technical information
- Interactive demo launcher

#### 3. Modern Tracker (Original Enhanced)

```bash
uv run modern_mouse_tracker_pl_animation.py
```

**Features:**

- Standard precision
- Full GUI with toggles
- Plinko animation system

#### 4. Raw Input Reader (Standalone)

```bash
uv run simple_hid_reader.py
```

**Features:**

- Console-based input monitoring
- System information display
- High-frequency polling

## Keyboard Shortcuts

### Universal Shortcuts (All Trackers)

- **ESC** - Exit application
- **F/F11** - Toggle fullscreen
- **C** - Clear/Reset history
- **L** - Toggle line history
- **T** - Toggle trail animation
- **G** - Toggle grow animation
- **P** - Toggle plinko animation
- **O** - Toggle coordinates display

### Advanced Tracker Only

- **V** - Toggle velocity information
- **R** - Toggle raw delta display

## Technical Implementation

### Raw Input Integration

The advanced tracker integrates with `rawInput.py` using:

```python
from rawInput import RawInputReader
import queue
import threading

# Threaded raw input processing
self.raw_input_reader = RawInputReader()
self.input_queue = queue.Queue()

# Enhanced data processing
def handle_raw_mouse_movement(self, data):
    self.raw_delta_x = data['delta_x']
    self.raw_delta_y = data['delta_y']
    velocity = math.sqrt(self.raw_delta_x**2 + self.raw_delta_y**2)
    # ... enhanced processing
```

### Performance Optimizations

- **Numpy arrays** for efficient history storage
- **Queue-based threading** for non-blocking input
- **Optimized rendering** pipeline at 60 FPS
- **Collision detection** using vectorized operations

### Fallback Mechanisms

- Raw input device registration with error handling
- Simplified registration fallback
- Message loop monitoring as final fallback
- Cross-platform compatibility considerations

## Use Cases

### Advanced Tracker

- **Gaming input analysis** - Precise movement tracking
- **Performance testing** - High-frequency input capture
- **Research applications** - Detailed movement statistics
- **Accessibility tools** - Enhanced input monitoring

### Modern Tracker

- **Educational demos** - Visual mouse tracking concepts
- **Presentation tools** - Interactive mouse visualization
- **Entertainment** - Plinko collision games

### Raw Input Reader

- **System diagnostics** - Low-level input monitoring
- **Security applications** - Input behavior analysis
- **Development tools** - API integration testing

## Architecture

```
┌─────────────────────────────────────────┐
│         Advanced Mouse Tracker          │
├─────────────────────────────────────────┤
│  Tkinter GUI Layer (60 FPS)            │
│  ├── Canvas Rendering                   │
│  ├── UI Controls                        │
│  └── Event Handling                     │
├─────────────────────────────────────────┤
│  Processing Layer                       │
│  ├── Velocity Calculations              │
│  ├── Collision Detection                │
│  ├── Statistics Tracking                │
│  └── Effect Management                  │
├─────────────────────────────────────────┤
│  Raw Input Layer (Threading)           │
│  ├── Queue Management                   │
│  ├── Data Processing                    │
│  └── Event Distribution                 │
├─────────────────────────────────────────┤
│  Windows API Layer                     │
│  ├── Raw Input Device Registration     │
│  ├── Message Loop Processing           │
│  ├── Fallback Mechanisms               │
│  └── Error Handling                    │
└─────────────────────────────────────────┘
```

## Development

### Adding New Features

1. **Visual Effects** - Extend the `draw_all()` method
2. **Input Processing** - Modify raw input callbacks
3. **Statistics** - Add to the statistics tracking system
4. **Controls** - Create new toggle methods and shortcuts

### Performance Tuning

- Adjust `max_history_points` for memory vs. precision trade-off
- Modify animation frame rate in `animate()` method
- Optimize numpy operations for collision detection
- Tune queue processing frequency

## Troubleshooting

### Common Issues

#### Raw Input Registration Fails

```
⚠️ Warning: Failed to register raw input devices. Error: 0
```

**Solution:** This is normal on some Windows configurations. The app continues with message monitoring fallback.

#### High CPU Usage

**Solution:** Reduce frame rate or history points:

```python
self.root.after(33, self.animate)  # 30 FPS instead of 60
self.max_history_points = 1000     # Reduce from 5000
```

#### Threading Issues

**Solution:** Ensure proper cleanup:

```python
def stop_and_quit(self):
    if self.raw_input_reader:
        self.raw_input_reader.stop()
    self.root.quit()
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Windows Raw Input API documentation
- Tkinter and numpy communities
- Python threading and queue documentation
- UV package manager for dependency management

---

**Created:** September 2025  
**Language:** Python 3.11+  
**Dependencies:** tkinter, numpy, ctypes, threading, queue  
**Platform:** Windows (Raw Input API specific)
