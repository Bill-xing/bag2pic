# Bag2Pic - ROS Bag 双目图像提取工具

[![Python 版本](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![ROS](https://img.shields.io/badge/ROS-ROS%201-brightgreen.svg)](https://www.ros.org/)
[![许可证](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

从 ROS 1 bag 文件中提取并同步双目图像（RGB + IR），支持时间戳对齐。适用于 MATLAB 双目相机标定。

[English](README.md) | 简体中文

## 主要特性

- **ROS 1 支持**: 解析 `.bag` 文件，支持 LZ4 压缩
- **时间戳同步**: 基于时间戳自动对齐 RGB 和 IR 图像
- **多种编码**: 支持 `rgb8`, `bgr8`, `yuyv`, `mono8`, `mono16` 等
- **镜像修正**: 可选的水平翻转功能，用于相机对齐
- **MATLAB 兼容**: 输出格式直接适用于 MATLAB Stereo Camera Calibrator
- **鲁棒处理**: 自动跳过损坏帧，提供详细统计

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/bag2pic.git
cd bag2pic

# 运行安装脚本
bash setup_env.sh

# 激活环境
conda activate astra_calib_env
```

### 使用

```bash
# 1. 检查 bag 文件中的话题
python inspect_bag.py your_file.bag

# 2. 提取并同步图像
python extract_stereo_images.py your_file.bag \
    --rgb-topic /cam/sensor_1/frameType_1 \
    --ir-topic /cam/sensor_2/frameType_2 \
    --time-threshold 0.08 \
    --flip-ir

# 3. 图像保存在 output/rgb 和 output/ir
```

## 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `bag_file` | str | *必需* | ROS bag 文件路径 |
| `--rgb-topic` | str | `/camera/color/image_raw` | RGB 图像话题名 |
| `--ir-topic` | str | `/camera/ir/image_raw` | 红外图像话题名 |
| `--output-dir` | str | `output` | 输出目录路径 |
| `--time-threshold` | float | `0.03` | 同步的最大时间差（秒）|
| `--flip-rgb` | 标志 | `False` | 水平翻转 RGB 图像 |
| `--flip-ir` | 标志 | `False` | 水平翻转 IR 图像 |

## 使用示例

### Orbbec Astra 相机

```bash
python extract_stereo_images.py data.bag \
    --rgb-topic /cam/sensor_1/frameType_1 \
    --ir-topic /cam/sensor_2/frameType_2 \
    --time-threshold 0.08 \
    --flip-ir
```

### Intel RealSense

```bash
python extract_stereo_images.py data.bag \
    --rgb-topic /camera/color/image_raw \
    --ir-topic /camera/infrared/image_raw
```

## 输出格式

```
output/
├── rgb/
│   ├── 0001.png
│   ├── 0002.png
│   └── ...
└── ir/
    ├── 0001.png
    ├── 0002.png
    └── ...
```

**特点**:
- 文件名匹配确保图像对应（例如 `rgb/0001.png` ↔ `ir/0001.png`）
- PNG 格式保证无损质量
- 从 0001 开始的连续编号
- 可直接用于 MATLAB Stereo Camera Calibrator

## 常见问题

### 问题："No synchronized pairs found"

**原因**: 时间戳差异超过阈值

**解决方法**:
```bash
python extract_stereo_images.py data.bag --time-threshold 0.1
```

### 问题："unsupported compression type: lz4"

**原因**: 未安装 LZ4 压缩支持

**解决方法**:
```bash
pip install --extra-index-url https://rospypi.github.io/simple/ roslz4
```

### 问题：话题名称错误

**原因**: 不同相机的话题名称不同

**解决方法**:
```bash
python inspect_bag.py your_file.bag
```

## 在 MATLAB 中使用

1. 打开 MATLAB
2. 启动 **Stereo Camera Calibrator** 应用
3. 点击 **Add Images**
4. 相机 1 选择 `output/rgb/` 文件夹
5. 相机 2 选择 `output/ir/` 文件夹
6. 设置棋盘格参数
7. 运行标定

## 支持的硬件

- ✅ Orbbec Astra 2
- ✅ Intel RealSense D435
- ✅ 支持 ROS 1 的通用双目相机

## 项目结构

```
bag2pic/
├── extract_stereo_images.py    # 主提取脚本
├── inspect_bag.py              # Bag 检查工具
├── setup_env.sh                # 自动环境配置
├── check_install.sh            # 安装检查脚本
├── examples.sh                 # 示例用法脚本
├── requirements.txt            # Python 依赖
├── environment.yml             # Conda 环境定义
├── README.md                   # 英文文档
├── README_CN.md                # 本文件
├── QUICKSTART.md               # 快速入门指南
├── CONTRIBUTING.md             # 贡献指南
├── CHANGELOG.md                # 更新日志
├── LICENSE                     # MIT 许可证
└── .gitignore                  # Git 忽略规则
```

## 技术细节

### 同步算法

1. 从 RGB 和 IR 话题提取所有消息
2. 按时间戳排序
3. 为每个 RGB 帧寻找最近的 IR 帧
4. 仅接受时间差 < 阈值的图像对
5. 跳过无法匹配的帧

### 时间戳对齐

```python
time_diff = abs(rgb_timestamp - ir_timestamp)
if time_diff <= threshold:
    save_pair(rgb_img, ir_img)
```

**默认阈值**: 30ms (0.03s)
**Orbbec Astra 推荐**: 80ms (0.08s)

## 性能指标

- **处理速度**: 1000 帧约 10-30 秒
- **内存占用**: 约 100-200 MB（取决于分辨率）
- **存储空间**: 每对图像约 1-2 MB（取决于分辨率和内容）

## 支持的图像编码

### 彩色图像
- `rgb8` - 8 位 RGB
- `bgr8` - 8 位 BGR（OpenCV 默认）
- `yuyv` / `yuv422` - YUV 4:2:2 格式

### 灰度/红外图像
- `mono8` - 8 位灰度
- `mono16` - 16 位灰度（自动转换为 8 位）
- `8UC1` - 8 位单通道
- `16UC1` - 16 位单通道

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- 为双目相机标定工作流程而构建
- 感谢 ROS 和 OpenCV 社区

## 联系方式

如有问题或建议，请在 GitHub 上开 issue。

---

**用 ❤️ 为机器人社区打造**
