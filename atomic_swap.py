"""This is a Atomic Swap smart contract."""

from pyteal import *

# Variables for the seller and buyer accounts, as well as the secret code, time out when the contract is nullified and then the fee.

secret_code = Bytes("base16", "83532373272375828")
time_out = 800000
fee = 333
joshua = Addr("6ZHGHH5Z5CTPCF5WCESXMGRSVK7QJETR63M3NY5FJCUYDHO57VTCMJOBGY")
susan = Addr("7Z5PWO2C6LFNQFGHWKSK5H47IQP5OJW2M3HA2QPXTY3WTNP5NU2MHBW27M")

# Program stores a value in a account on the blockchain and sets a code where once the seller of the service receives the code, they may access the funds immediately.

def hashed_timelock_contract(
    contract_seller=joshua,
    contract_buyer=susan,
    contract_fee=fee,
    contract_secret=secret_code,
    contract_hash_fn=Sha256,
    contract_timeout=time_out,
):
    fee_cond = Txn.fee() < Int(contract_fee)
    safety_cond = And(
        Txn.type_enum() == TxnType.Payment,
        Txn.close_remainder_to() == Global.zero_address(),
        Txn.rekey_to() == Global.zero_address(),
    )
    recv_cond = And(Txn.receiver() == contract_seller, contract_hash_fn(Arg(0)) == contract_secret)
    esc_cond = And(Txn.receiver() == contract_buyer, Txn.first_valid() > Int(contract_timeout))
    return And(fee_cond, safety_cond, Or(recv_cond, esc_cond))

# Compiles the smart contract into the TEAL programming language, this is what the AVM is able to read.

if __name__ == "__main__":
    print(compileTeal(hashed_timelock_contract(), mode=Mode.Signature, version=2))