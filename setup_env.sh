#!/bin/bash

# ROS 1 Bag Stereo Image Extractor - Environment Setup Script
# For Ubuntu 22.04 with Conda

echo "======================================================================="
echo "  ROS 1 Bag Stereo Image Extractor - Environment Setup"
echo "======================================================================="
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Error: Conda is not installed or not in PATH"
    echo "Please install Miniconda or Anaconda first:"
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "Step 1: Creating Conda environment 'astra_calib_env' with Python 3.9..."
conda create -n astra_calib_env python=3.9 -y

if [ $? -ne 0 ]; then
    echo "Error: Failed to create conda environment"
    exit 1
fi

echo ""
echo "Step 2: Activating environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate astra_calib_env

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate environment"
    exit 1
fi

echo ""
echo "Step 3: Installing Python packages..."
pip install opencv-python numpy

echo ""
echo "Step 4: Installing ROS bag support..."
pip install --extra-index-url https://rospypi.github.io/simple/ rosbag rospkg

echo ""
echo "Step 5: Installing bagpy..."
pip install bagpy

echo ""
echo "======================================================================="
echo "  Installation Complete!"
echo "======================================================================="
echo ""
echo "To use the extractor:"
echo "  1. Activate the environment: conda activate astra_calib_env"
echo "  2. Run the script: python extract_stereo_images.py your_file.bag"
echo ""
echo "To deactivate: conda deactivate"
echo ""
