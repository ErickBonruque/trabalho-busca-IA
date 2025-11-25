"""
Módulo responsável pela implementação dos algoritmos de busca.
Implementa BFS, DFS, Busca Gulosa e A* com suas estratégias específicas.
"""

import time
from collections import deque
import heapq
from nucleo.graph import Graph, No, TipoTerreno
from nucleo.agent import AgentEstado
from .heuristics import (distancia_manhattan, heuristica_combinada,
                        heuristica_gulosa_agressiva, heuristica_terreno,
                        limpar_cache_heuristicas)
from algoritmos.search_algorithms import *

class ResultadoBusca:
    """Armazena o resultado de uma execução de algoritmo de busca"""
    
    def __init__(self, nome_algoritmo):
        self.nome_algoritmo = nome_algoritmo
        self.caminho_encontrado = []
        self.custo_total = 0
        self.nos_expandidos = 0
        self.tempo_execucao = 0.0
        self.sucesso = False
        self.recompensas_no_caminho = []
        
    def definir_resultado(self, caminho, custo, nos_expandidos, tempo, sucesso=True):
        """Define os resultados da busca"""
        self.caminho_encontrado = caminho
        self.custo_total = custo
        self.nos_expandidos = nos_expandidos
        self.tempo_execucao = tempo
        self.sucesso = sucesso
        
    def adicionar_recompensa(self, recompensa):
        """Adiciona uma recompensa encontrada no caminho"""
        self.recompensas_no_caminho.append(recompensa)


def busca_bfs(grafo, no_inicial, no_objetivo, limite_nos=10000):
    """
    Busca em Largura (Breadth-First Search)
    Explora nível por nível, garante caminho mais curto em número de passos
    
    Args:
        grafo (Graph): Grafo do ambiente
        no_inicial (No): Nó inicial
        no_objetivo (No): Nó objetivo
        limite_nos (int): Limite de nós para evitar loops infinitos
        
    Returns:
        ResultadoBusca: Resultado da busca
    """
    resultado = ResultadoBusca("BFS")
    inicio_tempo = time.time()
    
    if no_inicial == no_objetivo:
        resultado.definir_resultado([no_inicial], 0, 0, 0.0)
        return resultado
    
    # Fila FIFO para BFS
    fila = deque([AgentEstado(no_inicial, 0, 0, None)])
    visitados = {no_inicial}
    nos_expandidos = 0
    
    while fila and nos_expandidos < limite_nos:
        estado_atual = fila.popleft()
        nos_expandidos += 1
        
        # Verifica se chegou ao objetivo
        if estado_atual.no == no_objetivo:
            caminho = estado_atual.reconstruir_caminho()
            custo_total = calcular_custo_caminho(caminho, grafo)
            tempo_total = time.time() - inicio_tempo
            
            resultado.definir_resultado(caminho, custo_total, nos_expandidos, tempo_total)
            return resultado
        
        # Expande vizinhos
        for vizinho, custo_aresta in grafo.adjacencias[estado_atual.no]:
            if vizinho not in visitados:
                visitados.add(vizinho)
                novo_custo = estado_atual.custo_g + custo_aresta
                novo_estado = AgentEstado(vizinho, novo_custo, 0, estado_atual)
                fila.append(novo_estado)
    
    # Não encontrou caminho
    tempo_total = time.time() - inicio_tempo
    resultado.definir_resultado([], 0, nos_expandidos, tempo_total, False)
    return resultado


def busca_dfs(grafo, no_inicial, no_objetivo, limite_nos=10000):
    """
    Busca em Profundidade (Depth-First Search)
    Explora o mais profundo possível antes de voltar
    
    Args:
        grafo (Graph): Grafo do ambiente
        no_inicial (No): Nó inicial
        no_objetivo (No): Nó objetivo
        limite_nos (int): Limite de nós para evitar loops infinitos
        
    Returns:
        ResultadoBusca: Resultado da busca
    """
    resultado = ResultadoBusca("DFS")
    inicio_tempo = time.time()
    
    if no_inicial == no_objetivo:
        resultado.definir_resultado([no_inicial], 0, 0, 0.0)
        return resultado
    
    # Pilha LIFO para DFS
    pilha = [AgentEstado(no_inicial, 0, 0, None)]
    visitados = {no_inicial}
    nos_expandidos = 0
    
    while pilha and nos_expandidos < limite_nos:
        estado_atual = pilha.pop()
        nos_expandidos += 1
        
        # Verifica se chegou ao objetivo
        if estado_atual.no == no_objetivo:
            caminho = estado_atual.reconstruir_caminho()
            custo_total = calcular_custo_caminho(caminho, grafo)
            tempo_total = time.time() - inicio_tempo
            
            resultado.definir_resultado(caminho, custo_total, nos_expandidos, tempo_total)
            return resultado
        
        # Expande vizinhos (em ordem reversa para manter comportamento consistente)
        vizinhos = list(grafo.adjacencias[estado_atual.no])
        for vizinho, custo_aresta in reversed(vizinhos):
            if vizinho not in visitados:
                visitados.add(vizinho)
                novo_custo = estado_atual.custo_g + custo_aresta
                novo_estado = AgentEstado(vizinho, novo_custo, 0, estado_atual)
                pilha.append(novo_estado)
    
    # Não encontrou caminho
    tempo_total = time.time() - inicio_tempo
    resultado.definir_resultado([], 0, nos_expandidos, tempo_total, False)
    return resultado


