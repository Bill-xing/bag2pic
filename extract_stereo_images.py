#!/usr/bin/env python3
"""
ROS 1 Bag File Stereo Image Extractor with Timestamp Synchronization
Extracts RGB and IR images from .bag files and aligns them for MATLAB calibration
"""

import os
import sys

# Remove ROS 2 paths to avoid conflicts with ROS 1 rosbag
sys.path = [p for p in sys.path if '/opt/ros/' not in p]

import numpy as np
import cv2
from pathlib import Path
import argparse


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Extract synchronized stereo images from ROS 1 bag file'
    )
    parser.add_argument(
        'bag_file',
        type=str,
        help='Path to the .bag file'
    )
    parser.add_argument(
        '--rgb-topic',
        type=str,
        default='/camera/color/image_raw',
        help='RGB image topic name (default: /camera/color/image_raw)'
    )
    parser.add_argument(
        '--ir-topic',
        type=str,
        default='/camera/ir/image_raw',
        help='IR image topic name (default: /camera/ir/image_raw)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory (default: output)'
    )
    parser.add_argument(
        '--time-threshold',
        type=float,
        default=0.03,
        help='Maximum time difference in seconds for synchronization (default: 0.03)'
    )
    parser.add_argument(
        '--flip-rgb',
        action='store_true',
        help='Flip RGB images horizontally (left-right mirror)'
    )
    parser.add_argument(
        '--flip-ir',
        action='store_true',
        help='Flip IR images horizontally (left-right mirror)'
    )
    parser.add_argument(
        '--frame-interval',
        type=int,
        default=1,
        help='Save every Nth frame (default: 1, save all frames). Use 5-10 to skip similar frames'
    )
    return parser.parse_args()


def setup_output_directories(output_dir):
    """Create output directories for RGB and IR images"""
    rgb_dir = Path(output_dir) / 'rgb'
    ir_dir = Path(output_dir) / 'ir'

    rgb_dir.mkdir(parents=True, exist_ok=True)
    ir_dir.mkdir(parents=True, exist_ok=True)

    return rgb_dir, ir_dir


def decode_image(msg_data, encoding, width, height):
    """
    Decode ROS sensor_msgs/Image to OpenCV format

    Args:
        msg_data: Raw image data bytes
        encoding: Image encoding (e.g., 'rgb8', 'yuyv', 'mono8')
        width: Image width
        height: Image height

    Returns:
        OpenCV image (BGR format for color, grayscale for mono)
    """
    try:
        if encoding == 'rgb8':
            img = np.frombuffer(msg_data, dtype=np.uint8).reshape(height, width, 3)
            return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        elif encoding == 'bgr8':
            img = np.frombuffer(msg_data, dtype=np.uint8).reshape(height, width, 3)
            return img

        elif encoding == 'yuyv' or encoding == 'yuv422':
            img = np.frombuffer(msg_data, dtype=np.uint8).reshape(height, width, 2)
            return cv2.cvtColor(img, cv2.COLOR_YUV2BGR_YUYV)

        elif encoding == 'mono8' or encoding == '8UC1':
            img = np.frombuffer(msg_data, dtype=np.uint8).reshape(height, width)
            return img

        elif encoding == 'mono16' or encoding == '16UC1':
            img = np.frombuffer(msg_data, dtype=np.uint16).reshape(height, width)
            img_8bit = (img / 256).astype(np.uint8)
            return img_8bit

        else:
            print(f"Warning: Unsupported encoding '{encoding}', attempting raw decode")
            img = np.frombuffer(msg_data, dtype=np.uint8).reshape(height, width, -1)
            if img.shape[2] == 3:
                return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            return img

    except Exception as e:
        print(f"Error decoding image with encoding '{encoding}': {e}")
        return None


