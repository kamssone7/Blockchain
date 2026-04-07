# ══════════════════════════════════════════════════════════════════#
#  TP1 — Mini-Blockchain Python — M1 RIST UFHB                      # 
#  Auteur : Dao Karim                                               #
# ══════════════════════════════════════════════════════════════════#

import hashlib
import json
import time
from datetime import datetime

'''1.Implementons la classe Transaction'''
class Transaction:
    '''represente une transaction simplifiee dans la blockchain.'''
    
    def __init__(self,from_:str,to:str,amount:float):
        self.from_=from_
        self.to=to
        self.amount=amount 
        self.timestamp=time.time()
        self.tx_id=self._calculate_id()

    def _calculate_id(self)->str:
        '''calcule un identifiant unique pour la transaction en utilisant le hashage.'''
        tx_data=json.dumps({
            "from": self.from_,
            "to": self.to,
            "amount": self.amount,
            "timestamp": self.timestamp

        }, sort_keys=True)
        return hashlib.sha256(tx_data.encode()).hexdigest()
    
    def to_dict(self)->dict:
        '''convertit la transaction en un dictionnaire pour faciliter le stockage et la manipulation.'''
        return {
            "from": self.from_,
            "to": self.to,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "tx_id": self.tx_id
        }
    
    def __repr__(self)->str:
        dt= datetime.fromtimestamp(self.timestamp).strftime('%H:%M:%S')
        return (f"Tx[{self.tx_id[:8]}...]"
                 f" {self.from_} -> {self.to} : {self.amount} BTC @ {dt}")
    
