import hashlib
import json
from time import time
from typing import List, Dict



# __init__ - конструктор. с его помощью я инициализирую атрибуты
# self - ссылка на экземпляр класса, через него обращаюсь к атрибутам и методам


# Блокдата - смысловое "наполнение" передаваемых в блок данных. Участвует в хэшировании (функц def hash)
class BlockData:
    def __init__(self,
                 index: int,
                 timestamp: int,
                 transaction: list,
                 previous_hash: str
                 ):
        self.index = index
        self.timestamp = timestamp
        self.transaction = transaction
        self.previous_hash = previous_hash

    def to_dict(self) -> dict:
        return {
            'index':self.index,
            'timestamp':self.timestamp,
            'transaction':self.transaction,
            'previous_hash':self.previous_hash
        }

    def hash (self) -> str:
        block_string = json.dumps(self.to_dict(),sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


# Класс блока
class Block:
    def __init__(self, data: BlockData):
        self.data = data         # переданные в BlockData данные
        self.hash = data.hash()  # их хэш
        self.signatures = {}     # подписи нод



# Класс ноды
class Node:
    def __init__(self, node_id: str):
        self.node_id = node_id

        # локальное состояние
        self.chain = list[Block] = []
        self.knows_nodes = set[str] = set()

        # Временное хранилище
        self.pending_blocks: dict[str, Block] = {}


    # функция генерации первого блока для всех нод. Всё по нулям для первоначального консенсуса
    def create_genesis_block(self):
        data = BlockData(
            index=0,
            timestamp=0,
            transaction=[],
            previous_hash="0"
        )
        block = Block(data)
        self.chain.append(block)


    # функция получения последнего блока в цепочке (буквально номер блока под номером -1 от текущего)
    def last_block(self) -> Block:
        return self.chain[-1]


    # функция проверки блока
    def validate_block(self, block: Block) -> bool:
        last_block = self.chain[-1]

        if block.data.previous_hash != last_block.hash:
            return False

        if block.hash != block.data.hash():
            return False

        return True


    # функция подписи блока с заглушкой
    def sign_block(self, block: Block):
        block.signatures[self.node_id] = 'подписано'


    # функция приема блока от сети
    def receive_block(self, block: Block):
        if not self.validate_block(block):
            return False

        self.pending_blocks[block.hash] = block
        self.sign_block(block)
        return True


    # функция проверки консенсуса
    def is_block_accepted(self, block: Block) -> bool:
        total_nodes = len(self.known_nodes) + 1  # + self
        required = total_nodes // 2 + 1

        return len(block.signatures) >= required


    # добавление блока в цепочку
    def try_commit_block(self, block_hash: str):
        block = self.pending_blocks.get(block_hash)
        if not block:
            return False

        if self.is_block_accepted(block):
            self.chain.append(block)
            del self.pending_blocks[block_hash]
            return True

        return False