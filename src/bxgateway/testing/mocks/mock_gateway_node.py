from bxcommon.connections.connection_pool import ConnectionPool
from bxcommon.connections.connection_type import ConnectionType
from bxcommon.connections.node_type import NodeType
from bxcommon.constants import DEFAULT_NETWORK_NUM
from bxcommon.services.transaction_service import TransactionService
from bxcommon.utils.alarm import AlarmQueue
from bxgateway.connections.abstract_gateway_node import AbstractGatewayNode


class MockGatewayNode(AbstractGatewayNode):
    def get_remote_blockchain_connection_cls(self):
        pass

    def get_blockchain_connection_cls(self):
        pass

    def get_relay_connection_cls(self):
        pass

    NODE_TYPE = NodeType.GATEWAY

    def __init__(self, opts):
        self.opts = opts
        self.alarm_queue = AlarmQueue()
        self.connection_pool = ConnectionPool()
        self.network_num = DEFAULT_NETWORK_NUM
        self.idx = 1

        self.broadcast_messages = []
        super(MockGatewayNode, self).__init__(opts)

        self._tx_service = TransactionService(self)

    def broadcast(self, msg, requester=None, prepend_to_queue=False, network_num=None,
                  connection_type=ConnectionType.RELAY):
        self.broadcast_messages.append((msg, connection_type))
        return []

    def get_tx_service(self, _network_num=None):
        return self._tx_service