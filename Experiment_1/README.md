# 实验一：网络与传输层示例

本目录包含使用 Python 标准库实现的 TCP/UDP 基础示例，以及一个基于 Tkinter 的可视化工具，便于在本机快速体验连接、收发与往返时延（RTT）的基础行为。

## 环境要求
- 操作系统：Windows、macOS 或 Linux 均可
- Python：3.8 及以上版本（建议 3.10+）
- 依赖：全部为标准库，无第三方依赖
  - `socket`、`threading`、`time`、`sys`、`subprocess`、`pathlib`
  - GUI 可视化使用 `tkinter`（macOS/Linux 若缺失需安装系统包：如 Debian/Ubuntu `sudo apt-get install python3-tk`）
- 端口：默认使用 `50000`，如被占用可修改对应脚本中的端口常量
- 防火墙：首次监听/连接本机端口时，系统可能提示放行，请选择允许

## 目录结构
```
Experiment_1/
├─ base/
│  ├─ tcp/
│  │  ├─ tcp_server.py      # 多线程 TCP 回显服务器
│  │  └─ tcp_client.py      # 交互式 TCP 客户端
│  └─ udp/
│     ├─ udp_server.py      # UDP 回显服务器（将消息转为大写再回传）
│     └─ udp_client.py      # 交互式 UDP 客户端
└─ advanced/
   └─ visual.py             # Tkinter 可视化：启动/停止服务、发送消息、统计字节与平均 RTT
```

## 快速开始
- 进入本目录后，使用系统自带 Python 解释器运行脚本（Windows 可用 `python` 或 `py`）。

### TCP 示例
1) 启动服务器（监听所有网卡 `0.0.0.0:50000`）：
```
python base/tcp/tcp_server.py
```
2) 启动客户端并与服务器交互（默认连接 `127.0.0.1:50000`）：
```
python base/tcp/tcp_client.py
```
- 在客户端中输入消息后，服务器会回显，输入 `exit` 或 `quit` 退出。

### UDP 示例
1) 启动服务器（监听 `0.0.0.0:50000`）：
```
python base/udp/udp_server.py
```
2) 启动客户端（默认向 `127.0.0.1:50000` 发送）：
```
python base/udp/udp_client.py
```
- 客户端输入内容后，服务器将以“大写回显”的形式返回；输入 `exit` 或 `quit` 退出。

### 可视化工具（推荐）
运行 Tkinter 可视化界面，一站式体验 TCP/UDP：
```
python advanced/visual.py
```
- TCP 页签：
  - 启动/停止服务器（内部以子进程运行 `base/tcp/tcp_server.py`）
  - 启动/停止客户端、发送消息、查看日志和统计
- UDP 页签：
  - 启动/停止服务器（内部以子进程运行 `base/udp/udp_server.py`）
  - 启动/停止客户端、发送消息、查看日志和统计
- 指标展示：消息数量、发送/接收字节数、平均 RTT（单位 ms）
- 地址与端口默认分别为 `127.0.0.1` 与 `50000`，可在界面中修改

## 配置说明
- 端口修改：
  - TCP 服务器端口在 `base/tcp/tcp_server.py` 顶部常量 `PORT` 中设置
  - UDP 服务器端口在 `base/udp/udp_server.py` 顶部常量 `PORT` 中设置
  - 客户端默认目标端口在对应 `tcp_client.py`、`udp_client.py` 的常量中设置
- 地址修改：
  - 客户端脚本默认连接 `127.0.0.1`，可改为局域网服务器 IP
  - 可视化界面支持直接在输入框修改地址与端口

## 常见问题
- 连接失败/被拒绝：确认服务器已启动、端口未被占用、客户端地址/端口一致
- 防火墙拦截：允许 Python 监听与访问本地网络端口
- Tkinter 缺失：在部分 Linux 发行版上需安装 `python3-tk`

## 文件说明
- `base/tcp/tcp_server.py`：多线程 TCP 回显服务器，接受消息后以“服务器已收到：{text}”形式回显
- `base/tcp/tcp_client.py`：交互式 TCP 客户端，支持循环输入与退出指令
- `base/udp/udp_server.py`：UDP 回显服务器，接收消息后转换为大写并回发
- `base/udp/udp_client.py`：交互式 UDP 客户端，支持循环输入与退出指令
- `advanced/visual.py`：图形化可视化工具，集成 TCP/UDP 服务启动、客户端发送与统计展示

## 备注
- 所有示例为作业用途，未做复杂异常处理与安全加固；请勿直接用于生产环境
- 若在同一台机器上同时运行 TCP 与 UDP 服务器且端口相同，一般可行；如端口冲突或策略限制，建议分配不同端口