def extract_messages_bagpy(bag_file, rgb_topic, ir_topic):
    """
    Extract messages from bag file using bagpy

    Returns:
        rgb_messages: List of (timestamp, image_data) tuples
        ir_messages: List of (timestamp, image_data) tuples
    """
    try:
        from bagpy import bagreader
    except ImportError:
        print("Error: bagpy not installed. Please run: pip install bagpy")
        sys.exit(1)

    print(f"Opening bag file: {bag_file}")
    bag = bagreader(bag_file)

    print(f"Available topics:")
    for topic in bag.topic_table['Topics']:
        print(f"  - {topic}")

    rgb_messages = []
    ir_messages = []

    print(f"\nExtracting messages from topics:")
    print(f"  RGB topic: {rgb_topic}")
    print(f"  IR topic: {ir_topic}")

    try:
        import rosbag
        with rosbag.Bag(bag_file, 'r') as bag_reader:
            total_messages = bag_reader.get_message_count([rgb_topic, ir_topic])
            print(f"\nTotal messages to process: {total_messages}")

            processed = 0
            for topic, msg, t in bag_reader.read_messages(topics=[rgb_topic, ir_topic]):
                timestamp = t.to_sec()

                if topic == rgb_topic:
                    rgb_messages.append({
                        'timestamp': timestamp,
                        'encoding': msg.encoding,
                        'width': msg.width,
                        'height': msg.height,
                        'data': msg.data
                    })
                elif topic == ir_topic:
                    ir_messages.append({
                        'timestamp': timestamp,
                        'encoding': msg.encoding,
                        'width': msg.width,
                        'height': msg.height,
                        'data': msg.data
                    })

                processed += 1
                if processed % 100 == 0:
                    print(f"Processed {processed}/{total_messages} messages...", end='\r')

            print(f"\nExtracted {len(rgb_messages)} RGB frames and {len(ir_messages)} IR frames")

    except ImportError:
        print("Error: rosbag not installed. Trying alternative method...")
        print("Please install rosbag: pip install --extra-index-url https://rospypi.github.io/simple/ rosbag")
        sys.exit(1)

    return rgb_messages, ir_messages


def synchronize_images(rgb_messages, ir_messages, time_threshold):
    """
    Synchronize RGB and IR images based on timestamps

    Args:
        rgb_messages: List of RGB message dictionaries
        ir_messages: List of IR message dictionaries
        time_threshold: Maximum time difference in seconds

    Returns:
        List of synchronized (rgb_msg, ir_msg, time_diff) tuples
    """
    print(f"\nSynchronizing images (threshold: {time_threshold}s)...")

    # Debug: show first few timestamps
    if rgb_messages and ir_messages:
        print(f"\nDebug - First RGB timestamps:")
        for i in range(min(3, len(rgb_messages))):
            print(f"  RGB[{i}]: {rgb_messages[i]['timestamp']:.6f}")
        print(f"\nDebug - First IR timestamps:")
        for i in range(min(3, len(ir_messages))):
            print(f"  IR[{i}]: {ir_messages[i]['timestamp']:.6f}")

        first_time_diff = abs(rgb_messages[0]['timestamp'] - ir_messages[0]['timestamp'])
        print(f"\nFirst timestamp difference: {first_time_diff:.6f} s ({first_time_diff*1000:.2f} ms)\n")

    synchronized_pairs = []
    time_diffs = []

    ir_index = 0
    total_rgb = len(rgb_messages)

    for rgb_idx, rgb_msg in enumerate(rgb_messages):
        rgb_time = rgb_msg['timestamp']

        min_time_diff = float('inf')
        best_ir_msg = None

        start_search = max(0, ir_index - 5)

        for i in range(start_search, len(ir_messages)):
            ir_msg = ir_messages[i]
            ir_time = ir_msg['timestamp']
            time_diff = abs(rgb_time - ir_time)

            if time_diff < min_time_diff:
                min_time_diff = time_diff
                best_ir_msg = ir_msg
                ir_index = i

            if ir_time > rgb_time + time_threshold:
                break

        if best_ir_msg is not None and min_time_diff <= time_threshold:
            synchronized_pairs.append((rgb_msg, best_ir_msg, min_time_diff))
            time_diffs.append(min_time_diff)

        if (rgb_idx + 1) % 50 == 0:
            print(f"Synchronized {rgb_idx + 1}/{total_rgb} RGB frames...", end='\r')

    print(f"\nSuccessfully synchronized {len(synchronized_pairs)} image pairs")

    if time_diffs:
        avg_time_diff = np.mean(time_diffs)
        max_time_diff = np.max(time_diffs)
        print(f"Average time difference: {avg_time_diff*1000:.2f} ms")
        print(f"Maximum time difference: {max_time_diff*1000:.2f} ms")

    return synchronized_pairs


