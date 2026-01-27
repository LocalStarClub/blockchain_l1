import hashlib
import json
from time import time
from typing import List, Dict

# Класс блока
# __init__ - конструктор. с его помощью я инициализирую атрибуты
# self - ссылка на экземпляр класса, через него обращаюсь к атрибутам и методам
class Block:
    def __init__(self, index: int, transactions: List[Dict], proof: int, previous_hash: str):
        # конструктор блока
        self.index = index # сохраняем переданый индекс в атрибут
        self.timestamp = time()
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash

    def hash(self) -> str:
        block_string = json.dumps(self.__dict__, sort_keys=True).encode() # превращаем блок в жсон и кодируем в байты
        return hashlib.sha256(block_string).hexdigest() # возвращаем хэш
    
# Класс блокчейна
class Blockchain:
    def __init__(self):
        # конструктор блокчейна 
        self.chain = List[Block] = [] # иниц. цепочку как список
        self.current_transactions: List[Dict] = [] # список транзакций
        self.nodes = set() # иниц. множество узлов
        self.create_genesis_block() # генезис-блок

    def create_genesis_block(self):
        # первый (генезис) блок
        genesis_block = Block(0, [], 0, 0) # блок с инд. 0, пустыми транзакциями
        self.chain.append(genesis_block) # добавляем в цепочку

    def new_block(self, proof: int) -> Block:
        block = Block(
            index=len(self.chain), # индекс - длина цепочки
            transactions=self.current_transactions, # транзакции из текущего списка
            proof=proof, # пруфы
            previous_hash=self.last_block.hash() # хэш ласт блока
        )
        self.current_transactions = [] # очищаем список текущих транзакций
        self.chain.append(block) # добавляем блок в цепочку
        return block # возвращаем созданный блок
    
    def proof_of_work(self, last_proof: int) -> int:
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof
    
    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        # статикметод проверки
        guess = f'{last_proof}{proof}'.encode() # создаем строку из пруфов и кодируем в байты
        guess_hash = hashlib.sha256(guess).hexdigest() # вычисляем хэш
        return guess_hash[:4] == '0000' # проверяем, начинается ли хэш с 0000
    
    @property
    def last_block(self) -> Block:
        return self.chain[-1] # последний элемент списка цепочки
    
    def new_transaction(self, sender: str, recipient: str, amount: float) -> int:
        # Метод для добавления новой транзакции
        self.current_transactions.append({  # Добавляем транзакцию в список текущих транзакций
            'sender': sender,  # Отправитель
            'recipient': recipient,  # Получатель
            'amount': amount,  # Сумма
        })
        return self.last_block.index + 1  # Возвращаем индекс блока, в который будет включена транзакция

    def add_node(self, address: str):
        # Метод для добавления новой ноды в сеть
        self.nodes.add(address)  # Добавляем адрес ноды в множество nodes

    def resolve_conflicts(self) -> bool:
        # Метод для разрешения конфликтов (консенсус)
        neighbours = self.nodes  # Получаем список всех нод
        new_chain = None  # Инициализируем переменную для новой цепочки
        max_length = len(self.chain)  # Запоминаем длину текущей цепочки

        for node in neighbours:  # Проходим по всем нодам
            response = requests.get(f'http://{node}/chain')  # Запрашиваем цепочку у ноды
            if response.status_code == 200:  # Если запрос успешен
                length = response.json()['length']  # Получаем длину цепочки
                chain = response.json()['chain']  # Получаем саму цепочку

                if length > max_length and self.valid_chain(chain):  # Если цепочка длиннее и валидна
                    max_length = length  # Обновляем максимальную длину
                    new_chain = chain  # Запоминаем новую цепочку

        if new_chain:  # Если найдена новая цепочка
            self.chain = new_chain  # Заменяем текущую цепочку на новую
            return True  # Возвращаем True, если цепочка была заменена
        return False  # Возвращаем False, если замена не потребовалась

    def valid_chain(self, chain: List[Block]) -> bool:
        # Метод для проверки валидности цепочки блоков
        last_block = chain[0]  # Начинаем с первого блока
        current_index = 1  # Переходим ко второму блоку

        while current_index < len(chain):  # Проходим по всем блокам
            block = chain[current_index]  # Получаем текущий блок
            if block.previous_hash != last_block.hash():  # Проверяем, совпадает ли хеш предыдущего блока
                return False  # Если нет, цепочка невалидна
            if not self.valid_proof(last_block.proof, block.proof):  # Проверяем Proof of Work
                return False  # Если Proof of Work невалиден, цепочка невалидна
            last_block = block  # Переходим к следующему блоку
            current_index += 1  # Увеличиваем индекс

        return True  # Если все блоки валидны, возвращаем True
    

