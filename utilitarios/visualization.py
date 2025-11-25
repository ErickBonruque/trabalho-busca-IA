"""
Módulo responsável pelas utilidades, visualização e funções auxiliares.
Renderização do ambiente, simulação de movimento e geração de ambientes.
"""

import time
import os
import random
from nucleo.graph import Graph, TipoTerreno, gerar_grafo_labirinto_com_biomas


def limpar_console():
    """Limpa o console de forma compatível com Windows e Linux"""
    os.system('cls' if os.name == 'nt' else 'clear')


def renderizar_mapa(grafo, agente=None, caminho=None, destacar_nos=None):
    """
    Renderiza o mapa do grafo em ASCII
    
    Args:
        grafo (Graph): Grafo do ambiente
        agente (Agent): Agente para mostrar posição atual (opcional)
        caminho (list): Caminho para destacar (opcional)
        destacar_nos (list): Nós específicos para destacar (opcional)
        
    Returns:
        str: Representação ASCII do mapa
    """
    if not grafo.nos:
        return "Grafo vazio"
    
    # Cria matriz para renderização
    matriz = []
    for y in range(grafo.altura):
        linha = []
        for x in range(grafo.largura):
            no = grafo.obter_no(x, y)
            if no:
                linha.append(no.obter_simbolo())
            else:
                linha.append('#')  # Parede (nó inexistente)
        matriz.append(linha)
    
    # Marca caminho se fornecido
    if caminho:
        for no in caminho:
            # Só marca como caminho se não for recompensa
            if not no.tem_recompensa:
                matriz[no.y][no.x] = '.'  # Caminho

    # Determina e marca Início e Fim
    no_inicio = None
    no_fim = None

    if caminho and len(caminho) > 0:
        no_inicio = caminho[0]
        no_fim = caminho[-1]
    elif agente:
        no_inicio = agente.posicao_inicial
        no_fim = agente.objetivo

    if no_inicio:
        matriz[no_inicio.y][no_inicio.x] = 'S'
    
    if no_fim:
        matriz[no_fim.y][no_fim.x] = 'G'
    
    # Marca posição do agente
    if agente:
        matriz[agente.posicao_atual.y][agente.posicao_atual.x] = 'A'
    
    # Destaca nós específicos
    if destacar_nos:
        for no in destacar_nos:
            matriz[no.y][no.x] = '+'  # Destaque especial
    
    # Constrói string de saída
    resultado = []
    resultado.append("   " + "".join(f"{i:2}" for i in range(grafo.largura)))
    resultado.append("   " + "--" * grafo.largura)
    
    for y, linha in enumerate(matriz):
        linha_str = f"{y:2}|" + " ".join(f"{celula}" for celula in linha)
        resultado.append(linha_str)
    
    return "\n".join(resultado)


def renderizar_mapa_com_legenda(grafo, agente=None, caminho=None):
    """
    Renderiza mapa com legenda explicativa
    
    Args:
        grafo (Graph): Grafo do ambiente
        agente (Agent): Agente (opcional)
        caminho (list): Caminho (opcional)
        
    Returns:
        str: Mapa com legenda
    """
    mapa = renderizar_mapa(grafo, agente, caminho)
    
    legenda = [
        "\n=== LEGENDA ===",
        "S = Inicio        G = Objetivo",
        "A = Agente        . = Caminho",
        "$ = Recompensa    * = Coletada", 
        "# = Parede        + = Destaque",
        "",
        "TERRENOS:",
        ". = Solido (1)    ~ = Arenoso (4)",
        "^ = Rochoso (10)  & = Pantano (20)",
        "================="
    ]
    
    return mapa + "\n" + "\n".join(legenda)