def save_synchronized_images(synchronized_pairs, rgb_dir, ir_dir, flip_rgb=False, flip_ir=False, frame_interval=1):
    """
    Save synchronized image pairs with matching filenames

    Args:
        synchronized_pairs: List of (rgb_msg, ir_msg, time_diff) tuples
        rgb_dir: Output directory for RGB images
        ir_dir: Output directory for IR images
        flip_rgb: Whether to flip RGB images horizontally
        flip_ir: Whether to flip IR images horizontally
        frame_interval: Save every Nth frame (1 = save all)
    """
    print(f"\nSaving images to:")
    print(f"  RGB: {rgb_dir}")
    print(f"  IR:  {ir_dir}")

    if flip_rgb:
        print(f"  Note: RGB images will be flipped horizontally")
    if flip_ir:
        print(f"  Note: IR images will be flipped horizontally")
    if frame_interval > 1:
        print(f"  Note: Saving every {frame_interval} frames (frame interval={frame_interval})")

    saved_count = 0
    output_index = 1

    for idx, (rgb_msg, ir_msg, time_diff) in enumerate(synchronized_pairs):
        # Skip frames based on interval
        if idx % frame_interval != 0:
            continue

        filename = f"{output_index:04d}.png"

        rgb_img = decode_image(
            rgb_msg['data'],
            rgb_msg['encoding'],
            rgb_msg['width'],
            rgb_msg['height']
        )

        ir_img = decode_image(
            ir_msg['data'],
            ir_msg['encoding'],
            ir_msg['width'],
            ir_msg['height']
        )

        if rgb_img is None or ir_img is None:
            print(f"Warning: Failed to decode image pair {idx+1}, skipping")
            continue

        # Apply horizontal flip if requested
        if flip_rgb:
            rgb_img = cv2.flip(rgb_img, 1)  # 1 = horizontal flip
        if flip_ir:
            ir_img = cv2.flip(ir_img, 1)  # 1 = horizontal flip

        rgb_path = rgb_dir / filename
        ir_path = ir_dir / filename

        cv2.imwrite(str(rgb_path), rgb_img)
        cv2.imwrite(str(ir_path), ir_img)

        saved_count += 1
        output_index += 1

        if saved_count % 50 == 0:
            print(f"Saved {saved_count} image pairs...", end='\r')

    print(f"\nSuccessfully saved {saved_count} synchronized image pairs")
    return saved_count


def main():
    args = parse_arguments()

    if not os.path.exists(args.bag_file):
        print(f"Error: Bag file not found: {args.bag_file}")
        sys.exit(1)

    print("="*70)
    print("ROS 1 Bag Stereo Image Extractor")
    print("="*70)

    rgb_dir, ir_dir = setup_output_directories(args.output_dir)

    rgb_messages, ir_messages = extract_messages_bagpy(
        args.bag_file,
        args.rgb_topic,
        args.ir_topic
    )

    if len(rgb_messages) == 0 or len(ir_messages) == 0:
        print("\nError: No messages found in one or both topics")
        print("Please check the topic names with: rosbag info <bag_file>")
        sys.exit(1)

    synchronized_pairs = synchronize_images(
        rgb_messages,
        ir_messages,
        args.time_threshold
    )

    if len(synchronized_pairs) == 0:
        print("\nWarning: No synchronized pairs found!")
        print("Try increasing the time threshold with --time-threshold")
        sys.exit(1)

    saved_count = save_synchronized_images(
        synchronized_pairs,
        rgb_dir,
        ir_dir,
        flip_rgb=args.flip_rgb,
        flip_ir=args.flip_ir,
        frame_interval=args.frame_interval
    )

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total RGB frames extracted:     {len(rgb_messages)}")
    print(f"Total IR frames extracted:      {len(ir_messages)}")
    print(f"Synchronized pairs found:       {len(synchronized_pairs)}")
    print(f"Successfully saved:             {saved_count}")
    print(f"Synchronization success rate:   {saved_count/len(rgb_messages)*100:.1f}%")
    print("="*70)
    print("\nImages ready for MATLAB Stereo Camera Calibrator!")


if __name__ == '__main__':
    main()
