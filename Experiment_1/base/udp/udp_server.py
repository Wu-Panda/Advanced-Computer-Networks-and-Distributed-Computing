#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UDP 服务器
1. 在指定端口上创建 UDP 套接字并绑定
2. 通过 recvfrom() 接收客户端数据
3. 打印客户端地址和接收到的消息
4. 把消息处理后（转大写）再通过 sendto() 发回客户端
"""

import socket

HOST = "0.0.0.0"  # 接收所有网卡上的数据
PORT = 50000       # UDP 端口，可与 TCP 共用，也可分开


def main():
    # 1. 创建 UDP 套接字（SOCK_DGRAM）
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 2. 绑定 IP 和端口
    udp_socket.bind((HOST, PORT))
    print(f"[启动] UDP 服务器启动成功，监听 {HOST}:{PORT}")

    # 3. 循环接收来自客户端的数据
    while True:
        data, addr = udp_socket.recvfrom(1024)  # data: bytes, addr: (ip, port)
        text = data.decode("utf-8", errors="ignore")
        print(f"[收到] 来自 {addr} 的消息：{text}")

        # 简单处理：转成大写再发回去
        reply = f"UDP 回显（大写）：{text.upper()}"
        udp_socket.sendto(reply.encode("utf-8"), addr)


if __name__ == "__main__":
    main()
