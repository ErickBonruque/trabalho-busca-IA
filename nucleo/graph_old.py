"""
Módulo responsável pela representação do grafo do ambiente.
Define tipos de terreno, nós, arestas e custos de deslocamento.
"""

from enum import Enum
from collections import defaultdict, deque
import random


class TipoTerreno(Enum):
    """Enumera os tipos de terreno e seus custos de deslocamento"""
    SOLIDO = (1, '.')    # Custo 1, símbolo '.'
    ARENOSO = (4, '~')   # Custo 4, símbolo '~'
    ROCHOSO = (10, '^')  # Custo 10, símbolo '^'
    PANTANO = (20, '&')  # Custo 20, símbolo '&'
    
    def __init__(self, custo, simbolo):
        self.custo = custo
        self.simbolo = simbolo


class No:
    """Representa um nó (vértice) no grafo"""
    
    def __init__(self, x, y, tipo_terreno=TipoTerreno.SOLIDO):
        self.x = x
        self.y = y
        self.tipo_terreno = tipo_terreno
        self.tem_recompensa = False
        self.recompensa_coletada = False
        
    def __str__(self):
        return f"No({self.x}, {self.y}, {self.tipo_terreno.name})"
        
    def __eq__(self, other):
        return isinstance(other, No) and self.x == other.x and self.y == other.y
        
    def __hash__(self):
        return hash((self.x, self.y))
        
    def obter_simbolo(self):
        """Retorna o símbolo visual do nó"""
        if self.tem_recompensa and not self.recompensa_coletada:
            return '$'  # Recompensa disponível
        elif self.recompensa_coletada:
            return '*'  # Recompensa coletada
        return self.tipo_terreno.simbolo


class Graph:
    """Representa o grafo do ambiente com nós, arestas e custos"""
    
    def __init__(self):
        self.nos = {}  # Dicionário {(x, y): No}
        self.adjacencias = defaultdict(list)  # {no: [(vizinho, custo), ...]}
        self.largura = 0
        self.altura = 0
        
    def adicionar_no(self, x, y, tipo_terreno=TipoTerreno.SOLIDO):
        """Adiciona um nó ao grafo"""
        no = No(x, y, tipo_terreno)
        self.nos[(x, y)] = no
        self.largura = max(self.largura, x + 1)
        self.altura = max(self.altura, y + 1)
        return no
        
    def obter_no(self, x, y):
        """Retorna o nó nas coordenadas especificadas"""
        return self.nos.get((x, y))
        
    def conectar_nos(self, no1, no2):
        """Conecta dois nós com arestas bidirecionais"""
        if no1 not in self.nos.values() or no2 not in self.nos.values():
            return False
            
        # Custo da aresta é baseado no terreno de destino
        custo1_para_2 = no2.tipo_terreno.custo
        custo2_para_1 = no1.tipo_terreno.custo
        
        # Adiciona conexões bidirecionais
        self.adjacencias[no1].append((no2, custo1_para_2))
        self.adjacencias[no2].append((no1, custo2_para_1))
        return True
        
    def obter_vizinhos(self, no):
        """Retorna lista de vizinhos e custos: [(vizinho, custo), ...]"""
        return self.adjacencias.get(no, [])
        
    def validar_conectividade(self):
        """Verifica se todos os nós são alcançáveis usando BFS"""
        if not self.nos:
            return False
            
        # Pega o primeiro nó como início
        no_inicial = next(iter(self.nos.values()))
        visitados = set()
        fila = deque([no_inicial])
        visitados.add(no_inicial)
        
        while fila:
            no_atual = fila.popleft()
            for vizinho, _ in self.obter_vizinhos(no_atual):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)
                    
        # Verifica se todos os nós foram visitados
        return len(visitados) == len(self.nos)
        
    def definir_recompensa(self, x, y):
        """Define que um nó possui uma recompensa"""
        no = self.obter_no(x, y)
        if no:
            no.tem_recompensa = True
            return True
        return False
        
    def coletar_recompensa(self, x, y):
        """Marca uma recompensa como coletada"""
        no = self.obter_no(x, y)
        if no and no.tem_recompensa and not no.recompensa_coletada:
            no.recompensa_coletada = True
            return True
        return False
        
    def resetar_recompensas(self):
        """Reseta o estado de todas as recompensas"""
        for no in self.nos.values():
            no.recompensa_coletada = False
            
    def obter_nos_com_recompensa(self):
        """Retorna lista de nós que possuem recompensas"""
        return [no for no in self.nos.values() if no.tem_recompensa]
        
    def obter_todos_nos(self):
        """Retorna lista de todos os nós do grafo"""
        return list(self.nos.values())
        
    def distancia_manhattan(self, no1, no2):
        """Calcula distância Manhattan entre dois nós"""
        return abs(no1.x - no2.x) + abs(no1.y - no2.y)
        
    def __str__(self):
        return f"Grafo({len(self.nos)} nós, {self.largura}x{self.altura})"


def gerar_grafo_teste(tamanho_min=30, largura=8, altura=6):
    """
    Gera um grafo de teste conectado com distribuição variada de terrenos
    """
    grafo = Graph()
    
    # Gera grid básico com terrenos aleatórios
    for y in range(altura):
        for x in range(largura):
            # Distribui tipos de terreno com probabilidades
            rand = random.random()
            if rand < 0.4:
                tipo = TipoTerreno.SOLIDO
            elif rand < 0.6:
                tipo = TipoTerreno.ARENOSO
            elif rand < 0.8:
                tipo = TipoTerreno.ROCHOSO
            else:
                tipo = TipoTerreno.PANTANO
                
            grafo.adicionar_no(x, y, tipo)
    
    # Conecta nós adjacentes (4-conectividade)
    for y in range(altura):
        for x in range(largura):
            no_atual = grafo.obter_no(x, y)
            if not no_atual:
                continue
                
            # Conecta com vizinhos (norte, sul, leste, oeste)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                novo_x, novo_y = x + dx, y + dy
                if 0 <= novo_x < largura and 0 <= novo_y < altura:
                    vizinho = grafo.obter_no(novo_x, novo_y)
                    if vizinho:
                        grafo.conectar_nos(no_atual, vizinho)
    
    # Valida conectividade
    if not grafo.validar_conectividade():
        print("Aviso: Grafo gerado não é completamente conectado!")
        
    # Distribui recompensas aleatoriamente (mínimo 5)
    nos_disponiveis = list(grafo.nos.values())
    num_recompensas = max(5, len(nos_disponiveis) // 6)
    
    nos_com_recompensa = random.sample(nos_disponiveis, num_recompensas)
    for no in nos_com_recompensa:
        no.tem_recompensa = True
        
    print(f"Grafo gerado: {len(grafo.nos)} nós, {num_recompensas} recompensas")
    return grafo


# Teste básico do módulo
if __name__ == "__main__":
    print("Testando módulo graph.py...")
    
    # Gera grafo de teste
    grafo = gerar_grafo_teste()
    
    # Testa funcionalidades básicas
    print(f"Grafo criado: {grafo}")
    print(f"Conectividade: {'OK' if grafo.validar_conectividade() else 'FALHA'}")
    print(f"Recompensas: {len(grafo.obter_nos_com_recompensa())}")
    
    # Testa um nó específico
    no_teste = grafo.obter_no(0, 0)
    if no_teste:
        print(f"Nó (0,0): {no_teste}")
        vizinhos = grafo.obter_vizinhos(no_teste)
        print(f"Vizinhos: {len(vizinhos)}")
