import socket
import threading
import time
import sys
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk


class VisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP/UDP Visualizer")
        self.root.geometry("1060x720")
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        self._setup_theme(style)
        self.tcp_socket = None
        self.tcp_connected = False
        self.tcp_bytes_sent = 0
        self.tcp_bytes_recv = 0
        self.tcp_msg_count = 0
        self.tcp_rtts = []
        self.tcp_server_proc = None
        self.tcp_server_running = False
        self.udp_bytes_sent = 0
        self.udp_bytes_recv = 0
        self.udp_msg_count = 0
        self.udp_rtts = []
        self.udp_socket = None
        self.udp_client_started = False
        self.udp_server_proc = None
        self.udp_server_running = False
        self.project_root = Path(__file__).resolve().parent.parent
        self.base_dir = self.project_root / "base"
        self._build_ui()

    def _setup_theme(self, style: ttk.Style):
        bg = "#f5f5f7"
        surface = "#ffffff"
        border = "#d1d1d6"
        text = "#1d1d1f"
        muted = "#6e6e73"
        primary = "#0a84ff"
        self.root.configure(bg=bg)
        style.configure("TFrame", background=bg)
        style.configure("Card.TFrame", background=surface, borderwidth=1, relief="solid")
        style.configure("TLabel", background=bg, foreground=text)
        style.configure("Muted.TLabel", background=bg, foreground=muted)
        style.configure("Section.TLabelframe", background=bg, foreground=text)
        style.configure("Section.TLabelframe.Label", background=bg, foreground=text)
        style.configure("Accent.TButton", background=primary, foreground="#ffffff")
        style.map("Accent.TButton", background=[("active", "#0069d9")])
        style.configure("TButton", background=surface, foreground=text)
        style.map("TButton", background=[("active", "#ededf0")])
        style.configure("Segmented.TButton", background=surface, foreground=text)
        style.configure("Segmented.Selected.TButton", background=primary, foreground="#ffffff")
        style.configure("TEntry", fieldbackground=surface, foreground=text)
        style.configure("Entry", fieldbackground=surface, foreground=text)

    def _build_ui(self):
        header = ttk.Frame(self.root, style="TFrame")
        ttk.Label(header, text="Network", font=("Segoe UI", 20, "bold")).pack(side=tk.LEFT, padx=16, pady=14)
        ttk.Label(header, text="Transport Visualizer", style="Muted.TLabel", font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=8)
        header.pack(fill=tk.X)

        seg = ttk.Frame(self.root, style="TFrame")
        self._seg_tcp_btn = ttk.Button(seg, text="TCP", style="Segmented.Selected.TButton", command=lambda: self._show_page("tcp"))
        self._seg_udp_btn = ttk.Button(seg, text="UDP", style="Segmented.TButton", command=lambda: self._show_page("udp"))
        self._seg_tcp_btn.pack(side=tk.LEFT, padx=(16, 0), pady=8)
        self._seg_udp_btn.pack(side=tk.LEFT, padx=(6, 0), pady=8)
        seg.pack(fill=tk.X)

        pages = ttk.Frame(self.root, style="TFrame")
        pages.pack(fill=tk.BOTH, expand=True)
        tcp_frame = ttk.Frame(pages, style="TFrame")
        udp_frame = ttk.Frame(pages, style="TFrame")
        self._page_tcp = tcp_frame
        self._page_udp = udp_frame

        self.tcp_host_var = tk.StringVar(value="127.0.0.1")
        self.tcp_port_var = tk.StringVar(value="50000")
        self.tcp_status_var = tk.StringVar(value="未连接")
        self.tcp_metrics_var = tk.StringVar(value="消息:0 发送字节:0 接收字节:0 平均RTT:0ms")

        server_box_tcp = ttk.LabelFrame(tcp_frame, text="服务器控制", style="Section.TLabelframe")
        ttk.Button(server_box_tcp, text="启动服务器", command=self.tcp_server_start).grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(server_box_tcp, text="停止服务器", command=self.tcp_server_stop).grid(row=0, column=1, padx=4, pady=4)
        self.tcp_server_status_var = tk.StringVar(value="未运行")
        ttk.Label(server_box_tcp, textvariable=self.tcp_server_status_var, style="Muted.TLabel").grid(row=0, column=2, padx=8)
        server_box_tcp.pack(fill=tk.X, pady=6, padx=24)

        client_box_tcp = ttk.LabelFrame(tcp_frame, text="客户端控制", style="Section.TLabelframe")
        ttk.Label(client_box_tcp, text="地址").grid(row=0, column=0, sticky="w")
        ttk.Entry(client_box_tcp, textvariable=self.tcp_host_var, width=15).grid(row=0, column=1, padx=8)
        ttk.Label(client_box_tcp, text="端口").grid(row=0, column=2, sticky="w")
        ttk.Entry(client_box_tcp, textvariable=self.tcp_port_var, width=8).grid(row=0, column=3, padx=8)
        ttk.Button(client_box_tcp, text="启动客户端", command=self.tcp_connect, style="Accent.TButton").grid(row=0, column=4, padx=8)
        ttk.Button(client_box_tcp, text="停止客户端", command=self.tcp_disconnect).grid(row=0, column=5, padx=8)
        ttk.Label(client_box_tcp, textvariable=self.tcp_status_var, style="Muted.TLabel").grid(row=0, column=6, padx=8)
        client_box_tcp.pack(fill=tk.X, pady=6, padx=24)

        tcp_mid = ttk.Frame(tcp_frame)
        self.tcp_msg_var = tk.StringVar()
        ttk.Entry(tcp_mid, textvariable=self.tcp_msg_var, width=60).grid(row=0, column=0, padx=8)
        ttk.Button(tcp_mid, text="发送", command=self.tcp_send, style="Accent.TButton").grid(row=0, column=1, padx=8)
        ttk.Button(tcp_mid, text="清空日志", command=lambda: self._clear_text(self.tcp_text)).grid(row=0, column=2, padx=8)
        ttk.Label(tcp_mid, textvariable=self.tcp_metrics_var, style="Muted.TLabel").grid(row=0, column=3, padx=8)
        tcp_mid.pack(fill=tk.X, pady=6, padx=24)

        tcp_bottom = ttk.Frame(tcp_frame)
        log_wrap_tcp = ttk.Frame(tcp_bottom, style="Card.TFrame")
        self.tcp_text = tk.Text(log_wrap_tcp, height=18, bg="#ffffff", fg="#1d1d1f", insertbackground="#1d1d1f")
        tcp_scroll = ttk.Scrollbar(log_wrap_tcp, command=self.tcp_text.yview)
        self.tcp_text.configure(yscrollcommand=tcp_scroll.set)
        self.tcp_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tcp_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        log_wrap_tcp.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)
        tcp_bottom.pack(fill=tk.BOTH, expand=True)

        self.udp_host_var = tk.StringVar(value="127.0.0.1")
        self.udp_port_var = tk.StringVar(value="50000")
        self.udp_metrics_var = tk.StringVar(value="消息:0 发送字节:0 接收字节:0 平均RTT:0ms")

        server_box_udp = ttk.LabelFrame(udp_frame, text="服务器控制", style="Section.TLabelframe")
        ttk.Button(server_box_udp, text="启动服务器", command=self.udp_server_start).grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(server_box_udp, text="停止服务器", command=self.udp_server_stop).grid(row=0, column=1, padx=4, pady=4)
        self.udp_server_status_var = tk.StringVar(value="未运行")
        ttk.Label(server_box_udp, textvariable=self.udp_server_status_var, style="Muted.TLabel").grid(row=0, column=2, padx=8)
        server_box_udp.pack(fill=tk.X, pady=6, padx=24)

        client_box_udp = ttk.LabelFrame(udp_frame, text="客户端控制", style="Section.TLabelframe")
        ttk.Label(client_box_udp, text="地址").grid(row=0, column=0, sticky="w")
        ttk.Entry(client_box_udp, textvariable=self.udp_host_var, width=15).grid(row=0, column=1, padx=8)
        ttk.Label(client_box_udp, text="端口").grid(row=0, column=2, sticky="w")
        ttk.Entry(client_box_udp, textvariable=self.udp_port_var, width=8).grid(row=0, column=3, padx=8)
        ttk.Button(client_box_udp, text="启动客户端", command=self.udp_client_start, style="Accent.TButton").grid(row=0, column=4, padx=4)
        ttk.Button(client_box_udp, text="停止客户端", command=self.udp_client_stop).grid(row=0, column=5, padx=4)
        client_box_udp.pack(fill=tk.X, pady=6, padx=24)

        udp_mid = ttk.Frame(udp_frame)
        self.udp_msg_var = tk.StringVar()
        ttk.Entry(udp_mid, textvariable=self.udp_msg_var, width=60).grid(row=0, column=0, padx=8)
        ttk.Button(udp_mid, text="发送", command=self.udp_send, style="Accent.TButton").grid(row=0, column=1, padx=8)
        ttk.Button(udp_mid, text="清空日志", command=lambda: self._clear_text(self.udp_text)).grid(row=0, column=2, padx=8)
        ttk.Label(udp_mid, textvariable=self.udp_metrics_var, style="Muted.TLabel").grid(row=0, column=3, padx=8)
        udp_mid.pack(fill=tk.X, pady=6, padx=24)

        udp_bottom = ttk.Frame(udp_frame)
        log_wrap_udp = ttk.Frame(udp_bottom, style="Card.TFrame")
        self.udp_text = tk.Text(log_wrap_udp, height=18, bg="#ffffff", fg="#1d1d1f", insertbackground="#1d1d1f")
        udp_scroll = ttk.Scrollbar(log_wrap_udp, command=self.udp_text.yview)
        self.udp_text.configure(yscrollcommand=udp_scroll.set)
        self.udp_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        udp_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        log_wrap_udp.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)
        udp_bottom.pack(fill=tk.BOTH, expand=True)

        self._page_tcp.pack(fill=tk.BOTH, expand=True)
        self._page_udp.pack_forget()

        # 去除定时重绘：不展示 RTT 图

    def _show_page(self, key: str):
        if key == "tcp":
            self._page_udp.pack_forget()
            self._page_tcp.pack(fill=tk.BOTH, expand=True)
            self._seg_tcp_btn.configure(style="Segmented.Selected.TButton")
            self._seg_udp_btn.configure(style="Segmented.TButton")
        else:
            self._page_tcp.pack_forget()
            self._page_udp.pack(fill=tk.BOTH, expand=True)
            self._seg_tcp_btn.configure(style="Segmented.TButton")
            self._seg_udp_btn.configure(style="Segmented.Selected.TButton")

    def _update_tcp_metrics(self):
        avg = int(sum(self.tcp_rtts) / len(self.tcp_rtts)) if self.tcp_rtts else 0
        self.tcp_metrics_var.set(f"消息:{self.tcp_msg_count} 发送字节:{self.tcp_bytes_sent} 接收字节:{self.tcp_bytes_recv} 平均RTT:{avg}ms")

    def _update_udp_metrics(self):
        avg = int(sum(self.udp_rtts) / len(self.udp_rtts)) if self.udp_rtts else 0
        self.udp_metrics_var.set(f"消息:{self.udp_msg_count} 发送字节:{self.udp_bytes_sent} 接收字节:{self.udp_bytes_recv} 平均RTT:{avg}ms")

    # 已移除 RTT 绘制与重绘函数

    def _clear_text(self, widget):
        widget.delete("1.0", tk.END)

    def tcp_connect(self):
        if self.tcp_connected:
            return
        host = self.tcp_host_var.get().strip()
        try:
            port = int(self.tcp_port_var.get().strip())
        except Exception:
            self.tcp_text.insert(tk.END, "端口无效\n")
            return
        def run():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, port))
                self.tcp_socket = s
                self.tcp_connected = True
                self.tcp_status_var.set("已连接")
                self.tcp_text.insert(tk.END, f"连接到 {host}:{port}\n")
            except Exception as e:
                self.tcp_text.insert(tk.END, f"连接失败: {e}\n")
        threading.Thread(target=run, daemon=True).start()

    def tcp_disconnect(self):
        if self.tcp_socket:
            try:
                self.tcp_socket.close()
            except Exception:
                pass
        self.tcp_socket = None
        self.tcp_connected = False
        self.tcp_status_var.set("未连接")
        self.tcp_text.insert(tk.END, "已断开\n")

    def tcp_send(self):
        msg = self.tcp_msg_var.get().strip()
        if not msg:
            return
        if not self.tcp_connected or not self.tcp_socket:
            self.tcp_text.insert(tk.END, "未连接\n")
            return
        def run():
            try:
                start = time.time()
                data = msg.encode("utf-8")
                self.tcp_socket.sendall(data)
                self.tcp_bytes_sent += len(data)
                resp = self.tcp_socket.recv(4096)
                end = time.time()
                if resp:
                    self.tcp_bytes_recv += len(resp)
                    rtt = int((end - start) * 1000)
                    self.tcp_rtts.append(rtt)
                    if len(self.tcp_rtts) > 200:
                        self.tcp_rtts = self.tcp_rtts[-200:]
                    self.tcp_msg_count += 1
                    self._update_tcp_metrics()
                    self.tcp_text.insert(tk.END, f"发送:{msg}\n")
                    self.tcp_text.insert(tk.END, f"回复:{resp.decode('utf-8', errors='ignore')} RTT:{rtt}ms\n")
                else:
                    self.tcp_text.insert(tk.END, "连接关闭\n")
                    self.tcp_disconnect()
            except Exception as e:
                self.tcp_text.insert(tk.END, f"异常:{e}\n")
        threading.Thread(target=run, daemon=True).start()

    def tcp_server_start(self):
        if self.tcp_server_running:
            return
        tcp_server_path = self.base_dir / "tcp" / "tcp_server.py"
        if not tcp_server_path.exists():
            self.tcp_text.insert(tk.END, f"找不到服务器脚本: {tcp_server_path}\n")
            return
        def run():
            try:
                proc = subprocess.Popen([sys.executable, str(tcp_server_path)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                self.tcp_server_proc = proc
                self.tcp_server_running = True
                self.tcp_server_status_var.set("运行中")
                self.tcp_text.insert(tk.END, f"已启动TCP服务器: {tcp_server_path}\n")
                def reader():
                    try:
                        for line in proc.stdout:
                            self.tcp_text.insert(tk.END, line)
                    except Exception:
                        pass
                threading.Thread(target=reader, daemon=True).start()
            except Exception as e:
                self.tcp_text.insert(tk.END, f"启动失败: {e}\n")
        threading.Thread(target=run, daemon=True).start()

    def tcp_server_stop(self):
        if self.tcp_server_proc and self.tcp_server_running:
            try:
                self.tcp_server_proc.terminate()
            except Exception:
                pass
        self.tcp_server_proc = None
        self.tcp_server_running = False
        self.tcp_server_status_var.set("未运行")
        self.tcp_text.insert(tk.END, "TCP服务器已停止\n")

    def udp_send(self):
        msg = self.udp_msg_var.get().strip()
        if not msg:
            return
        host = self.udp_host_var.get().strip()
        try:
            port = int(self.udp_port_var.get().strip())
        except Exception:
            self.udp_text.insert(tk.END, "端口无效\n")
            return
        if not self.udp_client_started or not self.udp_socket:
            self.udp_text.insert(tk.END, "UDP客户端未启动\n")
            return
        def run():
            try:
                start = time.time()
                data = msg.encode("utf-8")
                self.udp_socket.settimeout(3)
                self.udp_socket.sendto(data, (host, port))
                self.udp_bytes_sent += len(data)
                try:
                    resp, addr = self.udp_socket.recvfrom(4096)
                    end = time.time()
                    self.udp_bytes_recv += len(resp)
                    rtt = int((end - start) * 1000)
                    self.udp_rtts.append(rtt)
                    if len(self.udp_rtts) > 200:
                        self.udp_rtts = self.udp_rtts[-200:]
                    self.udp_msg_count += 1
                    self._update_udp_metrics()
                    self.udp_text.insert(tk.END, f"发送:{msg}\n")
                    self.udp_text.insert(tk.END, f"回复:{resp.decode('utf-8', errors='ignore')} RTT:{rtt}ms\n")
                except socket.timeout:
                    self.udp_text.insert(tk.END, "超时\n")
            except Exception as e:
                self.udp_text.insert(tk.END, f"异常:{e}\n")
        threading.Thread(target=run, daemon=True).start()

    def udp_client_start(self):
        if self.udp_client_started:
            return
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket = s
            self.udp_client_started = True
            self.udp_text.insert(tk.END, "UDP客户端已启动\n")
        except Exception as e:
            self.udp_text.insert(tk.END, f"UDP客户端启动失败: {e}\n")

    def udp_client_stop(self):
        if self.udp_socket:
            try:
                self.udp_socket.close()
            except Exception:
                pass
        self.udp_socket = None
        self.udp_client_started = False
        self.udp_text.insert(tk.END, "UDP客户端已停止\n")

    def udp_server_start(self):
        if self.udp_server_running:
            return
        udp_server_path = self.base_dir / "udp" / "udp_server.py"
        if not udp_server_path.exists():
            self.udp_text.insert(tk.END, f"找不到服务器脚本: {udp_server_path}\n")
            return
        def run():
            try:
                proc = subprocess.Popen([sys.executable, str(udp_server_path)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                self.udp_server_proc = proc
                self.udp_server_running = True
                self.udp_server_status_var.set("运行中")
                self.udp_text.insert(tk.END, f"已启动UDP服务器: {udp_server_path}\n")
                def reader():
                    try:
                        for line in proc.stdout:
                            self.udp_text.insert(tk.END, line)
                    except Exception:
                        pass
                threading.Thread(target=reader, daemon=True).start()
            except Exception as e:
                self.udp_text.insert(tk.END, f"启动失败: {e}\n")
        threading.Thread(target=run, daemon=True).start()

    def udp_server_stop(self):
        if self.udp_server_proc and self.udp_server_running:
            try:
                self.udp_server_proc.terminate()
            except Exception:
                pass
        self.udp_server_proc = None
        self.udp_server_running = False
        self.udp_server_status_var.set("未运行")
        self.udp_text.insert(tk.END, "UDP服务器已停止\n")


def main():
    root = tk.Tk()
    app = VisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()