def busca_gulosa(grafo, no_inicial, no_objetivo, limite_nos=10000):
    """
    Busca Gulosa (Greedy Best-First Search)
    Sempre escolhe o nó que pareça mais promissor (menor heurística)
    
    Args:
        grafo (Graph): Grafo do ambiente
        no_inicial (No): Nó inicial
        no_objetivo (No): Nó objetivo
        limite_nos (int): Limite de nós para evitar loops infinitos
        
    Returns:
        ResultadoBusca: Resultado da busca
    """
    resultado = ResultadoBusca("Gulosa")
    inicio_tempo = time.time()
    
    if no_inicial == no_objetivo:
        resultado.definir_resultado([no_inicial], 0, 0, 0.0)
        return resultado
    
    # Fila de prioridade ordenada por heurística h(n)
    recompensas = grafo.obter_nos_com_recompensa()
    h_inicial = heuristica_gulosa_agressiva(no_inicial, no_objetivo, grafo, recompensas)
    
    fila_prioridade = [AgentEstado(no_inicial, 0, h_inicial, None)]
    visitados = {no_inicial}
    nos_expandidos = 0
    
    while fila_prioridade and nos_expandidos < limite_nos:
        estado_atual = heapq.heappop(fila_prioridade)
        nos_expandidos += 1
        
        # Verifica se chegou ao objetivo
        if estado_atual.no == no_objetivo:
            caminho = estado_atual.reconstruir_caminho()
            custo_total = calcular_custo_caminho(caminho, grafo)
            tempo_total = time.time() - inicio_tempo
            
            resultado.definir_resultado(caminho, custo_total, nos_expandidos, tempo_total)
            return resultado
        
        # Expande vizinhos
        for vizinho, custo_aresta in grafo.adjacencias[estado_atual.no]:
            if vizinho not in visitados:
                visitados.add(vizinho)
                h_vizinho = heuristica_gulosa_agressiva(vizinho, no_objetivo, grafo, recompensas)
                novo_custo = estado_atual.custo_g + custo_aresta
                novo_estado = AgentEstado(vizinho, novo_custo, h_vizinho, estado_atual)
                heapq.heappush(fila_prioridade, novo_estado)
    
    # Não encontrou caminho
    tempo_total = time.time() - inicio_tempo
    resultado.definir_resultado([], 0, nos_expandidos, tempo_total, False)
    return resultado


def busca_a_estrela(grafo, no_inicial, no_objetivo, limite_nos=10000):
    """
    Busca A* (A-Star)
    Usa função f(n) = g(n) + h(n) para encontrar caminho ótimo
    
    Args:
        grafo (Graph): Grafo do ambiente
        no_inicial (No): Nó inicial
        no_objetivo (No): Nó objetivo
        limite_nos (int): Limite de nós para evitar loops infinitos
        
    Returns:
        ResultadoBusca: Resultado da busca
    """
    resultado = ResultadoBusca("A*")
    inicio_tempo = time.time()
    
    if no_inicial == no_objetivo:
        resultado.definir_resultado([no_inicial], 0, 0, 0.0)
        return resultado
    
    # Fila de prioridade ordenada por f(n) = g(n) + h(n)
    # A* usa heurística de terreno (admissível) sem considerar recompensas
    h_inicial = heuristica_terreno(no_inicial, no_objetivo, grafo)
    f_inicial = 0 + h_inicial
    
    fila_prioridade = [AgentEstado(no_inicial, 0, f_inicial, None)]
    visitados = {}  # Dicionário para armazenar melhor custo g conhecido
    visitados[no_inicial] = 0
    nos_expandidos = 0
    
    while fila_prioridade and nos_expandidos < limite_nos:
        estado_atual = heapq.heappop(fila_prioridade)
        
        # Se encontramos um caminho pior para este nó, ignora sem contar a expansão
        if estado_atual.custo_g > visitados.get(estado_atual.no, float('inf')):
            continue
        
        nos_expandidos += 1
        
        # Verifica se chegou ao objetivo
        if estado_atual.no == no_objetivo:
            caminho = estado_atual.reconstruir_caminho()
            custo_total = estado_atual.custo_g
            tempo_total = time.time() - inicio_tempo
            
            resultado.definir_resultado(caminho, custo_total, nos_expandidos, tempo_total)
            return resultado
        
        # Expande vizinhos
        for vizinho, custo_aresta in grafo.adjacencias[estado_atual.no]:
            novo_custo_g = estado_atual.custo_g + custo_aresta
            
            # Se encontramos um caminho melhor para o vizinho
            if novo_custo_g < visitados.get(vizinho, float('inf')):
                visitados[vizinho] = novo_custo_g
                h_vizinho = heuristica_terreno(vizinho, no_objetivo, grafo)
                f_vizinho = novo_custo_g + h_vizinho
                novo_estado = AgentEstado(vizinho, novo_custo_g, f_vizinho, estado_atual)
                heapq.heappush(fila_prioridade, novo_estado)
    
    # Não encontrou caminho
    tempo_total = time.time() - inicio_tempo
    resultado.definir_resultado([], 0, nos_expandidos, tempo_total, False)
    return resultado


