#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UDP 客户端
1. 创建 UDP 套接字
2. 使用 sendto() 向服务器发送数据
3. 使用 recvfrom() 接收服务器响应并打印
4. 支持循环发送，输入 exit/quit 退出
"""

import socket

SERVER_HOST = "127.0.0.1"  # UDP 服务器地址
SERVER_PORT = 50000        # UDP 服务器端口，应与 udp_server 一致


def main():
    # 1. 创建 UDP 套接字
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 可选进阶：设置超时（例如 5 秒）
    # udp_socket.settimeout(5)

    print(f"[信息] 已创建 UDP 客户端，将向 {SERVER_HOST}:{SERVER_PORT} 发送数据")

    while True:
        msg = input("请输入要发送的内容（输入 exit/quit 退出）：").strip()
        if msg.lower() in ("exit", "quit"):
            print("[信息] 退出 UDP 客户端")
            break

        if not msg:
            print("[提示] 不能发送空消息")
            continue

        # 2. 发送数据到服务器
        udp_socket.sendto(msg.encode("utf-8"), (SERVER_HOST, SERVER_PORT))

        try:
            # 3. 接收服务器响应
            data, addr = udp_socket.recvfrom(1024)
            print(f"[服务器 {addr} 回复] {data.decode('utf-8', errors='ignore')}")
        except socket.timeout:
            # 如果设置了超时，则可以看到这个分支
            print("[警告] 等待服务器响应超时（可能丢包或服务器未响应）")

    udp_socket.close()


if __name__ == "__main__":
    main()
