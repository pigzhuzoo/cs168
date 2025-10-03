import util

# Your program should send TTLs in the range [1, TRACEROUTE_MAX_TTL] inclusive.
# Technically IPv4 supports TTLs up to 255, but in practice this is excessive.
# Most traceroute implementations cap at approximately 30.  The unit tests
# assume you don't change this number.
TRACEROUTE_MAX_TTL = 30

# Cisco seems to have standardized on UDP ports [33434, 33464] for traceroute.
# While not a formal standard, it appears that some routers on the internet
# will only respond with time exceeeded ICMP messages to UDP packets send to
# those ports.  Ultimately, you can choose whatever port you like, but that
# range seems to give more interesting results.
TRACEROUTE_PORT_NUMBER = 33434  # Cisco traceroute port number.

# Sometimes packets on the internet get dropped.  PROBE_ATTEMPT_COUNT is the
# maximum number of times your traceroute function should attempt to probe a
# single router before giving up and moving on.
PROBE_ATTEMPT_COUNT = 3

class IPv4:
    # Each member below is a field from the IPv4 packet header.  They are
    # listed below in the order they appear in the packet.  All fields should
    # be stored in host byte order.
    #
    # You should only modify the __init__() method of this class.
    version: int
    header_len: int  # Note length in bytes, not the value in the packet.
    tos: int         # Also called DSCP and ECN bits (i.e. on wikipedia).
    length: int      # Total length of the packet.
    id: int
    flags: int
    frag_offset: int
    ttl: int
    proto: int
    cksum: int
    src: str
    dst: str

    def __init__(self, buffer: bytes):
        b = ''.join(format(byte, '08b') for byte in [*buffer])
        self.version = int(b[0 : 4], 2)
        self.header_len = int(b[4 : 8], 2) * 4
        self.tos = int(b[8 : 16], 2)
        self.length = int(b[16 : 32], 2)
        self.id = int(b[32 : 48], 2)
        self.flags = int(b[48 : 51], 2)
        self.frag_offset = int(b[51 : 64], 2)
        self.ttl = int(b[64 : 72], 2)
        self.proto = int(b[72 : 80], 2)
        self.cksum = int(b[80 : 96], 2)
        self.src = b[96 : 128]
        self.dst = b[128 : 160]
        # 源IP：32位（96-128）→ 拆4个8位段，转点分十进制（修正点2）
        src_bits = b[96:128]  # 32位源IP二进制
        src_octets = [
            int(src_bits[0:8], 2),   # 第1个8位段（十进制）
            int(src_bits[8:16], 2),  # 第2个8位段
            int(src_bits[16:24], 2), # 第3个8位段
            int(src_bits[24:32], 2)  # 第4个8位段
        ]
        self.src = ".".join(map(str, src_octets))  # 拼接为点分十进制
        
        # 目的IP：32位（128-160）→ 同src处理（修正点2）
        dst_bits = b[128:160]  # 32位目的IP二进制
        dst_octets = [
            int(dst_bits[0:8], 2),
            int(dst_bits[8:16], 2),
            int(dst_bits[16:24], 2),
            int(dst_bits[24:32], 2)
        ]
        self.dst = ".".join(map(str, dst_octets))
        # pass  # TODO

    def __str__(self) -> str:
        return f"IPv{self.version} (tos 0x{self.tos:x}, ttl {self.ttl}, " + \
            f"id {self.id}, flags 0x{self.flags:x}, " + \
            f"ofsset {self.frag_offset}, " + \
            f"proto {self.proto}, header_len {self.header_len}, " + \
            f"len {self.length}, cksum 0x{self.cksum:x}) " + \
            f"{self.src} > {self.dst}"


class ICMP:
    # Each member below is a field from the ICMP header.  They are listed below
    # in the order they appear in the packet.  All fields should be stored in
    # host byte order.
    #
    # You should only modify the __init__() function of this class.
    type: int
    code: int
    cksum: int

    def __init__(self, buffer: bytes):
        b = ''.join(format(byte, '08b') for byte in [*buffer])
        self.type = int(b[0 : 8], 2)
        self.code = int(b[8 : 16], 2)
        self.cksum = int(b[16 : 32], 2)
        # pass  # TODO

    def __str__(self) -> str:
        return f"ICMP (type {self.type}, code {self.code}, " + \
            f"cksum 0x{self.cksum:x})"


