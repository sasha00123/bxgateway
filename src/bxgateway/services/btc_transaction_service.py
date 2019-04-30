from bxcommon.services.transaction_service import TransactionService
import task_pool_executor as tpe  # pyre-ignore for now, figure this out later (stub file or Python wrapper?)


class BtcTransactionService(TransactionService):

    def __init__(self, node, network_num):
        super(BtcTransactionService, self).__init__(node, network_num)
        self.cpp_tx_hash_to_short_ids = tpe.Sha256ToShortIDMap()

    def assign_short_id(self, transaction_hash, short_id):
        super(BtcTransactionService, self).assign_short_id(transaction_hash, short_id)
        cpp_hash = tpe.Sha256(tpe.InputBytes(transaction_hash.binary))
        self.cpp_tx_hash_to_short_ids[cpp_hash] = short_id

    def _remove_transaction_by_short_id(self, short_id):
        if short_id in self._short_id_to_tx_hash:
            transaction_hash = self._short_id_to_tx_hash.pop(short_id)
            if transaction_hash in self._tx_hash_to_short_ids:
                short_ids = self._tx_hash_to_short_ids[transaction_hash]

                # Only clear mapping and _tx_hash_to_contents if last SID assignment
                if len(short_ids) == 1:
                    del self._tx_hash_to_short_ids[transaction_hash]
                    cpp_hash = tpe.Sha256(tpe.InputBytes(transaction_hash.binary))
                    del self.cpp_tx_hash_to_short_ids[cpp_hash]
                    if transaction_hash in self._tx_hash_to_contents:
                        del self._tx_hash_to_contents[transaction_hash]
                else:
                    short_ids.remove(short_id)