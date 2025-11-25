"""
Módulo responsável pelas funções heurísticas para os algoritmos de busca.
Implementa diferentes estratégias de estimativa de custo e avaliação.
"""

import math
from nucleo.graph import TipoTerreno


def _custo_minimo_terreno(grafo=None):
    """Retorna o menor custo de terreno conhecido."""
    # OTIMIZAÇÃO: Retorna o custo mínimo global dos tipos de terreno
    # Isso evita percorrer todos os nós do grafo (lento) e mantém a heurística admissível
    return min(tipo.custo for tipo in TipoTerreno)

def distancia_manhattan(no_atual, objetivo):
    """
    Calcula a distância Manhattan entre dois nós
    
    Args:
        no_atual (No): Nó atual
        objetivo (No): Nó objetivo
        
    Returns:
        int: Distância Manhattan
    """
    return abs(no_atual.x - objetivo.x) + abs(no_atual.y - objetivo.y)


def distancia_euclidiana(no_atual, objetivo):
    """
    Calcula a distância Euclidiana entre dois nós
    
    Args:
        no_atual (No): Nó atual
        objetivo (No): Nó objetivo
        
    Returns:
        float: Distância Euclidiana
    """
    dx = no_atual.x - objetivo.x
    dy = no_atual.y - objetivo.y
    return math.sqrt(dx * dx + dy * dy)


def heuristica_terreno(no_atual, objetivo, grafo=None):
    """
    Heurística que considera tipos de terreno no caminho
    Ajusta a distância Manhattan pelos custos esperados de terreno
    
    Args:
        no_atual (No): Nó atual
        objetivo (No): Nó objetivo
        grafo (Graph): Grafo do ambiente (opcional)
        
    Returns:
        float: Distância estimada considerando terrenos
    """
    distancia_base = distancia_manhattan(no_atual, objetivo)
    
    if distancia_base == 0:
        return 0
     
    custo_minimo = _custo_minimo_terreno(grafo)
    return distancia_base * custo_minimo


def avaliar_recompensas_proximas(no_atual, objetivo, recompensas, raio=3):
    """
    Avalia recompensas próximas e calcula bônus/penalidade
    
    Args:
        no_atual (No): Nó atual
        objetivo (No): Nó objetivo
        recompensas (list): Lista de nós com recompensas
        raio (int): Raio de busca por recompensas
        
    Returns:
        float: Bônus (negativo reduz custo) ou penalidade
    """
    if not recompensas:
        return 0
    
    bonus_total = 0
    distancia_direta = distancia_manhattan(no_atual, objetivo)
    
    for recompensa in recompensas:
        # Pula recompensas já coletadas
        if recompensa.recompensa_coletada:
            continue
            
        dist_para_recompensa = distancia_manhattan(no_atual, recompensa)
        dist_recompensa_objetivo = distancia_manhattan(recompensa, objetivo)
        
        # Se a recompensa está próxima (dentro do raio)
        if dist_para_recompensa <= raio:
            # Calcula desvio necessário
            desvio = (dist_para_recompensa + dist_recompensa_objetivo) - distancia_direta
            
            # Se o desvio é pequeno, dá bônus (reduz custo estimado)
            if desvio <= 2:
                bonus_total -= 5  # Reduz custo estimado (incentiva coleta)
            elif desvio <= 4:
                bonus_total -= 2  # Pequeno incentivo
                
    return bonus_total


def heuristica_combinada(no_atual, objetivo, grafo=None, recompensas=None):
    """
    Heurística principal que combina distância, terreno e recompensas
    
    Args:
        no_atual (No): Nó atual
        objetivo (No): Nó objetivo
        grafo (Graph): Grafo do ambiente
        recompensas (list): Lista de nós com recompensas
        
    Returns:
        float: Custo heurístico combinado
    """
    # Componente base: heurística de terreno
    h_base = heuristica_terreno(no_atual, objetivo, grafo)
    
    # Componente de recompensas
    h_recompensas = 0
    if recompensas:
        h_recompensas = avaliar_recompensas_proximas(no_atual, objetivo, recompensas)
    
    # Combina componentes
    h_total = h_base + h_recompensas
    
    # Garante que a heurística nunca seja negativa (mantém admissibilidade)
    return max(0, h_total)


