#!/bin/bash

# Check installation script for Bag2Pic

echo "======================================================================="
echo "  Bag2Pic Installation Check"
echo "======================================================================="
echo ""

# Check if conda is installed
echo -n "Checking conda installation... "
if command -v conda &> /dev/null; then
    echo "✓ Found ($(conda --version))"
else
    echo "✗ Not found"
    echo "Please install Miniconda or Anaconda"
    exit 1
fi

# Check if environment exists
echo -n "Checking astra_calib_env environment... "
if conda env list | grep -q "astra_calib_env"; then
    echo "✓ Found"
else
    echo "✗ Not found"
    echo "Run: bash setup_env.sh"
    exit 1
fi

# Activate environment and check packages
source $(conda info --base)/etc/profile.d/conda.sh
conda activate astra_calib_env

echo ""
echo "Checking Python packages:"
echo "-------------------------"

packages=("numpy" "cv2" "rosbag" "PIL")
package_names=("numpy" "opencv-python" "rosbag" "pillow")

all_good=true
for i in "${!packages[@]}"; do
    pkg="${packages[$i]}"
    name="${package_names[$i]}"
    echo -n "  - $name... "
    if python -c "import $pkg" 2>/dev/null; then
        version=$(python -c "import $pkg; print(getattr($pkg, '__version__', 'unknown'))" 2>/dev/null)
        echo "✓ ($version)"
    else
        echo "✗ Not found"
        all_good=false
    fi
done

echo ""
echo "Checking LZ4 support:"
echo "---------------------"
echo -n "  - roslz4... "
if python -c "import roslz4" 2>/dev/null; then
    echo "✓ Installed"
else
    echo "✗ Not found (optional, needed for LZ4-compressed bags)"
    echo "    Install with: pip install --extra-index-url https://rospypi.github.io/simple/ roslz4"
fi

echo ""
echo "Checking scripts:"
echo "-----------------"
scripts=("extract_stereo_images.py" "inspect_bag.py" "setup_env.sh")
for script in "${scripts[@]}"; do
    echo -n "  - $script... "
    if [ -f "$script" ]; then
        echo "✓ Found"
    else
        echo "✗ Not found"
        all_good=false
    fi
done

echo ""
echo "======================================================================="
if [ "$all_good" = true ]; then
    echo "  ✓ Installation Check PASSED"
    echo "======================================================================="
    echo ""
    echo "You're ready to use Bag2Pic!"
    echo ""
    echo "Quick start:"
    echo "  1. python inspect_bag.py your_file.bag"
    echo "  2. python extract_stereo_images.py your_file.bag [options]"
    echo ""
    echo "For detailed instructions, see QUICKSTART.md"
else
    echo "  ✗ Installation Check FAILED"
    echo "======================================================================="
    echo ""
    echo "Some components are missing. Please run:"
    echo "  bash setup_env.sh"
    exit 1
fi