def simular_movimento(grafo, agente, caminho, velocidade=1.0, mostrar_stats=True):
    """
    Simula o movimento do agente pelo caminho com animação
    
    Args:
        grafo (Graph): Grafo do ambiente
        agente (Agent): Agente a simular
        caminho (list): Lista de nós do caminho
        velocidade (float): Velocidade da animação (segundos por passo)
        mostrar_stats (bool): Se deve mostrar estatísticas
    """
    if not caminho:
        print("Nenhum caminho para simular!")
        return
    
    print(f"\n=== SIMULANDO MOVIMENTO - {len(caminho)} PASSOS ===")
    
    # Reseta agente para posição inicial
    agente.resetar_estado()
    
    for i, no in enumerate(caminho):
        limpar_console()
        
        # Atualiza posição do agente
        if i > 0:
            no_anterior = caminho[i-1]
            # Encontra custo do movimento
            custo_movimento = 0
            for vizinho, custo in grafo.obter_vizinhos(no_anterior):
                if vizinho == no:
                    custo_movimento = custo
                    break
            agente.mover_para(no, custo_movimento)
        
        # Renderiza estado atual
        print(f"PASSO {i+1}/{len(caminho)}")
        print(renderizar_mapa(grafo, agente, caminho))
        
        if mostrar_stats:
            print(f"\nPosição: ({no.x}, {no.y}) - Terreno: {no.tipo_terreno.name}")
            print(f"Custo Acumulado: {agente.custo_acumulado}")
            print(f"Recompensas Coletadas: {len(agente.recompensas_coletadas)}")
            
            if agente.recompensas_coletadas:
                recompensas_pos = [(r.x, r.y) for r in agente.recompensas_coletadas]
                print(f"Posições das Recompensas: {recompensas_pos}")
        
        # Pausa para animação
        if i < len(caminho) - 1:  # Não pausa no último passo
            time.sleep(velocidade)
    
    print(f"\n OBJETIVO ALCANÇADO!")
    print(f"Custo Final: {agente.custo_acumulado}")
    print(f"Recompensas: {len(agente.recompensas_coletadas)}")


def gerar_ambiente_personalizado(largura=8, altura=6, densidade_terreno=None):
    """
    Gera um ambiente personalizado com parâmetros específicos
    
    Args:
        largura (int): Largura do grafo
        altura (int): Altura do grafo
        densidade_terreno (dict): Probabilidades dos terrenos
        
    Returns:
        Graph: Grafo gerado
    """
    if densidade_terreno is None:
        densidade_terreno = {
            TipoTerreno.SOLIDO: 0.4,
            TipoTerreno.ARENOSO: 0.3,
            TipoTerreno.ROCHOSO: 0.2,
            TipoTerreno.PANTANO: 0.1
        }
    
    grafo = Graph()
    
    # Gera nós com distribuição personalizada
    for y in range(altura):
        for x in range(largura):
            # Escolhe terreno baseado nas probabilidades
            rand = random.random()
            soma_prob = 0
            tipo_escolhido = TipoTerreno.SOLIDO
            
            for tipo, prob in densidade_terreno.items():
                soma_prob += prob
                if rand <= soma_prob:
                    tipo_escolhido = tipo
                    break
            
            grafo.adicionar_no(x, y, tipo_escolhido)
    
    # Conecta nós (4-conectividade)
    for y in range(altura):
        for x in range(largura):
            no_atual = grafo.obter_no(x, y)
            if not no_atual:
                continue
                
            # Conecta com vizinhos adjacentes
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                novo_x, novo_y = x + dx, y + dy
                if 0 <= novo_x < largura and 0 <= novo_y < altura:
                    vizinho = grafo.obter_no(novo_x, novo_y)
                    if vizinho:
                        grafo.conectar_nos(no_atual, vizinho)
    
    return grafo


def distribuir_recompensas_estrategicas(grafo, num_recompensas=5):
    """
    Distribui recompensas de forma estratégica pelo grafo
    
    Args:
        grafo (Graph): Grafo do ambiente
        num_recompensas (int): Número de recompensas a distribuir
        
    Returns:
        list: Lista de nós que receberam recompensas
    """
    todos_nos = grafo.obter_todos_nos()
    
    if len(todos_nos) < num_recompensas:
        num_recompensas = len(todos_nos)
    
    # Evita colocar recompensas em terrenos muito caros
    nos_validos = [no for no in todos_nos 
                   if no.tipo_terreno.custo <= TipoTerreno.ROCHOSO.custo]
    
    if len(nos_validos) < num_recompensas:
        nos_validos = todos_nos
    
    # Seleciona nós aleatórios
    nos_recompensa = random.sample(nos_validos, num_recompensas)
    
    for no in nos_recompensa:
        no.tem_recompensa = True
    
    return nos_recompensa


