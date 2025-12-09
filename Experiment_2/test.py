import subprocess
import time
import os
import sys

# 辅助函数：打印分割线
def print_banner(text):
    print("\n" + "="*60)
    print(f" 🎬  {text}")
    print("="*60 + "\n")

def run_test():
    print_banner("启动基础设施 (CA中心 & 应用服务器)")
    
    # 1. 启动 CA
    ca_process = subprocess.Popen([sys.executable, "udp/udp_server.py"])
    time.sleep(1) 

    # 2. 启动 Server
    tcp_server_process = subprocess.Popen([sys.executable, "tcp/tcp_server.py"])
    time.sleep(1)

    # 3. 场景一：合法用户
    print_banner("场景一：合法用户 Alice (展示加密效果)")
    print("说明：Alice 向 CA 申请证书，并与 Server 进行 DES 加密通信。\n")
    
    # 我们直接调用 Client 代码中的类，而不是 subprocess，以便更好控制参数
    # 但为了模拟真实进程环境，这里创建一个临时脚本来运行合法 Client
    alice_script = """
import sys
import os
sys.path.append('tcp')
from tcp_client import SecureTcpClient
alice = SecureTcpClient("Alice", is_hacker=False)
alice.connect_and_send("My Secret Password is 123456")
"""
    with open("temp_alice.py", "w", encoding='utf-8') as f: f.write(alice_script)
    subprocess.call([sys.executable, "temp_alice.py"])
    time.sleep(1)

    # 4. 场景二：黑客攻击
    print_banner("场景二：黑客 Mallory (展示 CA 防御作用)")
    print("说明：Mallory 伪造了证书签名，试图连接 Server。\n")
    
    mallory_script = """
import sys
import os
sys.path.append('tcp')
from tcp_client import SecureTcpClient
# 开启黑客模式
mallory = SecureTcpClient("Mallory", is_hacker=True)
mallory.connect_and_send("I want to hack you")
"""
    with open("temp_mallory.py", "w", encoding='utf-8') as f: f.write(mallory_script)
    subprocess.call([sys.executable, "temp_mallory.py"])

    # 清理
    print_banner("测试结束，正在清理环境...")
    ca_process.terminate()
    tcp_server_process.terminate()
    if os.path.exists("temp_alice.py"): os.remove("temp_alice.py")
    if os.path.exists("temp_mallory.py"): os.remove("temp_mallory.py")
    print("✅ 演示完成")

if __name__ == "__main__":
    if not os.path.exists("secure_comm_lib.py"):
        print("❌ 错误：请在 Experiment_2 目录下运行 test.py")
    else:
        run_test()