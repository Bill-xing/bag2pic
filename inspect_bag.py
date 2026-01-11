#!/usr/bin/env python3
"""
Quick tool to inspect ROS bag file topics and message counts
"""

import sys
import argparse

# Remove ROS 2 paths to avoid conflicts with ROS 1 rosbag
sys.path = [p for p in sys.path if '/opt/ros/' not in p]


def inspect_bag(bag_file):
    """Display information about topics in the bag file"""
    try:
        import rosbag
    except ImportError:
        print("Error: rosbag not installed")
        print("Please run: pip install --extra-index-url https://rospypi.github.io/simple/ rosbag")
        sys.exit(1)

    print("="*70)
    print(f"Inspecting bag file: {bag_file}")
    print("="*70)

    with rosbag.Bag(bag_file, 'r') as bag:
        info = bag.get_type_and_topic_info()

        print(f"\nTotal duration: {bag.get_end_time() - bag.get_start_time():.2f} seconds")
        print(f"Total messages: {bag.get_message_count()}")

        print(f"\nTopics ({len(info.topics)}):")
        print("-"*70)

        image_topics = []

        for topic_name, topic_info in info.topics.items():
            msg_count = topic_info.message_count
            msg_type = topic_info.msg_type
            freq = topic_info.frequency

            print(f"\nTopic: {topic_name}")
            print(f"  Type: {msg_type}")
            print(f"  Messages: {msg_count}")
            if freq is not None:
                print(f"  Frequency: {freq:.2f} Hz")
            else:
                duration = bag.get_end_time() - bag.get_start_time()
                if duration > 0:
                    print(f"  Frequency: {msg_count/duration:.2f} Hz (calculated)")
                else:
                    print(f"  Frequency: N/A")

            if 'Image' in msg_type:
                image_topics.append(topic_name)

        if image_topics:
            print("\n" + "="*70)
            print("Image topics detected:")
            print("="*70)
            for topic in image_topics:
                print(f"  - {topic}")

            print("\nSuggested command:")
            if len(image_topics) >= 2:
                print(f"python extract_stereo_images.py {bag_file} \\")
                print(f"    --rgb-topic {image_topics[0]} \\")
                print(f"    --ir-topic {image_topics[1]}")
            else:
                print(f"python extract_stereo_images.py {bag_file} \\")
                print(f"    --rgb-topic <your_rgb_topic> \\")
                print(f"    --ir-topic <your_ir_topic>")
        else:
            print("\nNo image topics found in this bag file.")

        print("="*70)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Inspect ROS bag file')
    parser.add_argument('bag_file', help='Path to bag file')
    args = parser.parse_args()

    inspect_bag(args.bag_file)
