#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TCP 客户端
1. 连接到指定的 TCP 服务器
2. 发送一条或多条消息
3. 接收服务器返回的数据并打印
4. 用户输入 "exit" / "quit" 可退出客户端
"""

import socket

SERVER_HOST = "127.0.0.1"  # 默认连接本机
SERVER_PORT = 50000        # 需和服务器保持一致


def main():
    # 1. 创建 TCP 套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 2. 连接到服务器
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"[连接] 已连接到服务器 {SERVER_HOST}:{SERVER_PORT}")

        # 3. 交互式发送消息
        while True:
            msg = input("请输入要发送的内容（输入 exit/quit 退出）：").strip()
            if msg.lower() in ("exit", "quit"):
                print("[信息] 退出客户端")
                break

            if not msg:
                print("[提示] 不能发送空消息")
                continue

            # 发送数据
            client_socket.sendall(msg.encode("utf-8"))

            # 接收服务器回显的数据
            data = client_socket.recv(1024)
            if not data:
                print("[信息] 服务器已关闭连接")
                break

            print(f"[服务器回复] {data.decode('utf-8', errors='ignore')}")

    except ConnectionRefusedError:
        print("[错误] 无法连接到服务器，请确认服务器已启动且地址/端口正确")
    except Exception as e:
        print(f"[异常] {e}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