def heuristica_gulosa_agressiva(no_atual, objetivo, grafo=None, recompensas=None):
    """
    Heurística mais agressiva para busca gulosa
    Prioriza fortemente recompensas próximas
    
    Args:
        no_atual (No): Nó atual
        objetivo (No): Nó objetivo
        grafo (Graph): Grafo do ambiente
        recompensas (list): Lista de nós com recompensas
        
    Returns:
        float: Custo heurístico agressivo
    """
    h_base = distancia_manhattan(no_atual, objetivo)
    
    if not recompensas:
        return h_base
    
    # Encontra a recompensa mais próxima não coletada
    recompensa_mais_proxima = None
    menor_distancia = float('inf')
    
    for recompensa in recompensas:
        if not recompensa.recompensa_coletada:
            dist = distancia_manhattan(no_atual, recompensa)
            if dist < menor_distancia:
                menor_distancia = dist
                recompensa_mais_proxima = recompensa
    
    # Se há recompensa próxima, modifica drasticamente a heurística
    if recompensa_mais_proxima and menor_distancia <= 3:
        # Prioriza ir para a recompensa em vez do objetivo
        return menor_distancia * 0.5
    
    return h_base


def calcular_fator_terreno_caminho(caminho, grafo):
    """
    Calcula o fator médio de terreno de um caminho
    
    Args:
        caminho (list): Lista de nós do caminho
        grafo (Graph): Grafo do ambiente
        
    Returns:
        float: Fator médio de custo do terreno
    """
    if not caminho:
        return 1.0
    
    soma_custos = 0
    for no in caminho:
        soma_custos += no.tipo_terreno.custo
    
    return soma_custos / len(caminho)


def estimar_custo_restante(no_atual, objetivo, grafo):
    """
    Estima o custo restante considerando terrenos do grafo
    
    Args:
        no_atual (No): Nó atual
        objetivo (No): Nó objetivo
        grafo (Graph): Grafo do ambiente
        
    Returns:
        float: Custo estimado restante
    """
    distancia = distancia_manhattan(no_atual, objetivo)
    
    if distancia == 0:
        return 0
    
    # Calcula custo médio dos terrenos no grafo
    todos_nos = grafo.obter_todos_nos()
    custo_total = sum(no.tipo_terreno.custo for no in todos_nos)
    custo_medio = custo_total / len(todos_nos)
    
    # Estima custo baseado na distância e custo médio
    return distancia * custo_medio


# Cache para otimizar cálculos repetidos
_cache_distancias = {}

def distancia_manhattan_cached(no_atual, objetivo):
    """
    Versão com cache da distância Manhattan para otimizar performance
    
    Args:
        no_atual (No): Nó atual
        objetivo (No): Nó objetivo
        
    Returns:
        int: Distância Manhattan (do cache se disponível)
    """
    chave = ((no_atual.x, no_atual.y), (objetivo.x, objetivo.y))
    
    if chave not in _cache_distancias:
        _cache_distancias[chave] = distancia_manhattan(no_atual, objetivo)
    
    return _cache_distancias[chave]


def limpar_cache_heuristicas():
    """Limpa o cache de heurísticas para economizar memória"""
    global _cache_distancias
    _cache_distancias.clear()


# Teste básico do módulo
if __name__ == "__main__":
    print("Testando módulo heuristics.py...")
    
    from graph import gerar_grafo_teste, No, TipoTerreno
    
    # Gera grafo de teste
    grafo = gerar_grafo_teste()
    
    # Cria nós de teste
    no_inicio = grafo.obter_no(0, 0)
    no_fim = grafo.obter_no(7, 5)
    
    if no_inicio and no_fim:
        print(f"Nó início: {no_inicio}")
        print(f"Nó fim: {no_fim}")
        
        # Testa heurísticas
        dist_manhattan = distancia_manhattan(no_inicio, no_fim)
        h_terreno = heuristica_terreno(no_inicio, no_fim, grafo)
        h_combinada = heuristica_combinada(no_inicio, no_fim, grafo, 
                                         grafo.obter_nos_com_recompensa())
        
        print(f"Distância Manhattan: {dist_manhattan}")
        print(f"Heurística terreno: {h_terreno:.2f}")
        print(f"Heurística combinada: {h_combinada:.2f}")
        
    print("Teste concluído!")
