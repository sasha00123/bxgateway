from bxcommon.exceptions import ParseError
from bxcommon.messages.abstract_message_factory import AbstractMessageFactory
from bxgateway import eth_constants
from bxgateway.messages.eth.protocol.block_bodies_eth_protocol_message import BlockBodiesEthProtocolMessage
from bxgateway.messages.eth.protocol.block_headers_eth_protocol_message import BlockHeadersEthProtocolMessage
from bxgateway.messages.eth.protocol.disconnect_eth_protocol_message import DisconnectEthProtocolMessage
from bxgateway.messages.eth.protocol.eth_protocol_message import EthProtocolMessage
from bxgateway.messages.eth.protocol.eth_protocol_message_type import EthProtocolMessageType
from bxgateway.messages.eth.protocol.get_block_bodies_eth_protocol_message import GetBlockBodiesEthProtocolMessage
from bxgateway.messages.eth.protocol.get_block_headers_eth_protocol_message import GetBlockHeadersEthProtocolMessage
from bxgateway.messages.eth.protocol.hello_eth_protocol_message import HelloEthProtocolMessage
from bxgateway.messages.eth.protocol.new_block_eth_protocol_message import NewBlockEthProtocolMessage
from bxgateway.messages.eth.protocol.new_block_hashes_eth_protocol_message import NewBlockHashesEthProtocolMessage
from bxgateway.messages.eth.protocol.ping_eth_protocol_message import PingEthProtocolMessage
from bxgateway.messages.eth.protocol.pong_eth_protocol_message import PongEthProtocolMessage
from bxgateway.messages.eth.protocol.raw_eth_protocol_message import RawEthProtocolMessage
from bxgateway.messages.eth.protocol.status_eth_protocol_message import StatusEthProtocolMessage
from bxgateway.messages.eth.protocol.transactions_eth_protocol_message import TransactionsEthProtocolMessage
from bxgateway.utils.eth.framed_input_buffer import FramedInputBuffer
from bxgateway.utils.eth.rlpx_cipher import RLPxCipher


class EthProtocolMessageFactory(AbstractMessageFactory):
    _MESSAGE_TYPE_MAPPING = {
        EthProtocolMessageType.HELLO: HelloEthProtocolMessage,
        EthProtocolMessageType.DISCONNECT: DisconnectEthProtocolMessage,
        EthProtocolMessageType.PING: PingEthProtocolMessage,
        EthProtocolMessageType.PONG: PongEthProtocolMessage,
        EthProtocolMessageType.STATUS: StatusEthProtocolMessage,
        EthProtocolMessageType.TRANSACTIONS: TransactionsEthProtocolMessage,
        EthProtocolMessageType.NEW_BLOCK_HASHES: NewBlockHashesEthProtocolMessage,
        EthProtocolMessageType.GET_BLOCK_HEADERS: GetBlockHeadersEthProtocolMessage,
        EthProtocolMessageType.BLOCK_HEADERS: BlockHeadersEthProtocolMessage,
        EthProtocolMessageType.GET_BLOCK_BODIES: GetBlockBodiesEthProtocolMessage,
        EthProtocolMessageType.BLOCK_BODIES: BlockBodiesEthProtocolMessage,
        EthProtocolMessageType.NEW_BLOCK: NewBlockEthProtocolMessage,
    }

    def __init__(self, rlpx_cipher):

        if not isinstance(rlpx_cipher, RLPxCipher):
            raise TypeError("Argument rlpx_cipher is expected to be of type RLPxCipher but was {}"
                            .format(type(rlpx_cipher)))

        super(EthProtocolMessageFactory, self).__init__()

        self.message_type_mapping = self._MESSAGE_TYPE_MAPPING
        self.base_message_type = EthProtocolMessage

        self._framed_input_buffer = FramedInputBuffer(rlpx_cipher)

        self._expected_msg_type = None

    def set_expected_msg_type(self, msg_type):
        if not msg_type in [EthProtocolMessageType.AUTH, EthProtocolMessageType.AUTH_ACK]:
            raise ValueError("msg_type can be AUTH or AUTH_ACK")

        self._expected_msg_type = msg_type

    def reset_expected_msg_type(self):
        self._expected_msg_type = None

    def get_message_header_preview(self, input_buffer):
        """
        Peeks at a message, determining if its full.
        Returns (is_full_message, command, payload_length)
        """
        if self._expected_msg_type == EthProtocolMessageType.AUTH:

            return True, EthProtocolMessageType.AUTH, input_buffer.length
        elif self._expected_msg_type == EthProtocolMessageType.AUTH_ACK and \
            input_buffer.length >= eth_constants.ENC_AUTH_ACK_MSG_LEN:

            return True, EthProtocolMessageType.AUTH_ACK, eth_constants.ENC_AUTH_ACK_MSG_LEN
        elif self._expected_msg_type is None:

            is_full_msg, command = self._framed_input_buffer.peek_message(input_buffer)

            if is_full_msg:
                return True, command, 0

        return False, None, None

    def create_message_from_buffer(self, buf):
        """
        Parses a full message from a buffer based on its command into one of the loaded message types.
        """

        if self._expected_msg_type is not None:
            return self.base_message_type.initialize_class(RawEthProtocolMessage, buf, None)

        if len(buf) != 0:
            raise ParseError("All bytes are expected to be already read by self._framed_input_buffer")

        message_bytes, command = self._framed_input_buffer.get_full_message()

        message_cls = self.message_type_mapping[command]

        return self.base_message_type.initialize_class(message_cls, message_bytes, None)