'''2.Implementons la classe Block'''
class Block:
    '''represente un bloc dans la blockchain.'''
    
    def __init__(self,index:int,transactions:list,previous_hash:str='0'*64):
        self.index=index
        self.transactions=transactions   #liste de transactions
        self.previous_hash=previous_hash
        self.timestamp=time.time()
        self.nonce=0  #sera incremente lors du minage
        self.hash=self.calculate_hash()

    def calculate_hash(self)->str:
        '''calcule le SHA-256 du bloc .
        Inclut tous kes les champs: index, transactions, previous_hash, timestamp et nonce.'''
        block_data=json.dumps({
            "index": self.index,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_data.encode()).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
         target = '0' * difficulty 
         start_time = time.time()
         attempts = 0 
         print(f' Minage du bloc #{self.index}...') 
         while not self.hash.startswith(target): 
            self.nonce += 1 
            self.hash = self.calculate_hash()
            attempts += 1 
         elapsed = time.time() - start_time 
         print(f' Bloc #{self.index} miné en {elapsed:.3f}s' 
               f' | nonce={self.nonce:,}'
               f' | {attempts:,} tentatives' 
               f' | hash={self.hash[:16]}...')
            
    def __repr__(self) -> str:
        return (f"Block #{self.index} | "
                f"{len(self.transactions)} tx | "
                f"nonce={self.nonce} | "
                f"hash={self.hash[:12]}... | ")

'''3.Implementons la classe Blockchain'''
class Blockchain:
    "Gere la chaine de blocs complete."
    def __init__(self, difficulty: int = 3):
        self.difficulty = difficulty
        self.chain = []
        self.pending_tx = []  #tranctions en attente de confirmartion
        self._create_genesis_block()
    
    def _create_genesis_block(self) -> None:
         genesis = Block(0, [], '0'*64) 
         genesis.mine_block(self.difficulty)
         self.chain.append(genesis)

    @property 
    def last_block(self) -> Block:
        return self.chain[-1] 

    def add_transaction(self, tx: Transaction) -> None: 
        self.pending_tx.append(tx) 

    def add_block(self, miner: str = 'Miner') -> Block: 
        if not self.pending_tx: 
            print('[WARN] Bloc vide') 

        coinbase = Transaction('COINBASE', miner, 6.25) 
        txs = [coinbase] + self.pending_tx 

        new_block = Block(
            index=len(self.chain),
            transactions=txs, 
            previous_hash=self.last_block.hash
        )

        new_block.mine_block(self.difficulty) 
        self.chain.append(new_block) 
        self.pending_tx = []

        return new_block

    def get_balance(self, address: str) -> float: 
        balance = 0.0 
        for block in self.chain: 
            for tx in block.transactions: 
                if tx.from_ == address: 
                    balance -= tx.amount 
                if tx.to == address: 
                    balance += tx.amount 
        return balance 

    def is_chain_valid(self) -> bool: 
        for i in range(1, len(self.chain)): 
            curr = self.chain[i] 
            prev = self.chain[i - 1] 
            if curr.hash != curr.calculate_hash(): 
                return False 
            if curr.previous_hash != prev.hash: 
                return False 
        return True 

    def detect_tampering(self) -> list: 
        corrupted = [] 
        for i in range(1, len(self.chain)): 
            curr = self.chain[i] 
            prev = self.chain[i - 1] 
            if curr.hash != curr.calculate_hash(): 
                corrupted.append((i, "HASH_INVALIDE")) 
            elif curr.previous_hash != prev.hash: 
                corrupted.append((i, "CHAINAGE_INVALIDE")) 
        return corrupted 

    def display_chain(self) -> None: 
        print('\n' + '='*60) 
        print(f'BLOCKCHAIN | {len(self.chain)} blocs | difficulté={self.difficulty}') 
        print('='*60) 
        for block in self.chain: 
            print(f'[{block.index}] hash={block.hash[:16]}... '
                  f'prev={block.previous_hash[:16]}... '
                  f'nonce={block.nonce} txs={len(block.transactions)}') 
        print('='*60 + '\n') 


# =============================================================== 
# # 4. MAIN — SCÉNARIO DE DÉMONSTRATION COMPLET 
# # ===============================================================
if __name__ == '__main__': 
    print("\n=== INITIALISATION ===")
    bc = Blockchain(difficulty=3) 

    print("\n=== AJOUT TRANSACTIONS ===") 
    bc.add_transaction(Transaction('Alice', 'Bob', 2.0)) 
    bc.add_transaction(Transaction('Alice', 'Carol', 1.0)) 
    bc.add_transaction(Transaction('Bob', 'Dave', 0.5)) 

    print("\n=== MINAGE BLOC 1 ===") 
    bc.add_block(miner='Miner1') 

    print("\n=== AJOUT TRANSACTIONS ===") 
    bc.add_transaction(Transaction('Dave', 'Alice', 0.2)) 
    bc.add_transaction(Transaction('Carol', 'Bob', 0.3)) 

    print("\n=== MINAGE BLOC 2 ===") 
    bc.add_block(miner='Miner2') 

    print("\n=== BLOCKCHAIN ===") 
    bc.display_chain() 

    print("Chaîne valide ?", bc.is_chain_valid()) 

    print("\n=== SOLDES ===") 
    for user in ['Alice', 'Bob', 'Carol', 'Dave', 'Miner1', 'Miner2']: 
        print(f"{user}: {bc.get_balance(user):.4f} BTC") 

    print("\n=== ATTAQUE ===") 
    bc.chain[1].transactions[1].amount = 100 # fraude 

    print("Chaîne valide après attaque ?", bc.is_chain_valid()) 

    corrupted = bc.detect_tampering() 
    for c in corrupted: 
        print("Bloc corrompu:", c)

    print("\n=== TEST PROOF OF WORK ===")

    tx_list = [
    Transaction('Alice', 'Bob', 0.5),
    Transaction('Bob', 'Carol', 0.3),
]

for diff in [2, 3, 4, 5]:
  print(f"\n--- Difficulté {diff} ---")
  b = Block(index=1, transactions=tx_list)
  b.mine_block(difficulty=diff)

#b.mine_block(difficulty=19) essaie avec 19

""" Reponse aux questions du TP1:"""


'''Question TP1.1 — Pourquoi deux transactions identiques 
(même from, to, amount) ont-elles des tx_id différents ?
 Quel attribut provoque cette différence ?'''

# La raison pour laquelle deux transactions identiques ont des tx_id différents est l'attribut
#  "timestamp"

"""Question TP1.2 — 
Pourquoi le nonce est-il inclus dans le calcul du hash ? 
Qu'est-ce qui se passerait si on ne l'incluait pas ?"""

# Le nonce est inclus dans le calcul du hash pour permettre le processus de minage.
# lorsqu'on n'inclut pas le nonce dans le calcul du hash, 
# le hash du bloc serait toujours le même pour les mêmes transactions 
# et le même previous_hash.

'''Question TP1.3 — 
Notez les temps de minage pour chaque niveau de difficulté dans le tableau :

selon mes tests sur ma machine, voici les temps de minage pour chaque niveau de difficulté:'''

''' Difficulté	       Temps (s)	 Nonce trouvé	             Observations'''
#       2			   0.001s         59              Le minage est très rapide, le nonce trouvé est faible.
#       3			   0.134s        6639            Le minage prend plus de temps, le nonce trouvé est plus élevé.
#       4			   4.936s        225907          Le minage devient significativement plus long, le nonce trouvé est très élevé.
#       5		       7.223s        360090          Le minage est encore plus long, le nonce trouvé est extrêmement élevé.


'''Question TP1.4 — 
Bitcoin utilise une difficulté équivalente à 19+ zéros hexadécimaux au début du hash. 
Avec votre machine, estimez combien de temps prendrait le minage d'un bloc Bitcoin.'''

# Avec le constat que j'ai fait plus le niveau de difficulté augmente,
#  le temps de minage augmente de manière exponentielle.selon mes tests sur ma machine, 
# le minage d'un bloc avec une difficulté de 5 prend environ 7.223 secondes.
#lorsque je fais un test avec une difficulté de 19, le temps de minage devient astronomique,
#  dépassant largement les capacités de calcul de ma machine.et rien ne s'affiche après plusieurs heures d'attente.
#Donc j'en deduis que le minage d'un bloc Bitcoin avec une difficulté de 19+ zéros hexadécimaux prendrait des années,
#  voire des décennies, sur une machine classique.

'''Question TP1.5 — 
Après avoir modifié bc.chain[1].transactions[1].amount,
 la chaîne est invalide. Si l'attaquant recalcule ensuite 
 bc.chain[1].hash = bc.chain[1].calculate_hash(), la chaîne redevient-elle valide ? Expliquez.'''

# Non, la chaîne ne redeviendrait pas valide même si l'attaquant recalcule le hash du bloc modifié.
#  En effet, le hash du bloc modifié ne correspondrait plus au hash stocké dans le bloc suivant.
# De plus a cause du timestamp et du nonce qui sont inclus dans le calcul du hash,la chaine ne sera pas la même
#  donc la chaine sera invalide.

'''Question TP1.6 — 
Mempool. Dans notre implémentation, 
add_block() inclut TOUTES les transactions en attente. 
Dans Bitcoin, un bloc est limité à ~4 Mo. 
Proposez une modification de add_block() 
pour n'inclure que les N premières transactions (les plus anciennes) :'''

#max_txs=10
#Modification proposée :
#txs = [coinbase] + self.pending_tx[:max_txs]  # Inclure seulement les N premières transactions

'''Quelle stratégie de sélection Bitcoin utilise-t-il réellement ?'''

# Bitcoin utilise une stratégie de sélection basée sur les frais de transaction.
# Les mineurs sélectionnent généralement les transactions qui offrent les frais les plus élevés par octet.

'''Question TP1.7 — 
Forks. Si deux mineurs trouvent simultanément un bloc valide (#4 pour l'un, #4' pour l'autre),
 comment notre blockchain gère-t-elle ce cas ? Que se passe-t-il dans la réalité avec Bitcoin ?'''

# Dans notre implémentation, si deux mineurs trouvent simultanément un bloc valide,
#  les deux blocs seraient ajoutés à la chaîne, créant ainsi une bifurcation (fork).
#  La chaîne qui reçoit le prochain bloc miné deviendra la chaîne principale, tandis que l'autre bloc sera abandonné.
# Dans la réalité avec Bitcoin, lorsqu'un fork se produit, les mineurs continuent à miner sur la chaîne qu'ils ont reçue en premier.


'''Question TP1.8 — 
Extension optionnelle .
(Pour aller plus loin) Ajoutez une classe Wallet avec une paire de clés 
(clé privée + clé publique) en utilisant la bibliothèque cryptography '''

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
'''il faudrait penser a installer la bibliothèque cryptography'''
class Wallet:
    def __init__(self):
        self.private_key = ec.generate_private_key(ec.SECP256K1())
        self.public_key  = self.private_key.public_key()
        self.address     = self._derive_address()
    def _derive_address(self) -> str:
        pub_bytes = self.public_key.public_bytes(
            serialization.Encoding.X962,
            serialization.PublicFormat.CompressedPoint
        )
        return hashlib.sha256(pub_bytes).hexdigest()[:40]   # adresse simplifiée

    def sign(self, data: bytes) -> bytes:
        return self.private_key.sign(data, ec.ECDSA(hashes.SHA256()))
    def verify(self, signature: bytes, data: bytes) -> bool:
        try:
            self.public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False
        
'''
# Intégration avec Transaction :
# - alice.sign(json.dumps(tx.to_dict()).encode()) → signature
# - bob.verify(signature, message) → True/False
vue que pour les tests le code pour bob et alice n'etait pas en python
j'ai adapté le code pour que les test soient en python et que ça puisse fonctionner avec la classe Wallet que j'ai implémenté.
'''

# Intégration avec Transaction :
print("\n=== TEST WALLET ===")

# Création de deux wallets
alice = Wallet()
bob = Wallet()

print("Adresse Alice:", alice.address)
print("Adresse Bob  :", bob.address)

# Création d'une transaction
tx = Transaction('Alice', 'Bob', 1.5)

# Message à signer
message = json.dumps(tx.to_dict()).encode()

# Signature par Alice
signature = alice.sign(message)

print("Signature créée.")

# Vérification par Alice (normalement True)
print("Signature valide (Alice) ?", alice.verify(signature, message))

# Vérification avec Bob (normalement False)
print("Signature valide (Bob) ?", bob.verify(signature, message))

'''Pour ce Tp je me suis servi de la documentation sur le Tp proposé par le professeur pour pouvoir completer 
les espaces vides et repondre aux questions du Tp1. J'ai aussi copié le code fournit par le professeur et 
installé la bibliothèque (pip install cryptography) cryptography pour implémenter la classe Wallet.

pour le dernier test j'ai juste fait une stimulation.'''

'''Enseignant: Dr N'golo Konate
Matiere: Blockchain
Semestre: 2
Credits: 2'''