def calcular_custo_caminho(caminho, grafo):
    """
    Calcula o custo total de um caminho
    
    Args:
        caminho (list): Lista de nós do caminho
        grafo (Graph): Grafo do ambiente
        
    Returns:
        float: Custo total do caminho
    """
    if len(caminho) <= 1:
        return 0
    
    custo_total = 0
    for i in range(len(caminho) - 1):
        no_atual = caminho[i]
        no_proximo = caminho[i + 1]
        
        # Encontra o custo da aresta
        custo_total += grafo.obter_custo_aresta(no_atual, no_proximo)
                
    return custo_total


def identificar_recompensas_no_caminho(caminho, grafo):
    """
    Identifica quais recompensas seriam coletadas em um caminho
    
    Args:
        caminho (list): Lista de nós do caminho
        grafo (Graph): Grafo do ambiente
        
    Returns:
        list: Lista de nós com recompensas no caminho
    """
    recompensas_coletadas = []
    for no in caminho:
        if no.tem_recompensa:
            recompensas_coletadas.append(no)
    return recompensas_coletadas


def executar_todos_algoritmos(grafo, no_inicial, no_objetivo):
    """
    Executa todos os algoritmos de busca no mesmo ambiente
    
    Args:
        grafo (Graph): Grafo do ambiente
        no_inicial (No): Nó inicial
        no_objetivo (No): Nó objetivo
        
    Returns:
        dict: Dicionário com resultados de todos os algoritmos
    """
    print("Executando algoritmos de busca...")
    
    # Limpa cache de heurísticas para medição precisa
    limpar_cache_heuristicas()
    
    resultados = {}
    
    # Lista de algoritmos para executar
    algoritmos = [
        ("BFS", busca_bfs),
        ("DFS", busca_dfs),
        ("Gulosa", busca_gulosa),
        ("A*", busca_a_estrela)
    ]
    
    for nome, funcao_busca in algoritmos:
        print(f"  Executando {nome}...")
        
        # Reseta estado das recompensas para cada algoritmo
        grafo.resetar_recompensas()
        
        # Executa o algoritmo
        resultado = funcao_busca(grafo, no_inicial, no_objetivo)
        
        # Identifica recompensas no caminho
        if resultado.sucesso:
            recompensas_caminho = identificar_recompensas_no_caminho(
                resultado.caminho_encontrado, grafo)
            for recompensa in recompensas_caminho:
                resultado.adicionar_recompensa(recompensa)
        
        resultados[nome] = resultado
        
        # Feedback do progresso
        if resultado.sucesso:
            print(f"    [OK] Caminho encontrado (custo: {resultado.custo_total:.1f}, "
                  f"nos: {resultado.nos_expandidos})")
        else:
            print(f"    [X] Falha na busca ({resultado.nos_expandidos} nos expandidos)")
    
    print("Algoritmos executados com sucesso!")
    return resultados


# Teste básico do módulo
if __name__ == "__main__":
    print("Testando módulo search_algorithms.py...")
    
    from graph import gerar_grafo_teste
    
    # Gera grafo de teste
    grafo = gerar_grafo_teste()
    
    # Define nós inicial e objetivo
    no_inicial = grafo.obter_no(0, 0)
    no_objetivo = grafo.obter_no(7, 5)
    
    if no_inicial and no_objetivo:
        print(f"Testando busca de {no_inicial} para {no_objetivo}")
        
        # Testa BFS
        resultado_bfs = busca_bfs(grafo, no_inicial, no_objetivo)
        print(f"BFS: {'Sucesso' if resultado_bfs.sucesso else 'Falha'} - "
              f"Custo: {resultado_bfs.custo_total:.1f}")
        
        # Testa A*
        resultado_astar = busca_a_estrela(grafo, no_inicial, no_objetivo)
        print(f"A*: {'Sucesso' if resultado_astar.sucesso else 'Falha'} - "
              f"Custo: {resultado_astar.custo_total:.1f}")
    else:
        print("Erro: Não foi possível obter nós inicial/objetivo")
        
    print("Teste concluído!")
