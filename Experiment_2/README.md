# 实验二：安全通信编程基础 (基于 PGP 架构)

本目录包含“安全通信编程基础”实验的完整代码实现。本项目模拟了一个基于 **PGP (Pretty Good Privacy)** 架构的安全通信系统，集成了 RSA 非对称加密、DES 对称加密、MD5 消息摘要以及数字证书认证机制。

特别地，本项目演示了 **中间人嗅探（密文传输）** 和 **黑客伪造证书攻击（CA 防御）** 的完整攻防场景。

## 1\. 实验内容与技术架构

本项目旨在解决传统 TCP 通信明文传输的不安全性，通过以下机制实现机密性、完整性和身份认证：

  * **混合加密体制**：
      * **RSA (2048位)**：用于密钥交换和数字签名。利用公钥加密 DES 会话密钥，利用私钥进行数字签名。
      * **DES (CBC模式)**：用于通信数据的实际加密。由于 RSA 速度较慢，数据传输阶段使用效率更高的 DES 对称加密。
  * **身份认证与完整性**：
      * **数字证书 (Certificate)**：模拟 CA (Certificate Authority) 中心，对用户公钥进行签名，防止黑客伪造身份。
      * **MD5 摘要**：用于端点鉴别（Endpoint Authentication），验证通信双方身份及数据完整性。
  * **编码转换**：
      * **Base64**：确保加密后的二进制数据在网络传输中的兼容性。

## 2\. 环境依赖

本项目依赖 Python 3.8+ 及以下第三方加密库，请在使用前安装：

```bash
pip install pyDes pycryptodome
```

> **注意**：
>
>   * `pyDes`: 用于 DES 对称加密实现。
>   * `pycryptodome`: `Crypto` 库的现代维护版本，提供 RSA、SHA256 和 MD5 算法支持。

## 3\. 目录结构 (初始状态)

```text
Experiment_2/
├── secure_comm_lib.py      # [核心] 安全通信库：封装 RSA, DES, MD5, Base64 操作
├── test.py                 # [测试] 集成攻防演示脚本：自动运行合法用户与黑客攻击场景
├── udp/
│   ├── udp_server.py       # [CA中心] 负责接收公钥，颁发数字证书
│   └── udp_client.py       # [证书模块] TCP客户端自动调用此模块向 CA 申请证书
└── tcp/
    ├── tcp_server.py       # [安全服务器] 验证证书有效性，拦截黑客，解密 DES 密钥
    └── tcp_client.py       # [安全客户端] 支持合法连接与“黑客模式”，展示密文传输
```

> **运行后生成的文件**：
> 程序首次运行后，会自动在根目录下生成以下文件夹以存储密钥和证书：
>
>   * `ca_keys/`：存放 CA 中心的私钥和公钥。
>   * `server_data/`：存放 TCP 服务器的私钥和公钥。
>   * `client_keys/`：存放客户端生成的密钥对以及申请到的数字证书。

## 4\. 快速开始 (推荐)

本项目提供了一个集成测试脚本，可一键启动所有组件，并像“播放电影”一样演示**合法通信**与**黑客攻击**两个场景。

在 `Experiment_2` 目录下运行：

```bash
python test.py
```

**演示流程说明：**

1.  **基础设施启动**：自动启动 UDP CA 服务器和 TCP 安全服务器。
2.  **场景一：合法用户 (Alice)**
      * Alice 自动向 CA 申请证书。
      * Alice 连接服务器，服务器验证证书通过。
      * **密文演示**：控制台将打印出 DES 加密后的乱码（模拟网络嗅探），证明传输是安全的。
3.  **场景二：黑客攻击 (Mallory)**
      * 黑客 Mallory 伪造了一份证书（未经过 CA 签名）。
      * Mallory 尝试连接服务器。
      * **防御演示**：服务器检测到签名无效，拒绝连接并断开，保护系统安全。

## 5\. 手动运行步骤

若需分别观察各组件运行情况或进行单步调试，请打开三个终端窗口，按以下顺序执行：

### 第一步：启动 CA 中心 (UDP)

CA 中心启动后将监听 `50001` 端口，等待颁发证书。

```bash
# 终端 1
python udp/udp_server.py
```

### 第二步：启动安全服务器 (TCP)

服务器启动后监听 `50000` 端口。它会加载 CA 的公钥，用于验证后续连接者的身份。

```bash
# 终端 2
python tcp/tcp_server.py
```

### 第三步：启动客户端 (TCP)

客户端启动时，会自动检查本地是否有证书。若无，它会先通过 UDP 协议联系 CA 申请，然后再通过 TCP 协议连接文件服务器。

```bash
# 终端 3
python tcp/tcp_client.py
```

## 6\. 通信协议流程详解

代码实现了符合 PDF 要求的严格握手协议：

1.  **证书颁发阶段 (UDP)**

      * Client $\rightarrow$ CA: `{User_ID, Public_Key}`
      * CA $\rightarrow$ Client: `Sign_RSA_Priv(Public_Key)` (即数字证书)

2.  **安全握手阶段 (TCP)**

      * **Server Hello**: 发送 `Server_Public_Key`。
      * **Client Key Exchange**:
          * 生成临时 `DES_Key`。
          * 发送 `{Client_Public_Key, Certificate, Encrypt_RSA(DES_Key)}`。
      * **Server Verification**:
          * 使用 CA 公钥验证 `Certificate`，确认 `Client_Public_Key` 是否合法。
          * **安全检查**：若验证失败（如黑客攻击），直接断开连接。
          * 若验证成功，使用 Server 私钥解密得到 `DES_Key`。

3.  **身份鉴别阶段**

      * Server 发送随机字符串 (Challenge)。
      * Client 返回该字符串的 MD5 摘要。
      * Server 验证 MD5 摘要一致性。

4.  **数据传输阶段**

      * 所有后续应用层数据均使用 `DES_Key` 进行 CBC 模式加密传输，并在控制台展示密文形式。

-----

**备注**：所有密钥文件（`.pem`）和证书文件（`.sig`）均在运行时自动生成。若需重置环境，直接删除 `*_keys/` 和 `server_data/` 文件夹即可。