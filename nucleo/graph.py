"""
Módulo responsável pela representação avançada do grafo do ambiente.
Integra geração de labirintos com biomas naturais e distribuição inteligente de recompensas.
"""

from collections import defaultdict, deque
import random
import math
import config

from .maze_generator import gerar_labirinto_conectado
from .biome_generator import gerar_biomas_naturais, TipoTerreno


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
    """Representa o grafo avançado do ambiente com labirinto e biomas"""
    
    def __init__(self):
        self.nos = {}  # Dicionário {(x, y): No}
        self.adjacencias = defaultdict(list)  # {no: [(vizinho, custo), ...]}
        self.largura = 0
        self.altura = 0
        
        # Metadados do processo de geração
        self.maze_grid = None
        self.biome_map = None
        self.caminho_garantido = []
        self.recompensas_caminho_principal = []
        self.recompensas_areas_extras = []
        
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
    
    def obter_todos_nos(self):
        """Retorna todos os nós atualmente cadastrados no grafo"""
        return list(self.nos.values())
        
    def conectar_nos(self, no1, no2):
        """Conecta dois nós considerando o custo do terreno de destino"""
        if no1 not in self.nos.values() or no2 not in self.nos.values():
            return False
            
        # Custo é baseado no terreno de destino
        custo = no2.tipo_terreno.custo
        self.adjacencias[no1].append((no2, custo))
        
        # Conecta bidirecionalmente
        custo_reverso = no1.tipo_terreno.custo
        self.adjacencias[no2].append((no1, custo_reverso))
        
        return True
        
    def obter_vizinhos(self, no):
        """Retorna lista de pares (vizinho, custo) conectados ao nó."""
        return self.adjacencias.get(no, [])
    def obter_custo_aresta(self, no1, no2):
        """Retorna custo da aresta entre dois nós"""
        for vizinho, custo in self.adjacencias[no1]:
            if vizinho == no2:
                return custo
        return float('inf')
        
    def obter_nos_com_recompensa(self):
        """Retorna lista de nós que têm recompensas"""
        return [no for no in self.nos.values() if no.tem_recompensa]
        
    def resetar_recompensas(self):
        """Reseta estado de coleta das recompensas"""
        for no in self.nos.values():
            no.recompensa_coletada = False
            
    def validar_conectividade(self):
        """Valida se todos os nós são alcançáveis usando BFS"""
        if not self.nos:
            return False
            
        # Pega primeiro nó como início
        inicio = next(iter(self.nos.values()))
        visitados = set()
        fila = deque([inicio])
        visitados.add(inicio)
        
        while fila:
            no_atual = fila.popleft()
            for vizinho, _ in self.obter_vizinhos(no_atual):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)
        
        return len(visitados) == len(self.nos)
        
    def calcular_caminho_garantido(self, inicio, objetivo):
        """
        Calcula caminho garantido entre início e objetivo usando BFS
        
        Args:
            inicio, objetivo (No): Nós de início e fim
            
        Returns:
            list[No]: Caminho do início ao objetivo, ou lista vazia se não há caminho
        """
        if inicio not in self.nos.values() or objetivo not in self.nos.values():
            return []
            
        fila = deque([(inicio, [inicio])])
        visitados = {inicio}
        
        while fila:
            no_atual, caminho = fila.popleft()
            
            if no_atual == objetivo:
                self.caminho_garantido = caminho
                return caminho
                
            for vizinho, _ in self.obter_vizinhos(no_atual):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    novo_caminho = caminho + [vizinho]
                    fila.append((vizinho, novo_caminho))
        
        return []
        
    def distancia_manhattan(self, no1, no2):
        """Calcula distância Manhattan entre dois nós"""
        return abs(no1.x - no2.x) + abs(no1.y - no2.y)
        
    def __str__(self):
        return f"Grafo({len(self.nos)} nós, {self.largura}x{self.altura})"


