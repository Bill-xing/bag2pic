#!/bin/bash

# Example usage script for Bag2Pic
# This script demonstrates common usage patterns

echo "======================================================================="
echo "  Bag2Pic - Example Usage"
echo "======================================================================="
echo ""

# Check if bag file is provided
if [ $# -eq 0 ]; then
    echo "Usage: bash examples.sh <your_bag_file.bag>"
    echo ""
    echo "This script will demonstrate different ways to use Bag2Pic"
    exit 1
fi

BAG_FILE="$1"

# Check if file exists
if [ ! -f "$BAG_FILE" ]; then
    echo "Error: Bag file not found: $BAG_FILE"
    exit 1
fi

# Activate environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate astra_calib_env

echo "Bag file: $BAG_FILE"
echo ""

# Example 1: Inspect the bag
echo "======================================================================="
echo "Example 1: Inspecting bag file"
echo "======================================================================="
echo "Command: python inspect_bag.py \"$BAG_FILE\""
echo ""
read -p "Press Enter to run, or Ctrl+C to skip... "
python inspect_bag.py "$BAG_FILE"
echo ""

# Example 2: Basic extraction
echo "======================================================================="
echo "Example 2: Basic extraction with default topics"
echo "======================================================================="
echo "Command: python extract_stereo_images.py \"$BAG_FILE\""
echo ""
echo "This will use default topics:"
echo "  RGB: /camera/color/image_raw"
echo "  IR:  /camera/ir/image_raw"
echo ""
read -p "Press Enter to run, or Ctrl+C to skip... "
python extract_stereo_images.py "$BAG_FILE" --output-dir output_example1
echo ""

# Example 3: Custom topics (Orbbec Astra)
echo "======================================================================="
echo "Example 3: Extraction with custom topics (Orbbec Astra)"
echo "======================================================================="
echo "Command:"
echo "  python extract_stereo_images.py \"$BAG_FILE\" \\"
echo "      --rgb-topic /cam/sensor_1/frameType_1 \\"
echo "      --ir-topic /cam/sensor_2/frameType_2 \\"
echo "      --time-threshold 0.08 \\"
echo "      --flip-ir"
echo ""
read -p "Press Enter to run, or Ctrl+C to skip... "
python extract_stereo_images.py "$BAG_FILE" \
    --rgb-topic /cam/sensor_1/frameType_1 \
    --ir-topic /cam/sensor_2/frameType_2 \
    --time-threshold 0.08 \
    --flip-ir \
    --output-dir output_example3
echo ""

# Example 4: Custom output directory
echo "======================================================================="
echo "Example 4: Custom output directory"
echo "======================================================================="
echo "Command:"
echo "  python extract_stereo_images.py \"$BAG_FILE\" \\"
echo "      --output-dir ./my_calibration_images"
echo ""
read -p "Press Enter to run, or Ctrl+C to skip... "
python extract_stereo_images.py "$BAG_FILE" \
    --output-dir ./my_calibration_images
echo ""

# Example 5: Larger time threshold
echo "======================================================================="
echo "Example 5: Extraction with larger time threshold"
echo "======================================================================="
echo "Use this if you get 'No synchronized pairs found' error"
echo ""
echo "Command:"
echo "  python extract_stereo_images.py \"$BAG_FILE\" \\"
echo "      --time-threshold 0.15"
echo ""
read -p "Press Enter to run, or Ctrl+C to skip... "
python extract_stereo_images.py "$BAG_FILE" \
    --time-threshold 0.15 \
    --output-dir output_example5
echo ""

echo "======================================================================="
echo "Examples completed!"
echo "======================================================================="
echo ""
echo "Check the output directories:"
echo "  - output_example1/"
echo "  - output_example3/"
echo "  - my_calibration_images/"
echo "  - output_example5/"
echo ""
echo "Next steps:"
echo "  1. Review extracted images"
echo "  2. Select best 40-60 pairs for calibration"
echo "  3. Import into MATLAB Stereo Camera Calibrator"
echo ""
