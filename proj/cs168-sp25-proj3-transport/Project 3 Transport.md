# 项目 3：传输层

在本项目中，你将实现 TCP 协议的一个子集。你的实现将提供可靠性，但不包含拥塞控制。

完成本项目所需的课程内容：第 10 讲（传输层 1：TCP）、第 11 讲（传输层 2：TCP II）。

你可以独自完成本项目，也可以与一名搭档合作。你可以与之前项目的搭档继续合作，也可以选择新的搭档。提醒：[我们的课程政策页面有合作政策](https://su25.cs168.io/policies)，你必须遵守。

## 环境设置

### 操作系统安装

本项目已在 Linux 和 Mac 系统上测试通过。

如果你使用 Windows 系统，需要安装 Windows Subsystem for Linux（WSL）。WSL 是一个允许你在 Windows 上直接运行 Linux 环境的工具。安装 WSL 的步骤如下：



1. 以管理员身份打开 PowerShell，运行`wsl --install`。这将安装 Ubuntu 发行版。出现提示时，重启计算机。

2. 从开始菜单打开 Ubuntu 终端。它会提示你选择用户名和密码。选择你喜欢的即可，并记住它们。

如果安装成功，你会在终端中看到`username@hostname:~$`。如果你使用 VSCode，可以点击左下角的 “><” 箭头，选择 “连接到 WSL” 以打开 Linux 环境。其他代码编辑器可能也有连接到 WSL 的选项。

### （Windows 用户）文件位置注意事项

下载 starter 代码（见下文）后，不要在位于 Windows 文件系统（`/mnt/c`下的文件）上运行 Linux 命令。这可能会非常慢，因为你是在 Windows 磁盘上运行 Linux 命令。相反：



1. 使用`mkdir -p ~/projects`在你的 WSL 主目录中创建一个项目目录。

2. 使用`cp -r /mnt/c/Users/<username>/Downloads/cs168-su25-proj3-transport ~/projects/`将解压后的 starter 代码复制到`~/projects`。如果你使用 VSCode，也可以将文件夹拖到资源管理器侧边栏标签中。

3. 在终端中使用`cd ~/projects/cs168-su25-proj3-transport`导航到该文件夹并在其中工作。

### Python 安装

本项目已在 Python 3.7 上测试通过。（它可能也适用于更新版本的 Python，但使用风险自负。）

如果你在终端中运行`python3 --version`或`python --version`，看到类似`Python 3.7.*`的输出，说明已经准备就绪。

### Starter 代码

[在此处下载 starter 代码副本。](https://su25.cs168.io/assets/projects/proj3/cs168-su25-proj3-transport.zip)

在终端中，使用`cd`导航到`cs168-su25-proj3-transport/ext/cs168p2`目录。所有 Python 命令都应从该目录运行。

首先，运行以下命令为 Python 文件赋予可执行权限：



```
chmod +x ../../pox.py
```

要检查设置是否正常，在终端中运行：



```
python ../../pox.py config=tests/sanity\_test.cfg
```

如果看到以下消息，则说明所有设置都正确：



```
\[test] \[00:00:02] All checks passed, test PASSED
```

你只需要编辑`ext/cs168p2/``student_socket.py`。其中有明确的注释指示你应该填写代码的位置。

指导原则：



* 不要修改任何其他文件。

* 不要添加任何新文件。

* 不要添加任何导入语句。

* 不要编辑注释指示部分之外的代码。

* 不要添加任何硬编码的全局变量。

* 添加辅助方法是允许的。

* 一般来说，如果我们没有告诉你要使用某个东西，你可能不需要它。我们的目标不是为难你！

### 新规范说明

注意：本规范已为 2024 年秋季学期重写，更加清晰并提供了一些额外提示。可能包含错误。

[如果你想使用之前版本的规范，可以在此处找到。](https://sp24.cs168.io/assets/projects/transport3.pdf)

## 项目概述

本项目分为 9 个阶段。



* 在项目 3A 中，你需要完成阶段 1-5。

* 在项目 3B 中，你需要完成阶段 6-9。

每个阶段都有自己的单元测试，本地提供给你。你的成绩将仅由这些单元测试决定（没有隐藏测试）。

要运行单元测试，请导航到`cs168-su25-proj3-transport/ext/cs168p2`，并运行以下命令之一，将 5 替换为你要测试的阶段编号：



```
python autograder.py s5  # 运行阶段5的单元测试。

python autograder.py all  # 运行所有单元测试。

python autograder.py all 5  # 运行到第5阶段（含）的所有单元测试。
```

如果测试失败，你会看到类似以下的输出：



```
test\_s1\_t1 (\_\_main\_\_.test\_s1\_t1.test\_s1\_t1) ...&#x20;

&#x20;   Running test: ./tests/s1\_t1.cfg

&#x20;   Tracefile: ./trace/s1\_t1/2024-08-22T16:09:52.593234

../../pox.py config=./tests/s1\_t1.cfg tcpip.pcap --node=r1 --no-tx --filename=./trace/s1\_t1/2024-08-22T16:09:52.593234

FAIL
```

要查看该特定测试的格式化输出，请取失败前的最后一行，去掉`--filename`参数，在终端中运行该命令：



```
../../pox.py config=./tests/s1\_t1.cfg tcpip.pcap --node=r1 --no-tx
```

## 代码概述

你将在`student_socket.py`中实现`StudentUSocket`类，它代表一个 TCP 套接字。

`student_socket.py`还包含其他有用的方法，我们将在下面描述。

### 模运算

序列号是 32 位的，并且可以环绕（例如，`0xFFFFFFFF + 1 = 0x00000000`）。

当你对序列号执行算术运算时，请使用以下运算符：

| 模运算（使用这个） | 操作     | 算术等效（不要使用这个） |
| ------------------ | -------- | ------------------------ |
| A = A \|PLUS\| 1   | 加法     | A = A + 1                |
| C = A \|MINUS\| B  | 减法     | C = A - B                |
| if (A \|EQ\| B)    | 等于     | if (A == B)              |
| if (A \|NE\| B)    | 不等于   | if (A != B)              |
| if (A \|GT\| B)    | 大于     | if (A > B)               |
| if (A \|GE\| B)    | 大于等于 | if (A >= B)              |
| if (A \|LT\| B)    | 小于     | if (A < B)               |
| if (A \|LE\| B)    | 小于等于 | if (A <= B)              |

实例变量`self.state`记录当前 TCP 连接的状态。

`self.state`始终被赋值为以下列表中的一个值：



```
\[CLOSED, LISTEN, SYN\_RECEIVED, ESTABLISHED, SYN\_SENT, FIN\_WAIT\_1, FIN\_WAIT\_2, CLOSING, TIME\_WAIT, CLOSE\_WAIT, LAST\_ACK]
```

我们将在规范中出现相关状态时详细描述每个状态。

### 发送序列空间：TXControlBlock

实例变量`self.tx_data`是一个字节数组，表示你要发送的数据。用户会向该数组的末尾追加字节，而你会在发送时从数组的前端移除字节。

实例变量`self.snd`是一个`TXControlBlock`对象，包含关于你正在发送的出站字节流的信息。

`TXControlBlock`对象有以下相关实例变量：



* `self.snd.iss`：你的初始序列号。

* `self.snd.una`：你发送的最旧的未被确认的序列号。

* `self.snd.nxt`：你应该发送的下一个序列号。

* `self.snd.wnd`：当前发送窗口的大小，由对方（接收方）剩余的缓冲区空间决定。

下图显示了你正在发送的字节流以及这些实例变量的含义：



![TCP发送窗口。snd.una之前的是已发送且已确认的。snd.una到snd.nxt之间的是已发送但未确认的。snd.nxt到snd.una + snd.wnd之间的是未发送但可以发送的。snd.una + snd.wnd之后的是未发送且不能发送的。](https://su25.cs168.io/assets/projects/proj3/send-window.svg)

### 接收序列空间：RXControlBlock

实例变量`self.rx_data`是一个字节数组，表示你正在接收的数据。当你收到数据包时，你应该将它们的有效载荷（按正确顺序）追加到该字节数组中，以便用户可以读取。

实例变量`self.rcv`是一个`RXControlBlock`对象，包含关于你正在接收的入站字节流的信息。

`RXControlBlock`对象有以下相关实例变量：



* `self.rcv.nxt`：你期望接收的下一个序列号。

* `self.rcv.wnd`：当前接收窗口的大小，由你剩余的缓冲区空间决定。

下图显示了你正在接收的字节流以及这些实例变量的含义：



![TCP接收窗口。rcv.nxt之前的是已接收的。rcv.nxt到rcv.nxt + rcv.wnd之间的是未接收但可以接收的。rcv.nxt + rcv.wnd之后的是未接收且不能接收的。](https://su25.cs168.io/assets/projects/proj3/receive-window.svg)

### 接收传入的段

你发送和接收的数据包是 TCP/IP 数据包。

如果你收到一个 IP 数据包`p`，可以像这样提取 TCP 头部和有效载荷：



```
seg = p.tcp
```

如果你收到一个 TCP 段`seg`，可以从其头部提取以下字段：



* `seg.seq`：序列号。

* `seg.ack`：确认号。

* `seg.win`：通告窗口（对方剩余的缓冲区空间）。

* `seg.ACK`：该段是否设置了 ACK 标志（布尔值）。

* `seg.SYN`：该段是否设置了 SYN 标志（布尔值）。

* `seg.FIN`：该段是否设置了 FIN 标志（布尔值）。

如果你收到一个 TCP 段`seg`，可以像这样提取有效载荷：



```
seg.payload       # 有效载荷。

len(seg.payload)  # 有效载荷的长度。
```

### 发送出站段

要创建一个新数据包，可以使用函数`self.new_packet(ack=True, data=None, syn=False)`，它接受以下参数：



* `ack`：是否设置 ACK 标志。默认为 True。

* `data`：要发送的 TCP 有效载荷。默认为 None。

* `syn`：是否设置 SYN 标志。默认为 False。

## 阶段 1：三次握手

### 概述

回顾用于建立 TCP 连接的三次握手：



![TCP三次握手。初始状态为CLOSED。发送SYN后，状态变为SYN\_SENT。发送ACK后，状态变为ESTABLISHED。](https://su25.cs168.io/assets/projects/proj3/tcp-handshake.svg)

握手前，`self.state`为`CLOSED`。

当你发送 SYN 数据包时，你将把状态改为`SYN_SENT`。

当你收到 SYN-ACK 数据包时，你将发送 ACK 数据包并将状态改为`ESTABLISHED`。

### 阶段 1.1：发送 SYN

在`connect`中，实现发送 SYN 数据包。



1. 将你的下一个序列号设置为初始序列号。（你的初始序列号已经为你设置好了。）

2. 使用`self.new_packet`创建一个 SYN 数据包。记住，SYN 数据包不包含任何数据。

3. 使用`self.tx(p)`发送你刚刚创建的数据包`p`。

4. 将状态设置为`SYN_SENT`。

5. 适当地更新下一个序列号。记住，SYN 数据包占用 1 个序列号空间。另外，记住使用模运算。

### 阶段 1.2：接收数据包

接下来，在`rx`中，实现接收数据包。



1. 如果当前状态是`SYN_SENT`，调用`self.handle_synsent(seg)`。

### 阶段 1.3：处理 SYN-ACK，发送 ACK

最后，在`handle_synsent`中，实现处理 SYN-ACK 并发送 ACK。你的所有代码都应在`if acceptable_ack`块内。



1. 你刚刚收到了 SYN-ACK 数据包，因此更新接收序列空间，以指示在此之后你期望接收的下一个字节。

2. SYN-ACK 数据包也在确认你发送的 SYN 数据包，因此更新发送序列空间，以指示 SYN 已被确认。

3. 检查你收到的 SYN-ACK 数据包是否确实在确认你发送的 SYN（ starter 代码中已给出此 if 条件）。如果是，则通过步骤 4-7 发送 ACK 数据包：

4. 将你的下一个序列号设置为 ACK 数据包的确认号。

5. 将状态设置为`ESTABLISHED`。

6. 调用`self.set_pending_ack()`表示你要发送一个 ACK。

7. 调用`self.update_window(seg)`。后续阶段会详细介绍。

### 测试与调试

要运行所有阶段 1 的测试：



```
python autograder.py s1
```

本阶段的测试：



1. 你发送一个 SYN。你收到一个 SYN-ACK，并发送一个 ACK。



```
../../pox.py config=./tests/s1\_t1.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 1 相同，但将对方的初始序列号设置在接近环绕边界的位置。



```
../../pox.py config=./tests/s1\_t2.cfg tcpip.pcap --node=r1 --no-tx
```

要运行到目前为止的所有测试：



```
python autograder.py all 1
```

## 阶段 2：接收有序数据

### 概述

在本阶段，你将处理按序到达的数据包。

例如，假设你收到 P1、P2 和 P3，顺序正确。那么，你只需要将它们的每个有效载荷复制到`self.rx_data`中，就完成了。

另一方面，假设 P2 丢失，你收到了 P1 和 P3。当你收到 P1 时，可以将其有效载荷复制到`self.rx_data`。但当你收到 P3 时，还不能复制其有效载荷。目前，你会丢弃 P3 并发送一个确认，请求 P2。

### 阶段 2.1：原始接收

在`rx`中，实现处理到达的原始 TCP/IP 数据包。你的所有代码都应在`if self.acceptable_seg(seg, payload)`块内。



1. 如果该段是按序的（即，它是你期望的下一个段），调用`self.handle_accepted_seg(seg, payload)`。

2. 否则，该数据包是乱序的，因此调用`self.set_pending_ack()`表示你要发送一个确认。

不要在你的代码中从`rx`返回，因为你需要执行函数的其余部分。

### 阶段 2.2：处理接受的段

在`handle_accepted_seg`中，实现处理你在阶段 2.1 中处理的有序数据包。



1. 如果状态是`[ESTABLISHED, FIN_WAIT_1, FIN_WAIT_2]`之一，且有效载荷的长度非零，调用`handle_accepted_payload(payload)`。

不要在你的代码中从`handle_accepted_seg`返回，因为你需要执行函数的其余部分。

### 阶段 2.3：处理接受的有效载荷

在`handle_accepted_payload`中，实现处理你在阶段 2.2 中处理的有效载荷。



1. 你刚刚收到一个数据包，因此更新接收序列空间，以指示在此之后你期望接收的下一个字节。

2. 你刚刚收到一些有效载荷，这会占用你的一些缓冲区空间。相应地减小接收窗口大小。

3. 你要将有效载荷传递给用户，因此将有效载荷添加到`self.rx_data`的末尾。

   提示：`a += b`可用于将字节添加到字节数组的末尾。

4. 调用`self.set_pending_ack()`以指示你要确认此数据。

### 测试与调试

要运行所有阶段 2 的测试：



```
python autograder.py s2
```

本阶段的测试：



1. 你收到 1 个带有有效载荷的数据包。检查你是否处理了正确数量的数据包。检查序列号。检查接收的数据是否正确。



```
../../pox.py config=./tests/s2\_t1.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 1 相同，但你收到 3 个带有有效载荷的数据包。



```
../../pox.py config=./tests/s2\_t2.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 1 相同，但你收到 50 个带有有效载荷的数据包。



```
../../pox.py config=./tests/s2\_t3.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 1 相同，但数据包被丢弃一次。你应该用一个确认来请求该数据包。然后，你在第二次尝试时收到该数据包。



```
../../pox.py config=./tests/s2\_t4.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 4 相同，但你收到 3 个数据包，第二个数据包被丢弃。你应该用一个确认来请求第二个数据包。然后，你在第二次尝试时收到该数据包。



```
../../pox.py config=./tests/s2\_t5.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 5 相同，但你收到 15 个数据包，每隔一个数据包（1、3、5、7 等）被丢弃。每个数据包最多被丢弃一次，因此你在第二次尝试时收到数据包。



```
../../pox.py config=./tests/s2\_t6.cfg tcpip.pcap --node=r1 --no-tx
```

要运行到目前为止的所有测试：



```
python autograder.py all 2
```

## 阶段 3：接收乱序数据

### 概述：乱序数据包

在阶段 2 中，如果我们收到乱序的段，我们会丢弃它并发送一个确认，请求下一个有序的段。

在本阶段，我们将对此进行改进，通过暂时保存任何乱序的段，直到它们可以按序处理。

例如，假设你要接收 P1、P2 和 P3，但 P2 丢失了。

你收到 P1 并处理它。

然后，你收到 P3。不像前一阶段那样丢弃 P3，你会将 P3 存储在你的*接收队列*中，并发送一个确认请求 P2。

然后，当你收到 P2 时，你可以处理 P2。之后，你可以到接收队列中处理 P3。

注意，我们暂时存储乱序数据包，但最终会按序处理它们。

### 概述：数据包重叠

有时，对方可能有 bug，你会收到带有重叠有效载荷的数据包。例如，假设你要接收的字节流是：



```
P O T A T O

1 2 3 4 5 6
```

你可能收到一个数据包：



```
P O T A

1 2 3 4
```

和另一个数据包：



```
T A T O

3 4 5 6
```

如果我们只是将每个有效载荷追加到接收队列的末尾，用户会收到 “POTATATO”，这是不正确的。我们需要从第二个数据包的开头移除重复的字节。

### 代码概述：接收队列

实例变量`self.rx_queue`是一个`RecvQueue`对象，用于存储乱序数据包。

`RecvQueue`会自动按序列号顺序为你排序数据包。

`RecvQueue`对象有以下相关方法：



* `self.rx_queue.push(p)`：将数据包`p`添加到队列中。

* `s, p = self.rx_queue.pop()`：从队列中移除并返回序列号最小的数据包。

  返回值是一个元组，包含数据包的序列号（`s`）和数据包本身（`p`）。

* `s, p = self.rx_queue.peek()`：返回但不移除队列中序列号最小的数据包。

  返回值是一个元组，包含数据包的序列号（`s`）和数据包本身（`p`）。

* `self.rx_queue.empty()`：返回一个布尔值，指示队列是否为空。

### 阶段 3.1：插入到接收队列

在`rx`中，实现将到达的数据包插入到接收队列中。你的所有代码都应在`if self.acceptable_seg(seg, payload)`块内。



1. 在阶段 2.1 中，你修改了`rx`来处理传入的数据包。现在你可以注释掉那段代码。

2. 当一个数据包到达时，只需将其插入到`self.rx_queue`中。

### 阶段 3.2：处理接收队列

同样在`rx`中，实现从接收队列处理任何有序的段。每次调用`rx`时，队列中可能有下一个有序的段可供处理。



1. 如果队列中的下一个数据包（序列号最小的）是乱序的，设置一个待发送的确认并停止检查队列。

2. 否则，队列中的下一个数据包是有序的，因此你应该处理它。

   从队列中弹出该数据包。

   提取其有效载荷（使用提示来处理重叠）。

   调用`self.handle_accepted_seg`来处理有效载荷。

3. 重复步骤 1 和 2，直到处理完队列中所有有序的数据包。

不要在你的代码中从`rx`返回，因为你需要执行函数的其余部分。

### 测试与调试

要运行所有阶段 3 的测试：



```
python autograder.py s3
```

本阶段的测试：



1. 你收到 1 个带有有效载荷的数据包。该数据包第一次被丢弃，第二次发送。检查数据是否被正确接收。



```
../../pox.py config=./tests/s3\_t1.cfg tcpip.pcap --node=r1 --no-tx
```



1. 你收到 3 个数据包。每隔一个数据包（1、3、5、7 等）被丢弃。每个数据包最多被丢弃一次，因此你在第二次尝试时收到数据包。



```
../../pox.py config=./tests/s3\_t2.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 2 相同，但你收到 15 个数据包。



```
../../pox.py config=./tests/s3\_t3.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 2 相同，但将对方的初始序列号设置在接近环绕边界的位置。



```
../../pox.py config=./tests/s3\_t4.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 3 相同，但将对方的初始序列号设置在接近环绕边界的位置。



```
../../pox.py config=./tests/s3\_t5.cfg tcpip.pcap --node=r1 --no-tx
```

要运行到目前为止的所有测试：



```
python autograder.py all 3
```

## 阶段 4：简单的数据发送

### 概述

在阶段 2 和 3 中，你实现了数据接收。在本阶段，你将实现数据发送。

回顾一下，用户将他们要发送的字节放入`self.tx_data`中，你的工作是将这些字节发送出去。你会在发送时从该数组的前端移除字节。

然而，你不能立即发送`self.tx_data`中的所有内容。发送窗口（`self.snd.wnd`）告诉我们在任何时候可以有多少出站字节在传输中。当我们处理确认时，我们的发送窗口会更新，这将允许我们发送更多的数据包。

### 阶段 4.1：处理确认

在`check_ack`中，实现处理传入的确认。你的所有代码都应在`if self.state in (ESTABLISHED, FIN_WAIT_1, FIN_WAIT_2, CLOSE_WAIT, CLOSING):`块内。



1. 如果收到的段的确认号表示一个已发送但未被确认的数据包，对该段调用`self.handle_accepted_ack`。

   提示：查看[发送序列空间图](https://su25.cs168.io/proj3/#send-sequence-space-txcontrolblock)，了解哪些序列号是已发送但未被确认的。

2. 如果确认号之前已经被确认过（即，这是一个旧的确认），丢弃该数据包。

   允许`check_ack`的其余部分执行，但不允许`handle_accepted_seg`的其余部分执行。（提示：有一个布尔变量可以帮助你。）

3. 如果确认号表示一个你尚未发送的字节，丢弃该数据包。

   不允许`check_ack`的其余部分执行，也不允许`handle_accepted_seg`的其余部分执行。

### 阶段 4.2：处理接受的确认

在`handle_accepted_ack`中，实现处理有序的确认。（目前我们不处理乱序的确认。）



1. 更新跟踪已发送但未被确认的序列号的变量。

### 阶段 4.3：创建段

在`maybe_send`中，实现发送尽可能多的传输缓冲区（`self.tx_data`）中的数据，只要允许。

创建要发送的数据包时，你需要满足以下条件：



* 你不能发送比`self.tx_data`中更多的数据。

  如果`self.tx_data`变为空，在这次`maybe_send`调用中就没有更多数据可发送了。

* 你不能发送超过发送窗口允许的数据。

  提示：我们的解决方案将`remaining`设置为根据窗口你仍然可以发送的字节数。

  提示：查看[发送序列空间图](https://su25.cs168.io/proj3/#send-sequence-space-txcontrolblock)，思考哪个范围对应于你尚未发送但仍可以发送的字节。

* 你发送的每个有效载荷的大小必须小于或等于`self.mss`字节。

使用`self.new_packet`创建新数据包，并使用`self.tx`发送数据包。

当你发送一些字节时，记住从`self.tx_data`数组的前端移除这些字节。

### 阶段 4.4：传输段

在`tx`中，实现传输数据包时更新发送序列空间。你的所有代码都应在`if (p.tcp.SYN or p.tcp.FIN or p.tcp.payload) and not retxed:`块内。



1. 如果数据包包含非空有效载荷，更新发送序列空间中要发送的下一个序列号。

### 测试与调试

要运行所有阶段 4 的测试：



```
python autograder.py s4
```

本阶段的测试：



1. 你发送 1 个数据包。检查对方是否正确接收了所有数据。



```
../../pox.py config=./tests/s4\_t1.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 1 相同，但你发送 3 个数据包。



```
../../pox.py config=./tests/s4\_t2.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 1 相同，但你发送 50 个数据包。



```
../../pox.py config=./tests/s4\_t3.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 2 相同，但将对方的初始序列号设置在接近环绕边界的位置。



```
../../pox.py config=./tests/s4\_t4.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 3 相同，但将对方的初始序列号设置在接近环绕边界的位置。



```
../../pox.py config=./tests/s4\_t5.cfg tcpip.pcap --node=r1 --no-tx
```

要运行到目前为止的所有测试：



```
python autograder.py all 4
```

## 阶段 5：遵守通告窗口

### 概述

欢迎来到本项目中最短的阶段。

在阶段 4 中，你在发送数据时遵守了发送窗口（例如，你不能发送太多在传输中的数据包）。

然而，到目前为止，我们将`self.snd.wnd`设置为`self.TX_DATA_MAX`，这是不正确的。

每次你收到一个数据包时，对方会通告它剩余的缓冲区空间。你应该使用这个通告的值来调整你的发送窗口大小，这样你就不会向对方发送过多的数据包。

注意：在实际中，你还会实现拥塞控制并设置`self.snd.wnd`以避免网络拥塞，但在本项目中我们会跳过这一点。

### 阶段 5.1：更新窗口大小

在`update_window`中，实现正确设置窗口大小。



1. 将发送窗口赋值为段中通告的值。

### 测试与调试

要运行所有阶段 5 的测试：



```
python autograder.py s5
```

本阶段的测试：



1. 将对方的接收窗口设置为 1 字节。你有 300 字节要发送。检查你是否发送了 300 个数据包。



```
../../pox.py config=./tests/s5\_t1.cfg tcpip.pcap --node=r1 --no-tx
```



1. 将对方的接收窗口设置为 199 字节。你有 1990 字节要发送。检查你是否发送了 10 个数据包。



```
../../pox.py config=./tests/s5\_t2.cfg tcpip.pcap --node=r1 --no-tx
```

要运行到目前为止的所有测试：



```
python autograder.py all 5
```

如果此时阶段 1-5 的所有测试都通过，你就完成了项目 3A！不要忘记提交到 Gradescope 上的项目 3A 自动评分系统。

要提交项目 3A，只需将`student_socket.py`文件提交到[Gradescope 上的项目 3A 自动评分系统](https://www.gradescope.com/courses/1054987/assignments/6346821)。

## 阶段 6：被动关闭

### 概述

现在我们转向连接终止。在 TCP 中，有两种优雅关闭过程：



* 被动关闭：对方先关闭。（阶段 6）

* 主动关闭：你先关闭。（阶段 7）

下图显示了被动关闭中发生的情况：



![被动关闭图。在已建立状态，你和对方都可以发送有效载荷。你收到FIN，并发送ACK，进入关闭等待状态，此时只有你可以发送有效载荷。你完成后发送FIN，进入最后确认状态，此时双方都不能发送有效载荷。你收到ACK（确认你的FIN），进入关闭状态。](https://su25.cs168.io/assets/projects/proj3/passive-close.svg)



* 你处于`ESTABLISHED`状态。

* 你收到一个 FIN 数据包。作为响应，你发送一个 ACK，并转换到`CLOSE_WAIT`状态。

* 当你完成后，你发送一个 FIN，并转换到`LAST_ACK`状态。

* 当你收到一个 ACK 时，你转换到`CLOSED`状态。

### 代码概述：FIN 控制

实例变量`self.fin_ctrl`有两个用于连接终止的有用方法。



* `self.fin_ctrl.set_pending(next_state=None)`：有时你知道你要发送一个 FIN，但实际上还不能发送，因为传输缓冲区中还有一些数据在等待。因此，当你想要发送 FIN 时，应该调用这个函数。

  如果提供了`next_state`作为参数，在 FIN 实际发送后，你将转换到该状态。

* `self.fin_ctrl.acks_our_fin(ack)`：接收`ack`（来自传入数据包的确认号）。如果你发送的 FIN 已被确认，则返回 True。

### 阶段 6.1：接收 FIN

在`handle_accepted_fin`中，实现接收来自对方的 FIN。



1. 如果你处于`ESTABLISHED`状态，执行步骤 2-4。

2. 在接收序列空间中，更新你期望接收的下一个序列号。

3. 调用`self.set_pending_ack()`来确认 FIN。

4. 更新`self.state`。

### 阶段 6.2：发送 FIN

在`close`中，实现发送 FIN。你的所有代码都应在`elif self.state is CLOSE_WAIT:`块内。



1. 设置一个待发送的 FIN。记住提供一个参数，指定发送 FIN 后要转换到的状态。

   提示：使用`self.fin_ctrl`的一个方法。

### 阶段 6.3：接收 ACK

在`check_ack`中，实现接收确认（确认你的 FIN）并关闭连接。你的所有代码都应在`elif self.state == LAST_ACK:`块内。



1. 如果你刚刚收到的段中的确认号正在确认你发送的 FIN，则调用`self._delete_tcb()`来删除连接状态。

   提示：使用`self.fin_ctrl`的一个方法。

### 测试与调试

要运行所有阶段 6 的测试：



```
python autograder.py s6
```

本阶段的测试：



1. 执行三次握手。

   第四个数据包是来自对方的 FIN。

   第五个数据包是你的 ACK。

   第六个数据包是你的 FIN。

   第七个数据包是对方的 ACK。

   检查在被动关闭期间你是否转换到正确的状态。



```
../../pox.py config=./tests/s6\_t1.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 1 相同，但将对方的初始序列号设置在接近环绕边界的位置。



```
../../pox.py config=./tests/s6\_t2.cfg tcpip.pcap --node=r1 --no-tx
```

要运行到目前为止的所有测试：



```
python autograder.py all 6
```

## 阶段 7：主动关闭

### 概述

在阶段 6 中，你实现了被动关闭，即对方先关闭。在本阶段，你将实现主动关闭，即你先关闭。

下图显示了主动关闭中发生的情况：



![主动关闭图。在已建立状态，你和对方都可以发送有效载荷。你完成后发送FIN，进入FIN\_WAIT\_1状态，此时只有对方可以发送有效载荷。路径1：你收到ACK，进入FIN\_WAIT\_2状态。你收到FIN并发送ACK，进入TIME\_WAIT状态。路径2：你收到FIN-ACK，发送ACK，立即进入TIME\_WAIT状态。路径3：你收到FIN，发送ACK，进入CLOSING状态。你收到ACK，进入TIME\_WAIT状态。在TIME\_WAIT状态，双方都不能发送有效载荷。计时器等待一段时间后，转换到CLOSED状态。](https://su25.cs168.io/assets/projects/proj3/active-close.svg)



* 你处于`ESTABLISHED`状态。

* 当你完成后，你发送一个 FIN，并转换到`FIN_WAIT_1`状态。

此时，我们的状态转换可能遵循 3 种可能的路径。在所有 3 种路径中，我们的目标是到达`TIME_WAIT`状态。



1. 如果你只收到一个 ACK，说明对方还有数据要发送。

   你转换到`FIN_WAIT_2`状态，在那里你等待对方发送 FIN。

   最终，你收到一个 FIN，作为响应，你发送一个确认并转换到`TIME_WAIT`状态。

2. 如果你收到一个 FIN-ACK，说明对方在你完成的同时也完成了。

   作为响应，你发送一个确认并立即转换到`TIME_WAIT`状态。

3. 如果你收到一个 FIN，说明对方也完成了，但尚未确认你的 FIN。

   你转换到`CLOSING`状态，在那里等待对方确认你的 FIN。

   最终，你收到对你的 FIN 的确认，并转换到`TIME_WAIT`状态。

一旦你到达`TIME_WAIT`状态，你将启动一个计时器，等待一段时间后转换到`CLOSED`状态。

### 代码概述：启动计时器

要转换到`TIME_WAIT`状态，你应该调用`self.start_timer_timewait()`。

这个方法将为你转换到`TIME_WAIT`状态，并且还会启动计时器，等待一段时间后转换到`CLOSED`状态。

### 阶段 7.1：发送 FIN

在`close`中，实现发送 FIN。你的所有代码都应在`elif self.state is ESTABLISHED:`块内。



1. 设置一个待发送的 FIN。记住提供一个参数，指定发送 FIN 后要转换到的状态。

   提示：使用`self.fin_ctrl`的一个方法。

### 阶段 7.2：接收 FIN

在`handle_accepted_fin`中，实现图中接收 FIN 的所有 3 种状态转换。



1. 如果你处于`FIN_WAIT_1`状态并且收到一个 FIN-ACK 数据包，则：

   设置一个待发送的确认。

   立即转换到`TIME_WAIT`状态。提示：使用`self.start_timer_timewait()`进行转换。

2. 否则，如果你处于`FIN_WAIT_1`状态并且只收到一个 FIN 数据包（未设置 ACK 标志），则：

   设置一个待发送的确认。

   转换到`CLOSING`状态。

3. 否则，如果你处于`FIN_WAIT_2`状态并且收到一个 FIN 数据包，则：

   在接收序列空间中，更新你期望接收的下一个序列号。

   设置一个待发送的确认。

   使用`self.start_timer_timewait()`转换到`TIME_WAIT`状态。

### 阶段 7.3：接收 ACK

在`check_ack`中，实现图中接收确认的两种状态转换。



1. 如果你处于`FIN_WAIT_1`状态（starter 代码中已包含此 if 检查），则：

   使用`self.fin_ctrl`的一个方法检查你刚刚收到的段中的确认号是否在确认你发送的 FIN。

   如果是，则转换到`FIN_WAIT_2`状态。

2. 如果你处于`CLOSING`状态（starter 代码中已包含此 if 检查），则：

   使用`self.fin_ctrl`的一个方法检查你刚刚收到的段中的确认号是否在确认你发送的 FIN。

   如果是，则使用`self.start_timer_timewait()`转换到`TIME_WAIT`状态。

### 测试与调试

要运行所有阶段 7 的测试：



```
python autograder.py s7
```

本阶段的测试：



1. 你处于`ESTABLISHED`状态并发送一个 FIN。你应该转换到`FIN_WAIT_1`状态。

   你收到一个 ACK。你应该转换到`FIN_WAIT_2`状态。

   然后，你收到一个 FIN。你应该发送一个 ACK 并转换到`TIME_WAIT`状态。

   计时器应该超时，你应该转换到`CLOSED`状态。



```
../../pox.py config=./tests/s7\_t1.cfg tcpip.pcap --node=r1 --no-tx
```



1. 当传输缓冲区中还有一些数据时，你尝试关闭连接。

   你应该等待所有数据发送完毕后再发送 FIN。



```
../../pox.py config=./tests/s7\_t2.cfg tcpip.pcap --node=r1 --no-tx
```

要运行到目前为止的所有测试：



```
python autograder.py all 7
```

## 阶段 8：重传数据包

### 概述

在阶段 4 中，你实现了简单的有序段发送。然而，你没有处理你发送的数据包丢失的情况。在本阶段，你将通过重传数据包来处理丢失的数据包。

在本项目中，你第一次发送数据包时，会：



* 给数据包加上时间戳，指示数据包最初传输的时间。

* 将数据包添加到*重传队列*中。

当一个数据包被确认后，你可以从重传队列中移除该数据包。

每 100 毫秒，会检查重传队列中最旧的数据包（序列号最小的）是否已过期。如果已过期，则重传该数据包。

数据包过期是什么意思？在本阶段，我们认为一个数据包如果在 1 秒内没有被确认，就是过期的。

注意：我们只在第一次传输数据包时将其添加到队列中。不会将重传的数据包添加到队列中。

### 阶段 8.1：将首次发送的数据包加入重传队列

在 `tx` 方法中，实现将首次发送的数据包加入重传队列。所有代码都应放在 `if (p.tcp.SYN or p.tcp.FIN or p.tcp.payload) and not retxed:` 代码块内（与阶段 4.4 的代码在同一位置）。



1. 为数据包设置时间戳，记录其首次发送的时间。可以使用 `self._clock.time()` 获取当前时间（单位为秒）。

2. 将数据包添加到重传队列 `self.retransmit_queue` 中。

### 阶段 8.2：检查并重传过期数据包

在 `retransmit` 方法中，实现检查重传队列中是否有过期数据包并进行重传。



1. 如果重传队列为空，直接返回（无需执行任何操作）。

2. 找到队列中最旧的数据包（即序列号最小的包）。

3. 检查该数据包是否已过期：计算当前时间（`self._clock.time()`）与数据包时间戳的差值，如果差值大于 1 秒，则认为数据包过期。

4. 如果数据包已过期，使用 `self.tx(p, retxed=True)` 重传该数据包（`retxed=True` 表示这是一个重传的包）。

5. 更新该数据包的时间戳为当前时间（因为它刚刚被重传）。

### 阶段 8.3：处理 ACK 时移除已确认的数据包

在 `handle_accepted_ack` 方法中，实现当收到 ACK 时，从复传队列中移除已被确认的数据包。



1. 遍历重传队列中的所有数据包，检查每个包的序列号和长度是否已被当前 ACK 确认。

* 对于包含 payload 的数据包：如果 ACK 号大于该包的序列号加上 payload 长度，则该包已被确认。

* 对于 SYN 或 FIN 数据包：SYN 和 FIN 各占 1 个序列号空间，因此如果 ACK 号大于该包的序列号，则该包已被确认。

1. 从队列中移除所有已被确认的数据包。

### 测试与调试

要运行阶段 8 的所有测试：



```
python autograder.py s8
```

本阶段的测试包括：



1. 发送 1 个数据包，该数据包丢失，然后被重传。检查重传机制是否正常工作。



```
../../pox.py config=./tests/s8\_t1.cfg tcpip.pcap --node=r1 --no-tx
```



1. 发送 3 个数据包，其中第二个数据包丢失并被重传。检查重传后的数据接收是否正确。



```
../../pox.py config=./tests/s8\_t2.cfg tcpip.pcap --node=r1 --no-tx
```



1. 发送 50 个数据包，随机有 10 个数据包丢失并被重传。检查最终是否所有数据都被正确接收。



```
../../pox.py config=./tests/s8\_t3.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 2 类似，但序列号接近 32 位 wrap-around 边界。检查重传机制在序列号环绕时是否正常工作。



```
../../pox.py config=./tests/s8\_t4.cfg tcpip.pcap --node=r1 --no-tx
```

要运行到目前为止的所有测试：



```
python autograder.py all 8
```

## 阶段 9：处理重复 ACK 与快速重传

### 概述

在阶段 8 中，我们通过超时机制来触发重传，但这种方式可能不够高效（需要等待 1 秒才重传）。在本阶段，我们将实现 “快速重传” 机制：当收到 3 个重复的 ACK 时，立即重传可能丢失的数据包，而无需等待超时。

重复 ACK 是指：多个 ACK 携带相同的 ACK 号，且该 ACK 号小于当前发送窗口中未被确认的最大序列号。这通常意味着中间有数据包丢失，接收方在持续确认已收到的最后一个有序数据包。

### 阶段 9.1：跟踪重复 ACK

在 `check_ack` 方法中，实现对重复 ACK 的计数。所有代码应放在处理 “旧 ACK” 的分支中（即阶段 4.1 中处理 “该 ACK 号之前已被确认过” 的情况）。



1. 如果收到的 ACK 是重复 ACK（即 ACK 号与上一个 ACK 号相同，且处于未被完全确认的范围内），则将重复 ACK 计数器加 1。

2. 否则，重置重复 ACK 计数器为 0。

### 阶段 9.2：触发快速重传

在 `check_ack` 方法中，当重复 ACK 计数器达到 3 时，触发快速重传。



1. 如果重复 ACK 计数器达到 3：

* 找到重传队列中序列号最小的未被确认的数据包（即最旧的未确认包）。

* 立即重传该数据包（使用 `self.tx(p, retxed=True)`）。

* 重置重复 ACK 计数器为 0。

### 测试与调试

要运行阶段 9 的所有测试：



```
python autograder.py s9
```

本阶段的测试包括：



1. 发送 4 个数据包，其中第二个数据包丢失。接收方会发送 3 个重复 ACK，触发快速重传。检查是否在收到 3 个重复 ACK 后立即重传丢失的包。



```
../../pox.py config=./tests/s9\_t1.cfg tcpip.pcap --node=r1 --no-tx
```



1. 发送 10 个数据包，随机丢失 2 个数据包，每个丢失的包都会触发 3 个重复 ACK 和快速重传。检查快速重传机制是否正确处理多个丢包场景。



```
../../pox.py config=./tests/s9\_t2.cfg tcpip.pcap --node=r1 --no-tx
```



1. 与测试 1 类似，但序列号接近 32 位 wrap-around 边界。检查快速重传在序列号环绕时是否正常工作。



```
../../pox.py config=./tests/s9\_t3.cfg tcpip.pcap --node=r1 --no-tx
```

要运行所有阶段的测试：



```
python autograder.py all
```

如果所有阶段（1-9）的测试都通过，那么你就完成了整个 Project 3！不要忘记将 `student_socket.py` 文件提交到 Gradescope 上的 Project 3B 自动评分系统。

提交 Project 3B 时，只需提交 `student_socket.py` 文件到 [Gradescope 上的 Project 3B 自动评分系统](https://www.gradescope.com/courses/1054987/assignments/6346822)。

> （注：文档部分内容可能由 AI 生成）