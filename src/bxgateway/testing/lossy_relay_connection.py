from bxcommon.utils import logger
from bxgateway.connections.abstract_relay_connection import AbstractRelayConnection


class LossyRelayConnection(AbstractRelayConnection):
    def __init__(self, sock, address, node, from_me=False, setup=False):
        super(LossyRelayConnection, self).__init__(sock, address, node, setup)

        logger.debug("Test mode: Client is started in test mode. Simulating dropped transactions.")

        self.tx_drop_counter = 0
        self.tx_assign_drop_counter = 0
        self.tx_unknown_txs_drop_counter = 0

    def msg_tx(self, msg):

        self.tx_drop_counter += 1

        # Drop every 10th message
        if self.tx_drop_counter > 0 and self.tx_drop_counter % 10 == 0:
            self.tx_drop_counter = 0
            logger.debug("Test mode: Dropping transaction message.")
        else:
            super(LossyRelayConnection, self).msg_tx(msg)

    def msg_txs(self, msg):
        self.tx_unknown_txs_drop_counter += 1

        # Drop every 3rd message
        if self.tx_unknown_txs_drop_counter > 0 and self.tx_unknown_txs_drop_counter % 3 == 0:
            self.tx_unknown_txs_drop_counter = 0
            logger.debug("Test mode: Dropping unknown txs message.")
        else:
            super(LossyRelayConnection, self).msg_txs(msg)