def gerar_grafo_labirinto_com_biomas(tamanho_min=config.MAPA_TAMANHO_MIN, 
                                    largura=config.MAPA_LARGURA, 
                                    altura=config.MAPA_ALTURA, 
                                    seed=config.SEED, 
                                    scale_biomas=config.BIOMA_ESCALA, 
                                    num_recompensas_min=5):
    """
    Gera grafo avançado com labirinto base, biomas naturais e distribuição inteligente de recompensas
    
    Args:
        tamanho_min (int): Número mínimo de nós no grafo
        largura, altura (int): Dimensões do labirinto
        seed (int): Semente para reprodução
        scale_biomas (float): Suavidade dos biomas (0.05=suave, 0.15=variado)
        num_recompensas_min (int): Número mínimo de recompensas
        
    Returns:
        Graph: Grafo completo com labirinto, biomas e recompensas
    """
    if seed is not None:
        random.seed(seed)
    
    print(f"Gerando labirinto {largura}x{altura} com biomas...")
    
    # 1. Gera labirinto base
    maze_grid, valid_positions = gerar_labirinto_conectado(largura, altura, seed)
    
    # Verifica se temos nós suficientes
    if len(valid_positions) < tamanho_min:
        print(f"Aviso: Labirinto gerado tem apenas {len(valid_positions)} nós (mínimo: {tamanho_min})")
        # Aumenta dimensões e tenta novamente
        new_width = int(largura * 1.5)
        new_height = int(altura * 1.2)
        maze_grid, valid_positions = gerar_labirinto_conectado(new_width, new_height, seed)
        largura, altura = new_width, new_height
    
    # 2. Gera biomas para toda a área
    biome_map, biome_stats = gerar_biomas_naturais(
        largura, altura, seed=seed, scale=scale_biomas, octaves=config.BIOMA_OITAVAS
    )
    
    print(f"Biomas gerados:")
    for terrain, percentage in biome_stats['percentages'].items():
        print(f"  {terrain.name}: {percentage:.1f}%")
    
    # 3. Cria grafo e adiciona apenas nós em posições válidas do labirinto
    grafo = Graph()
    grafo.maze_grid = maze_grid
    grafo.biome_map = biome_map
    
    for x, y in valid_positions:
        tipo_terreno = biome_map[y][x]
        grafo.adicionar_no(x, y, tipo_terreno)
    
    # 4. Conecta nós adjacentes (4-conectividade dentro do labirinto)
    for x, y in valid_positions:
        no_atual = grafo.obter_no(x, y)
        
        # Verifica vizinhos nas 4 direções
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            
            # Só conecta se vizinho também está no labirinto
            if (nx, ny) in valid_positions:
                vizinho = grafo.obter_no(nx, ny)
                if vizinho:
                    vizinhos_existentes = {n for n, _ in grafo.obter_vizinhos(no_atual)}
                    if vizinho not in vizinhos_existentes:
                        grafo.conectar_nos(no_atual, vizinho)
    
    # 5. Escolhe pontos inicial e final aleatórios
    inicio_pos = random.choice(valid_positions)
    no_inicial = grafo.obter_no(inicio_pos[0], inicio_pos[1])
    
    # Escolhe objetivo longe do início
    objetivo_pos = max(valid_positions, 
                      key=lambda pos: abs(pos[0] - inicio_pos[0]) + abs(pos[1] - inicio_pos[1]))
    no_objetivo = grafo.obter_no(objetivo_pos[0], objetivo_pos[1])
    
    # 6. Calcula caminho garantido entre início e objetivo
    caminho_garantido = grafo.calcular_caminho_garantido(no_inicial, no_objetivo)
    
    if not caminho_garantido:
        print("Erro: Não foi possível encontrar caminho entre início e objetivo!")
        return None
    
    print(f"Caminho garantido: {len(caminho_garantido)} passos")
    
    # 7. Distribui recompensas de forma inteligente
    num_recompensas = max(num_recompensas_min, len(valid_positions) // 8)
    distribuir_recompensas_inteligentes(grafo, caminho_garantido, num_recompensas)
    
    # Validação final
    if not grafo.validar_conectividade():
        print("Aviso: Grafo gerado não é completamente conectado!")
    
    print(f"Grafo labirinto gerado: {len(grafo.nos)} nós, {num_recompensas} recompensas")
    
    return grafo, no_inicial, no_objetivo


def distribuir_recompensas_inteligentes(grafo, caminho_garantido, num_total):
    """
    Distribui recompensas de forma inteligente no grafo
    
    Args:
        grafo (Graph): Grafo onde distribuir recompensas
        caminho_garantido (list[No]): Caminho principal entre início e objetivo
        num_total (int): Número total de recompensas a distribuir
    """
    nos_disponiveis = list(grafo.nos.values())
    nos_caminho = set(caminho_garantido)
    nos_fora_caminho = [no for no in nos_disponiveis if no not in nos_caminho]
    
    # 50% no caminho principal (excluindo início e fim)
    num_caminho = max(1, num_total // 2)
    candidatos_caminho = caminho_garantido[1:-1]  # Exclui início e fim
    
    if len(candidatos_caminho) >= num_caminho:
        # Distribui uniformemente ao longo do caminho
        step = len(candidatos_caminho) // num_caminho
        recompensas_caminho = [candidatos_caminho[i * step] for i in range(num_caminho)]
    else:
        # Se caminho é muito curto, usa todos os candidatos
        recompensas_caminho = candidatos_caminho
    
    for no in recompensas_caminho:
        no.tem_recompensa = True
    
    grafo.recompensas_caminho_principal = recompensas_caminho
    
    # 50% em áreas fora do caminho principal
    num_extras = num_total - len(recompensas_caminho)
    
    if num_extras > 0 and nos_fora_caminho:
        # Prioriza nós que estão a uma distância razoável do caminho (não muito longe)
        candidatos_extras = []
        for no in nos_fora_caminho:
            dist_min = min(grafo.distancia_manhattan(no, no_caminho) for no_caminho in nos_caminho)
            if dist_min <= 5:  # Não muito longe do caminho principal
                candidatos_extras.append((no, dist_min))
        
        # Ordena por distância e pega os melhores
        candidatos_extras.sort(key=lambda x: x[1])
        num_candidatos = min(num_extras, len(candidatos_extras))
        
        recompensas_extras = [candidatos_extras[i][0] for i in range(num_candidatos)]
        
        # Se ainda faltam recompensas, pega aleatoriamente dos restantes
        if num_candidatos < num_extras:
            restantes = [no for no in nos_fora_caminho 
                        if no not in [c[0] for c in candidatos_extras[:num_candidatos]]]
            extras_aleatorias = random.sample(restantes, 
                                           min(num_extras - num_candidatos, len(restantes)))
            recompensas_extras.extend(extras_aleatorias)
        
        for no in recompensas_extras:
            no.tem_recompensa = True
            
        grafo.recompensas_areas_extras = recompensas_extras
    
    total_recompensas = len(grafo.obter_nos_com_recompensa())
    print(f"Recompensas distribuídas: {len(recompensas_caminho)} no caminho, "
          f"{total_recompensas - len(recompensas_caminho)} em áreas extras")


# Função de compatibilidade com código antigo
def gerar_grafo_teste(tamanho_min=30, largura=20, altura=15, seed=None):
    """Gera um grafo conectado para cenários de teste."""
    resultado = gerar_grafo_labirinto_com_biomas(
        tamanho_min=tamanho_min, largura=largura, altura=altura, seed=seed
    )

    if resultado:
        grafo, _, _ = resultado
        if len(grafo.nos) >= tamanho_min and grafo.validar_conectividade():
            return grafo

    print("Aviso: usando gerador básico para garantir conectividade nos testes.")
    return _gerar_grafo_basico_conectado(largura, altura, seed)

def gerar_grafo_teste(tamanho_min=30, largura=20, altura=15, seed=None):
    """Gera um grafo conectado para cenários de teste."""
    resultado = gerar_grafo_labirinto_com_biomas(
        tamanho_min=tamanho_min, largura=largura, altura=altura, seed=seed
    )

    if resultado:
        grafo, _, _ = resultado
        if len(grafo.nos) >= tamanho_min and grafo.validar_conectividade():
            return grafo

    print("Aviso: usando gerador básico para garantir conectividade nos testes.")
    return _gerar_grafo_basico_conectado(largura, altura, seed)

def _gerar_grafo_basico_conectado(largura, altura, seed=None):
    """Gera uma grade totalmente conectada usando o modelo de grafo atual."""
    rng = random.Random(seed)
    grafo = Graph()

    for y in range(altura):
        for x in range(largura):
            rand = rng.random()
            if rand < 0.4:
                tipo = TipoTerreno.SOLIDO
            elif rand < 0.6:
                tipo = TipoTerreno.ARENOSO
            elif rand < 0.8:
                tipo = TipoTerreno.ROCHOSO
            else:
                tipo = TipoTerreno.PANTANO

            grafo.adicionar_no(x, y, tipo)

    for y in range(altura):
        for x in range(largura):
            no_atual = grafo.obter_no(x, y)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < largura and 0 <= ny < altura:
                    vizinho = grafo.obter_no(nx, ny)
                    if vizinho:
                        grafo.conectar_nos(no_atual, vizinho)

    nos_disponiveis = grafo.obter_todos_nos()
    num_recompensas = max(5, len(nos_disponiveis) // 6)
    for no in rng.sample(nos_disponiveis, num_recompensas):
        no.tem_recompensa = True

    return grafo

# Teste básico do módulo
if __name__ == "__main__":
    print("Testando geração avançada de grafos...")
    
    # Gera grafo com labirinto e biomas
    resultado = gerar_grafo_labirinto_com_biomas(
        tamanho_min=50, largura=25, altura=15, seed=42
    )
    
    if resultado:
        grafo, inicio, objetivo = resultado
        
        print(f"\nGrafo criado: {grafo}")
        print(f"Início: {inicio}")
        print(f"Objetivo: {objetivo}")
        print(f"Conectividade: {'OK' if grafo.validar_conectividade() else 'FALHA'}")
        print(f"Recompensas: {len(grafo.obter_nos_com_recompensa())}")
        
        # Mostra amostra do labirinto
        print(f"\nAmostra do labirinto (10x8):")
        for y in range(min(8, grafo.altura)):
            linha = ""
            for x in range(min(10, grafo.largura)):
                no = grafo.obter_no(x, y)
                if no:
                    linha += no.obter_simbolo()
                else:
                    linha += '#'
            print(linha)