class UDP:
    # Each member below is a field from the UDP header.  They are listed below
    # in the order they appear in the packet.  All fields should be stored in
    # host byte order.
    #
    # You should only modify the __init__() function of this class.
    src_port: int
    dst_port: int
    len: int
    cksum: int

    def __init__(self, buffer: bytes):
        b = ''.join(format(byte, '08b') for byte in [*buffer])
        self.src_port = int(b[0 : 16], 2)
        self.dst_port = int(b[16 : 32], 2)
        self.len = int(b[32 : 48], 2)
        self.cksum = int(b[48 : 64], 2)
        # pass  # TODO

    def __str__(self) -> str:
        return f"UDP (src_port {self.src_port}, dst_port {self.dst_port}, " + \
            f"len {self.len}, cksum 0x{self.cksum:x})"

# TODO feel free to add helper functions if you'd like

def traceroute(sendsock: util.Socket, recvsock: util.Socket, ip: str) \
        -> list[list[str]]:
    """ Run traceroute and returns the discovered path.

    Calls util.print_result() on the result of each TTL's probes to show
    progress.

    Arguments:
    sendsock -- This is a UDP socket you will use to send traceroute probes.
    recvsock -- This is the socket on which you will receive ICMP responses.
    ip -- This is the IP address of the end host you will be tracerouting.

    Returns:
    A list of lists representing the routers discovered for each ttl that was
    probed.  The ith list contains all of the routers found with TTL probe of
    i+1.   The routers discovered in the ith list can be in any order.  If no
    routers were found, the ith list can be empty.  If `ip` is discovered, it
    should be included as the final element in the list.
    """

    # TODO Add your implementation
    result = []  # 存储最终结果：每个元素是对应TTL的路由器列表
    target_reached = False  # 标记是否到达目标主机

    for ttl in range(1, TRACEROUTE_MAX_TTL + 1):
        current_routers = set()  # 用集合去重当前TTL的路由器IP
        sendsock.set_ttl(ttl)   # 设置当前TTL

        for _ in range(PROBE_ATTEMPT_COUNT):
            # 发送UDP探针包（ payload为"Potato"，目标端口固定）
            sendsock.sendto("Potato".encode(), (ip, TRACEROUTE_PORT_NUMBER))

            # 等待响应
            if recvsock.recv_select():
                buf, _ = recvsock.recvfrom()  # 接收ICMP响应包
                try:
                    # 解析IPv4头部（获取源IP和协议类型）
                    ipv4 = IPv4(buf)
                    # 只处理ICMP协议的响应（proto=1）
                    if ipv4.proto != 1:
                        continue

                    # 提取ICMP头部（跳过IPv4头部）
                    icmp_buf = buf[ipv4.header_len:]
                    icmp = ICMP(icmp_buf)

                    # 情况1：ICMP类型11（TTL过期）→ 中间路由器
                    if icmp.type == 11 and icmp.code == 0:
                        current_routers.add(ipv4.src)
                    # 情况2：ICMP类型3（目标不可达）且源IP是目标IP→ 到达终点
                    elif icmp.type == 3 and ipv4.src == ip:
                        current_routers.add(ipv4.src)
                        target_reached = True

                except (IndexError, ValueError):
                    # 忽略解析失败的数据包（可能不完整）
                    continue

        # 将当前TTL的结果转为列表，添加到总结果
        result.append(list(current_routers))
        # 打印当前TTL的探测结果
        util.print_result(list(current_routers), ttl)

        # 若到达目标主机，停止探测
        if target_reached:
            break

    return result


if __name__ == '__main__':
    args = util.parse_args()
    ip_addr = util.gethostbyname(args.host)
    print(f"traceroute to {args.host} ({ip_addr})")
    traceroute(util.Socket.make_udp(), util.Socket.make_icmp(), ip_addr)
