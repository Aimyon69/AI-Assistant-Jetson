#!/bin/bash
# 这是一个用于配置 Jetson USB Gadget 为 HID 键盘的脚本
#以此根用户权限运行 (sudo)

# 1. 定义变量
GADGET_DIR="/sys/kernel/config/usb_gadget/l4t"
VID="0x0955"
PID="0x7020" # 使用 Tegra 的默认 ID

# 注意：如果 Jetson 已经在运行默认的 l4t-usb-device-mode，
# 我们通常需要先停止它，或者在它基础上修改。
# 为简单起见，这里假设我们添加一个新的 HID 功能，
# 但最稳妥的方法是直接使用 Python 往 /dev/hidg0 写数据（如果由于 L4T 默认脚本存在）。

# 检查是否已有 hidg0，如果没有，则需要配置 ConfigFS
if [ ! -e "/dev/hidg0" ]; then
    echo "正在配置 USB HID..."
    # 停止当前的 USB gadget 服务 (警告：如果你是通过 USB SSH 的，这会断开连接！)
    # systemctl stop nv-l4t-usb-device-mode
    
    # 这里是一个简化的通用 ConfigFS 配置流程
    # 实际在 Jetson 上，最简单的“无痛”方法是修改 /opt/nvidia/l4t-usb-device-mode/nv-l4t-usb-device-mode.sh
    # 找到 enable_hid 相关部分并取消注释，然后重启服务。
    
    echo "请检查 /opt/nvidia/l4t-usb-device-mode/nv-l4t-usb-device-mode.sh"
    echo "确保在这个官方脚本中，enable_hid=1 被设置。"
else
    echo "检测到 /dev/hidg0 已存在！可以直接运行 Python 脚本。"
fi