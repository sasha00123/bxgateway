import rlp

from bxgateway import eth_constants
from bxgateway.utils.eth import crypto_utils


class BlockHeader(rlp.Serializable):
    fields = [
        ("prev_hash", rlp.sedes.Binary.fixed_length(eth_constants.BLOCK_HASH_LEN)),
        ("uncles_hash", rlp.sedes.Binary.fixed_length(eth_constants.BLOCK_HASH_LEN)),
        ("coinbase", rlp.sedes.Binary.fixed_length(eth_constants.ADDRESS_LEN, allow_empty=True)),
        ("state_root", rlp.sedes.Binary.fixed_length(eth_constants.MERKLE_ROOT_LEN, allow_empty=True)),
        ("tx_list_root", rlp.sedes.Binary.fixed_length(eth_constants.MERKLE_ROOT_LEN, allow_empty=True)),
        ("receipts_root", rlp.sedes.Binary.fixed_length(eth_constants.MERKLE_ROOT_LEN, allow_empty=True)),
        ("bloom", rlp.sedes.BigEndianInt(eth_constants.BLOOM_LEN)),
        ("difficulty", rlp.sedes.big_endian_int),
        ("number", rlp.sedes.big_endian_int),
        ("gas_limit", rlp.sedes.big_endian_int),
        ("gas_used", rlp.sedes.big_endian_int),
        ("timestamp", rlp.sedes.big_endian_int),
        ("extra_data", rlp.sedes.binary),
        ("mix_hash", rlp.sedes.binary),
        ("nonce", rlp.sedes.binary)
    ]

    def hash(self):
        """The binary block hash"""
        return crypto_utils.keccak_hash(rlp.encode(self))