def validar_ambiente(grafo, no_inicial=None, no_objetivo=None):
    """
    Valida se o ambiente está bem formado para busca
    
    Args:
        grafo (Graph): Grafo do ambiente
        no_inicial (No): Nó inicial (opcional)
        no_objetivo (No): Nó objetivo (opcional)
        
    Returns:
        tuple: (is_valid, error_messages)
    """
    erros = []
    
    # Verifica se há nós
    if not grafo.nos:
        erros.append("Grafo não possui nós")
    
    # Verifica conectividade
    if not grafo.validar_conectividade():
        erros.append("Grafo não é totalmente conectado")
    
    # Verifica tamanho mínimo
    if len(grafo.nos) < 30:
        erros.append(f"Grafo muito pequeno: {len(grafo.nos)} nós (mín. 30)")
    
    # Verifica nós inicial e objetivo
    if no_inicial and no_inicial not in grafo.nos.values():
        erros.append("Nó inicial não existe no grafo")
    
    if no_objetivo and no_objetivo not in grafo.nos.values():
        erros.append("Nó objetivo não existe no grafo")
    
    if no_inicial and no_objetivo and no_inicial == no_objetivo:
        erros.append("Nó inicial e objetivo são o mesmo")
    
    # Verifica recompensas
    recompensas = grafo.obter_nos_com_recompensa()
    if len(recompensas) < 5:
        erros.append(f"Poucas recompensas: {len(recompensas)} (mín. 5)")
    
    return len(erros) == 0, erros


def obter_estatisticas_grafo(grafo):
    """
    Calcula estatísticas do grafo
    
    Args:
        grafo (Graph): Grafo do ambiente
        
    Returns:
        dict: Estatísticas do grafo
    """
    if not grafo.nos:
        return {"erro": "Grafo vazio"}
    
    # Conta tipos de terreno
    contagem_terrenos = {}
    for terreno in TipoTerreno:
        contagem_terrenos[terreno.name] = 0
    
    for no in grafo.nos.values():
        contagem_terrenos[no.tipo_terreno.name] += 1
    
    # Calcula outras métricas
    total_nos = len(grafo.nos)
    recompensas = len(grafo.obter_nos_com_recompensa())
    
    # Calcula custo médio
    custo_total = sum(no.tipo_terreno.custo for no in grafo.nos.values())
    custo_medio = custo_total / total_nos if total_nos > 0 else 0
    
    return {
        "total_nos": total_nos,
        "dimensoes": f"{grafo.largura}x{grafo.altura}",
        "recompensas": recompensas,
        "custo_medio_terreno": custo_medio,
        "distribuicao_terrenos": contagem_terrenos,
        "conectividade": "OK" if grafo.validar_conectividade() else "FALHA"
    }


def escolher_nos_aleatorios(grafo, evitar_recompensas=True):
    """
    Escolhe nós inicial e objetivo aleatórios no grafo
    
    Args:
        grafo (Graph): Grafo do ambiente
        evitar_recompensas (bool): Se deve evitar nós com recompensas
        
    Returns:
        tuple: (no_inicial, no_objetivo)
    """
    todos_nos = grafo.obter_todos_nos()
    
    if evitar_recompensas:
        nos_sem_recompensa = [no for no in todos_nos if not no.tem_recompensa]
        if len(nos_sem_recompensa) >= 2:
            todos_nos = nos_sem_recompensa
    
    if len(todos_nos) < 2:
        return None, None
    
    # Escolhe dois nós diferentes
    no_inicial = random.choice(todos_nos)
    nos_restantes = [no for no in todos_nos if no != no_inicial]
    no_objetivo = random.choice(nos_restantes)
    
    return no_inicial, no_objetivo


# Teste básico do módulo
if __name__ == "__main__":
    print("Testando módulo utils.py...")
    
    # Gera ambiente de teste
    resultado = gerar_grafo_labirinto_com_biomas()
    if resultado:
        grafo = resultado[0]
    else:
        print("Erro na geração do grafo")
        exit(1)
    
    print("=== ESTATÍSTICAS DO GRAFO ===")
    stats = obter_estatisticas_grafo(grafo)
    for chave, valor in stats.items():
        print(f"{chave}: {valor}")
    
    print("\n=== MAPA GERADO ===")
    print(renderizar_mapa_com_legenda(grafo))
    
    # Testa validação
    no_inicial, no_objetivo = escolher_nos_aleatorios(grafo)
    valido, erros = validar_ambiente(grafo, no_inicial, no_objetivo)
    
    print(f"\n=== VALIDAÇÃO ===")
    print(f"Ambiente válido: {valido}")
    if erros:
        for erro in erros:
            print(f"  - {erro}")
    
    print("\nTeste concluído!")
