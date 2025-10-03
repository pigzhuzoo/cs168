"""
Your awesome Distance Vector router for CS 168

Based on skeleton code by:
  MurphyMc, zhangwen0411, lab352
"""

import sim.api as api
from cs168.dv import (
    RoutePacket,
    Table,
    TableEntry,
    DVRouterBase,
    Ports,
    FOREVER,
    INFINITY,
)


class DVRouter(DVRouterBase):

    # A route should time out after this interval
    ROUTE_TTL = 15

    # -----------------------------------------------
    # At most one of these should ever be on at once
    SPLIT_HORIZON = False
    POISON_REVERSE = False
    # -----------------------------------------------

    # Determines if you send poison for expired routes
    POISON_EXPIRED = False

    # Determines if you send updates when a link comes up
    SEND_ON_LINK_UP = False

    # Determines if you send poison when a link goes down
    POISON_ON_LINK_DOWN = False

    def __init__(self):
        """
        Called when the instance is initialized.
        DO NOT remove any existing code from this method.
        However, feel free to add to it for memory purposes in the final stage!
        """
        assert not (
            self.SPLIT_HORIZON and self.POISON_REVERSE
        ), "Split horizon and poison reverse can't both be on"

        self.start_timer()  # Starts signaling the timer at correct rate.

        # Contains all current ports and their latencies.
        # See the write-up for documentation.
        self.ports = Ports()

        # This is the table that contains all current routes
        self.table = Table()
        self.table.owner = self

        ##### Begin Stage 10A #####
        self.history = {}
        ##### End Stage 10A #####

    def add_static_route(self, host, port):
        """
        Adds a static route to this router's table.

        Called automatically by the framework whenever a host is connected
        to this router.

        :param host: the host.
        :param port: the port that the host is attached to.
        :returns: nothing.
        """
        # `port` should have been added to `peer_tables` by `handle_link_up`
        # when the link came up.
        assert port in self.ports.get_all_ports(), "Link should be up, but is not."

        ##### Begin Stage 1 #####
        self.table[host] = TableEntry(host ,port ,self.ports.get_latency(port) ,FOREVER)
        ##### End Stage 1 #####

    def handle_data_packet(self, packet, in_port):
        """
        Called when a data packet arrives at this router.

        You may want to forward the packet, drop the packet, etc. here.

        :param packet: the packet that arrived.
        :param in_port: the port from which the packet arrived.
        :return: nothing.
        """
        
        ##### Begin Stage 2 #####
        if packet.dst in self.table and self.table[packet.dst].latency < INFINITY:
            self.send(packet=packet, port=self.table[packet.dst].port)
        ##### End Stage 2 #####
    def _get_advertised_latency(self, host, entry, port):
        """计算实际发送的延迟（用于增量判断的核心值）"""
        if self.SPLIT_HORIZON and port == entry.port:
            return None  # 水平分割：不发送
        if self.POISON_REVERSE and port == entry.port:
            return INFINITY  # 毒化反向：发送INFINITY
        if entry.latency >= INFINITY:
            return INFINITY  # 路由不可达：发送INFINITY
        return entry.latency  # 正常路由：发送实际延迟
    def send_routes(self, force=False, single_port=None):
        """
        Send route advertisements for all routes in the table.

        :param force: if True, advertises ALL routes in the table;
                      otherwise, advertises only those routes that have
                      changed since the last advertisement.
               single_port: if not None, sends updates only to that port; to
                            be used in conjunction with handle_link_up.
        :return: nothing.
        """
        
        ##### Begin Stages 3, 6, 7, 8, 10 #####
        ports_to_process = [single_port] if single_port is not None else self.ports.get_all_ports()

        for host, entry in self.table.items():
            for p in ports_to_process:
                # 计算当前应发送的延迟（考虑水平分割/毒化反向）
                advertised_latency = self._get_advertised_latency(host, entry, p)
                if advertised_latency is None:  # 水平分割不发送
                    continue

                # 检查是否需要发送（force=True 或 与历史记录不同）
                need_send = False
                if force:
                    need_send = True
                else:
                    # 检查历史记录：端口p是否记录过该主机的延迟
                    port_history = self.history.get(p, {})
                    last_latency = port_history.get(host, None)
                    if last_latency != advertised_latency:
                        need_send = True

                if need_send:
                    self.send_route(p, host, advertised_latency)
                    # 更新历史记录
                    if p not in self.history:
                        self.history[p] = {}
                    self.history[p][host] = advertised_latency
        ##### End Stages 3, 6, 7, 8, 10 #####

    def expire_routes(self):
        """
        Clears out expired routes from table.
        accordingly.
        """
        
        ##### Begin Stages 5, 9 #####
        for host, entry in list(self.table.items()):
            if api.current_time() >= entry.expire_time:
                if self.POISON_EXPIRED is True:
                    # self.table.pop(host)
                    self.table[host] = TableEntry(
                        dst=entry.dst,
                        port=entry.port,
                        latency=INFINITY,
                        expire_time=api.current_time() + self.ROUTE_TTL
                    )
                else:
                    self.table.pop(host)
                    # 清理历史记录中已删除的路由
                    for port in self.history:
                        if host in self.history[port]:
                            del self.history[port][host]
        ##### End Stages 5, 9 #####

    def handle_route_advertisement(self, route_dst, route_latency, port):
        """
        Called when the router receives a route advertisement from a neighbor.

        :param route_dst: the destination of the advertised route.
        :param route_latency: latency from the neighbor to the destination.
        :param port: the port that the advertisement arrived on.
        :return: nothing.
        """
        
        ##### Begin Stages 4, 10 #####
        latency = route_latency + self.ports.get_latency(port)
        if latency > INFINITY:
            latency = INFINITY
        flag = False
        if route_dst not in self.table:
            self.table[route_dst] = TableEntry(route_dst, port, latency, api.current_time()+self.ROUTE_TTL)
            flag = True
        elif port is self.table[route_dst].port:
            self.table[route_dst] = TableEntry(route_dst, port, latency, api.current_time()+self.ROUTE_TTL)
            flag = True
        elif latency < self.table[route_dst].latency:
            self.table[route_dst] = TableEntry(route_dst, port, latency, api.current_time()+self.ROUTE_TTL)
            flag = True
        if flag is True:
            self.send_routes(force=False)
        ##### End Stages 4, 10 #####

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this router goes up.

        :param port: the port that the link is attached to.
        :param latency: the link latency.
        :returns: nothing.
        """
        self.ports.add_port(port, latency)

        ##### Begin Stage 10B #####
        if self.SEND_ON_LINK_UP:
            self.send_routes(force=True, single_port=port)
        ##### End Stage 10B #####

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this router goes down.

        :param port: the port number used by the link.
        :returns: nothing.
        """
        self.ports.remove_port(port)

        ##### Begin Stage 10B #####
        updated = False  # 标记是否有路由被修改
        # 处理所有使用该端口的路由
        for host in list(self.table.keys()):
            entry = self.table[host]
            if entry.port == port:
                if self.POISON_ON_LINK_DOWN:
                    # 毒化路由
                    self.table[host] = TableEntry(
                        dst=host,
                        port=port,
                        latency=INFINITY,
                        expire_time=api.current_time() + self.ROUTE_TTL
                    )
                else:
                    # 删除路由并清理历史记录
                    self.table.pop(host)
                    for p in self.history:
                        if host in self.history[p]:
                            del self.history[p][host]
                updated = True
        # 触发增量更新
        if updated:
            self.send_routes(force=False)
        ##### End Stage 10B #####

    # Feel free to add any helper methods!
