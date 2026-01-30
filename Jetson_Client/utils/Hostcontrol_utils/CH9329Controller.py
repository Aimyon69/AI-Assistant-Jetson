import serial
import time

class CH9329Controller:
    def __init__(self, port='/dev/ttyCH341USB0', baudrate=9600):
        """初始化串口"""
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            print(f"✅ 串口已连接: {port}")
        except Exception as e:
            print(f"❌ 串口连接失败: {e}")
            self.ser = None

    def _send_packet(self, cmd, length, data):
        """
        核心发送函数：自动计算 '基础和+2' 的校验码
        """
        if not self.ser: return

        head = [0x57, 0xAB]
        addr = 0x00
        
        # 1. 计算基础校验和 (Addr + Cmd + Len + Sum(Data))
        base_sum = addr + cmd + length + sum(data)
        
        # 2. 【关键修正】根据你的图片，结果必须 +2
        checksum = (base_sum + 2) & 0xFF
        
        # 3. 组包发送
        packet = head + [addr, cmd, length] + data + [checksum]
        self.ser.write(bytearray(packet))
        # 稍微延时，防止指令太快模块处理不过来
        time.sleep(0.02) 

    # ================= 键盘功能 =================
    
    def press_key(self, key_code, modifier=0x00):
        """
        按下并释放一个键
        :param key_code: HID键码 (如 'a'是0x04)
        :param modifier: 修饰键 (Shift=0x02, Ctrl=0x01, Alt=0x04)
        """
        # 按下
        data_press = [0x00] * 8
        data_press[0] = modifier # Byte 0: 修饰键
        data_press[2] = key_code # Byte 2: 键值
        self._send_packet(0x02, 0x08, data_press)
        
        time.sleep(0.05) # 模拟按键时长
        
        # 释放 (发送全0)
        data_release = [0x00] * 8
        self._send_packet(0x02, 0x08, data_release)

    def type_string(self, text):
        """
        自动输入字符串（支持小写字母和数字）
        """
        print(f"⌨️ 正在输入: {text}")
        for char in text:
            # 简单的映射逻辑
            if 'a' <= char <= 'z':
                code = 0x04 + (ord(char) - ord('a'))
                self.press_key(code)
            elif '0' <= char <= '9':
                if char == '0': code = 0x27
                else: code = 0x1E + (ord(char) - ord('1'))
                self.press_key(code)
            elif char == ' ':
                self.press_key(0x2C) # Space
            elif char == '\n':
                self.press_key(0x28) # Enter
            # ... 其他符号需要查HID表补充
            time.sleep(0.05) # 打字速度

    # ================= 鼠标功能 =================
    # 根据图片：Cmd=0x05, Len=0x05, Data=[0x01, Buttons, X, Y, Wheel]
    
    def send_mouse(self, buttons=0, x=0, y=0, wheel=0):
        """
        发送鼠标动作
        :param buttons: 1=左键, 2=右键, 4=中键
        :param x: 水平移动 (-128 ~ 127)
        :param y: 垂直移动 (-128 ~ 127)
        """
        # 处理负数 (转补码)
        if x < 0: x = (x + 256) & 0xFF
        if y < 0: y = (y + 256) & 0xFF
        if wheel < 0: wheel = (wheel + 256) & 0xFF
        
        # 固定结构: [0x01, 按键, X, Y, 滚轮]
        data = [0x01, buttons, x, y, wheel]
        self._send_packet(0x05, 0x05, data)

    def click_left(self):
        """单击左键"""
        self.send_mouse(buttons=0x01) # 按下
        time.sleep(0.1)
        self.send_mouse(buttons=0x00) # 松开

    def move_mouse_relative(self, x, y):
        """移动鼠标 (相对距离)"""
        self.send_mouse(x=x, y=y)

    def close(self):
        if self.ser: self.ser.close()

# ================= 使用示例 =================

if __name__ == "__main__":
    # 实例化 (记得改波特率，如果你试出来是 115200)
    controller = CH9329Controller(baudrate=9600)
    
    # 1. 输入密码示例
    # controller.type_string("password123")
    # controller.press_key(0x28) # 回车
    
    # 2. 鼠标示例 (画个圈或者抖动一下)
    # controller.move_mouse_relative(10, 10) # 向右下移动
    # controller.click_left()
    
    controller.close()