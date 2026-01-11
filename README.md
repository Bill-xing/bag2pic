# Bag2Pic - ROS Bag Stereo Image Extractor

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![ROS](https://img.shields.io/badge/ROS-ROS%201-brightgreen.svg)](https://www.ros.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python tool for extracting and synchronizing stereo images (RGB + IR) from ROS 1 bag files with timestamp-based alignment. Perfect for stereo camera calibration in MATLAB.

## Features

- **ROS 1 Bag Support**: Extract images from `.bag` files with LZ4 compression
- **Timestamp Synchronization**: Automatically align RGB and IR images based on timestamps
- **Multiple Encodings**: Support for `rgb8`, `bgr8`, `yuyv`, `mono8`, `mono16`, and more
- **Mirror Correction**: Optional horizontal flip for camera alignment
- **MATLAB Ready**: Output format compatible with MATLAB Stereo Camera Calibrator
- **Robust Processing**: Auto-skip corrupted frames with detailed statistics

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Command Line Arguments](#command-line-arguments)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Output Format](#output-format)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Ubuntu 22.04 (or similar Linux distribution)
- Conda or Miniconda
- Python 3.9+

### Option 1: Automatic Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/bag2pic.git
cd bag2pic

# Run setup script
bash setup_env.sh

# Activate environment
conda activate astra_calib_env
```

### Option 2: Manual Setup

```bash
# Create conda environment
conda create -n astra_calib_env python=3.9 -y
conda activate astra_calib_env

# Install dependencies
pip install -r requirements.txt

# Install ROS bag support
pip install --extra-index-url https://rospypi.github.io/simple/ rosbag rospkg roslz4
```

### Option 3: Using environment.yml

```bash
conda env create -f environment.yml
conda activate astra_calib_env
```

## Quick Start

```bash
# 1. Inspect your bag file to find topic names
python inspect_bag.py your_file.bag

# 2. Extract and synchronize images
python extract_stereo_images.py your_file.bag \
    --rgb-topic /cam/sensor_1/frameType_1 \
    --ir-topic /cam/sensor_2/frameType_2 \
    --time-threshold 0.08 \
    --flip-ir

# 3. Images will be saved to output/rgb and output/ir
```

## Usage

### Inspect Bag File

Use `inspect_bag.py` to view topics and metadata:

```bash
python inspect_bag.py your_file.bag
```

**Output:**
```
======================================================================
Inspecting bag file: your_file.bag
======================================================================

Total duration: 59.40 seconds
Total messages: 595

Topics (6):
----------------------------------------------------------------------

Topic: /cam/sensor_1/frameType_1
  Type: sensor_msgs/Image
  Messages: 297
  Frequency: 5.00 Hz

Topic: /cam/sensor_2/frameType_2
  Type: sensor_msgs/Image
  Messages: 298
  Frequency: 5.00 Hz
```

### Extract Stereo Images

Use `extract_stereo_images.py` to extract and synchronize images:

```bash
python extract_stereo_images.py <bag_file> [options]
```

## Command Line Arguments

### extract_stereo_images.py

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bag_file` | str | *required* | Path to the ROS bag file |
| `--rgb-topic` | str | `/camera/color/image_raw` | RGB image topic name |
| `--ir-topic` | str | `/camera/ir/image_raw` | IR image topic name |
| `--output-dir` | str | `output` | Output directory path |
| `--time-threshold` | float | `0.03` | Max time difference for sync (seconds) |
| `--flip-rgb` | flag | `False` | Flip RGB images horizontally |
| `--flip-ir` | flag | `False` | Flip IR images horizontally |

## Examples

### Basic Usage

```bash
python extract_stereo_images.py data.bag
```

### Custom Topics

```bash
python extract_stereo_images.py data.bag \
    --rgb-topic /camera/color/image_raw \
    --ir-topic /camera/infrared/image_raw
```

### With Mirror Correction

For Orbbec Astra cameras where IR and RGB are mirrored:

```bash
python extract_stereo_images.py data.bag \
    --rgb-topic /cam/sensor_1/frameType_1 \
    --ir-topic /cam/sensor_2/frameType_2 \
    --flip-ir
```

### Larger Timestamp Tolerance

If cameras have hardware sync delay:

```bash
python extract_stereo_images.py data.bag \
    --time-threshold 0.1
```

### Custom Output Directory

```bash
python extract_stereo_images.py data.bag \
    --output-dir ./calibration_images
```

## Output Format

```
output/
├── rgb/
│   ├── 0001.png
│   ├── 0002.png
│   ├── 0003.png
│   └── ...
└── ir/
    ├── 0001.png
    ├── 0002.png
    ├── 0003.png
    └── ...
```

**Key Features:**
- Matching filenames ensure paired images (e.g., `rgb/0001.png` ↔ `ir/0001.png`)
- PNG format for lossless quality
- Sequential numbering starting from 0001
- Ready for MATLAB Stereo Camera Calibrator

## Troubleshooting

### Issue: "No synchronized pairs found"

**Cause:** Timestamp difference exceeds threshold

**Solution:**
```bash
# Increase time threshold (try 0.05, 0.08, or 0.1)
python extract_stereo_images.py data.bag --time-threshold 0.1
```

### Issue: "unsupported compression type: lz4"

**Cause:** LZ4 compression support not installed

**Solution:**
```bash
pip install --extra-index-url https://rospypi.github.io/simple/ roslz4
```

### Issue: "ImportError: cannot import name 'Log'"

**Cause:** ROS 2 and ROS 1 path conflict

**Solution:** The script automatically filters ROS 2 paths. If issue persists:
```bash
unset ROS_DISTRO
export PYTHONPATH=""
```

### Issue: Wrong topic names

**Cause:** Topic names vary between cameras

**Solution:**
```bash
# Use inspect tool to find correct topics
python inspect_bag.py your_file.bag
```

## Using with MATLAB

1. Open MATLAB
2. Launch **Stereo Camera Calibrator** app
3. Click **Add Images**
4. Select `output/rgb` folder for camera 1
5. Select `output/ir` folder for camera 2
6. Set checkerboard parameters
7. Run calibration

## Performance

- **Processing Speed**: ~10-30 seconds for 1000 frames
- **Memory Usage**: ~100-200 MB (varies with resolution)
- **Storage**: ~1-2 MB per image pair (depends on resolution and content)

## Supported Image Encodings

### Color Images
- `rgb8` - 8-bit RGB
- `bgr8` - 8-bit BGR (OpenCV default)
- `yuyv` / `yuv422` - YUV 4:2:2 format

### Grayscale/IR Images
- `mono8` - 8-bit grayscale
- `mono16` - 16-bit grayscale (auto-converted to 8-bit)
- `8UC1` - 8-bit single channel
- `16UC1` - 16-bit single channel

## Project Structure

```
bag2pic/
├── extract_stereo_images.py    # Main extraction script
├── inspect_bag.py              # Bag inspection utility
├── setup_env.sh                # Automated environment setup
├── requirements.txt            # Python dependencies
├── environment.yml             # Conda environment definition
├── README.md                   # This file
├── LICENSE                     # MIT License
└── .gitignore                  # Git ignore rules
```

## Technical Details

### Synchronization Algorithm

1. Extract all messages from RGB and IR topics
2. Sort by timestamp
3. For each RGB frame, find nearest IR frame
4. Accept pair only if time difference < threshold
5. Skip frames that cannot be matched

### Timestamp Alignment

```python
time_diff = abs(rgb_timestamp - ir_timestamp)
if time_diff <= threshold:
    save_pair(rgb_img, ir_img)
```

**Default threshold**: 30ms (0.03s)
**Recommended for Orbbec Astra**: 80ms (0.08s)

## Development

### Running Tests

```bash
# Test with sample bag file
python extract_stereo_images.py test_data/sample.bag --output-dir test_output

# Verify output
ls -R test_output/
```

### Debug Mode

Enable debug output by editing the script to print intermediate values:
```python
# Already included in synchronization output
Debug - First RGB timestamps:
  RGB[0]: 1768149158.735834
  RGB[1]: 1768149158.935834
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Changelog

### v1.0.0 (2026-01-12)
- Initial release
- ROS 1 bag file support
- Timestamp-based synchronization
- LZ4 compression support
- Horizontal flip options
- MATLAB output format

## Known Limitations

- Only supports ROS 1 bag format (not ROS 2)
- Requires all messages to fit in memory
- No real-time processing support
- Output is PNG only (no JPEG/TIFF options)

## Tested Hardware

- ✅ Orbbec Astra 2
- ✅ Intel RealSense D435
- ✅ Generic stereo cameras with ROS 1 drivers

## References

- [ROS Bag Files](http://wiki.ros.org/Bags)
- [MATLAB Stereo Camera Calibrator](https://www.mathworks.com/help/vision/ref/stereocameracalibrator-app.html)
- [OpenCV Documentation](https://docs.opencv.org/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for stereo camera calibration workflows
- Inspired by the need for robust ROS bag processing
- Thanks to the ROS and OpenCV communities

## Contact

For questions or issues, please open an issue on GitHub or contact the maintainers.

---

**Made with ❤️ for the robotics community**
