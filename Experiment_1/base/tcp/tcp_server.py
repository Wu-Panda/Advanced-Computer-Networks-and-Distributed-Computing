#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TCP 服务器（多线程版）
1. 在本机指定端口上监听 TCP 连接
2. 接收客户端发送的一条或多条消息
3. 打印客户端地址和消息内容
4. 把收到的消息回显给客户端（简单回声服务器）
5. 支持多个客户端并发（用线程处理）
"""

import socket
import threading

HOST = "0.0.0.0"  # 监听所有网卡
PORT = 50000       # 服务器端口，可自行修改


def handle_client(conn: socket.socket, addr):
    """处理单个客户端连接的函数（运行在独立线程中）"""
    print(f"[连接建立] 客户端 {addr} 已连接")

    # 基础：循环收发数据，直到客户端主动断开或发送空数据
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"[连接关闭] 客户端 {addr} 已断开")
                break

            text = data.decode("utf-8", errors="ignore")
            print(f"[收到] 来自 {addr} 的消息：{text}")

            # 进阶示例：在回显前加上服务器前缀
            reply = f"服务器已收到：{text}"
            conn.sendall(reply.encode("utf-8"))
    except ConnectionResetError:
        print(f"[异常] 客户端 {addr} 异常断开连接")
    finally:
        conn.close()


def main():
    # 1. 创建 TCP 套接字（AF_INET：IPv4，SOCK_STREAM：TCP）
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 2. 允许端口复用（避免程序异常退出后端口短时间内处于 TIME_WAIT）
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 3. 绑定 IP 和端口
    server_socket.bind((HOST, PORT))

    # 4. 开始监听，并设置等待队列长度
    server_socket.listen(5)
    print(f"[启动] TCP 服务器启动成功，监听 {HOST}:{PORT}")

    # 5. 主循环：接受新的客户端连接
    while True:
        conn, addr = server_socket.accept()
        # 为每一个新连接创建一个线程进行处理
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()
        print(f"[线程] 为客户端 {addr} 启动处理线程 {t.name}")


if __name__ == "__main__":
    main()
