"""
Arquivo de teste completo para validar o sistema de algoritmos de busca.
Executa testes automatizados de todos os componentes.
"""

import sys
import os
import traceback

# Adiciona o diretório pai ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nucleo.graph import gerar_grafo_teste, TipoTerreno
from nucleo.agent import Agent, AgentEstado  
from algoritmos.search_algorithms import (busca_bfs, busca_dfs, busca_gulosa, 
                              busca_a_estrela, executar_todos_algoritmos)
from algoritmos.heuristics import (distancia_manhattan, heuristica_combinada, 
                       limpar_cache_heuristicas)
from utilitarios.visualization import (renderizar_mapa, validar_ambiente, obter_estatisticas_grafo,
                  escolher_nos_aleatorios, distribuir_recompensas_estrategicas)
from utilitarios.results import ResultadoComparativo


class TestRunner:
    """Classe para executar testes do sistema"""
    
    def __init__(self):
        self.testes_passaram = 0
        self.testes_falharam = 0
        self.erros = []
        
    def executar_teste(self, nome_teste, func_teste):
        """Executa um teste individual"""
        try:
            print(f"[TESTE] Executando: {nome_teste}...")
            func_teste()
            print(f"   [OK] {nome_teste} - PASSOU")
            self.testes_passaram += 1
        except Exception as e:
            print(f"   [FALHA] {nome_teste} - ERRO: {e}")
            self.testes_falharam += 1
            self.erros.append(f"{nome_teste}: {e}")
            
    def relatorio_final(self):
        """Exibe relatório final dos testes"""
        total = self.testes_passaram + self.testes_falharam
        print(f"\n{'='*50}")
        print("\n[RESULTADO] DOS TESTES:")
        print("="*40)
        print(f"[SUCESSO] Testes Passaram: {self.testes_passaram}")
        print(f"[FALHA] Testes Falharam: {self.testes_falharam}")
        print(f"[TOTAL] de Testes: {total}")
        
        if self.erros:
            print("\n[AVISO] ERROS ENCONTRADOS:")
            for erro in self.erros:
                print(f"  - {erro}")
            print("\n[RESULTADO] TESTES FALHARAM!")
            return False
        else:
            print("\n[SUCESSO] TODOS OS TESTES PASSARAM!")
            return True
def testar_grafo():
    """Testa funcionalidades do módulo graph.py"""
    # Gera grafo
    grafo = gerar_grafo_teste(30, 8, 6)
    assert len(grafo.nos) >= 30, "Grafo deve ter pelo menos 30 nós"
    
    # Testa conectividade
    assert grafo.validar_conectividade(), "Grafo deve ser conectado"
    
    # Testa recompensas
    recompensas = grafo.obter_nos_com_recompensa()
    assert len(recompensas) >= 5, "Deve haver pelo menos 5 recompensas"
    
    # Testa reset de recompensas
    if recompensas:
        recompensas[0].recompensa_coletada = True
        grafo.resetar_recompensas()
        assert not recompensas[0].recompensa_coletada, "Reset deve funcionar"


def testar_agente():
    """Testa funcionalidades do módulo agent.py"""
    grafo = gerar_grafo_teste(30, 6, 5)
    no_inicial = grafo.obter_no(0, 0)
    no_objetivo = grafo.obter_no(5, 4)
    
    assert no_inicial and no_objetivo, "Nós devem existir"
    
    # Cria agente
    agente = Agent(no_inicial, no_objetivo)
    assert agente.posicao_atual == no_inicial, "Posição inicial correta"
    assert not agente.chegou_ao_objetivo(), "Não deve ter chegado ao objetivo"
    
    # Testa movimento
    vizinhos = grafo.obter_vizinhos(no_inicial)
    if vizinhos:
        vizinho, custo = vizinhos[0]
        agente.mover_para(vizinho, custo)
        assert agente.custo_acumulado == custo, "Custo deve ser atualizado"
        assert len(agente.caminho_percorrido) == 2, "Caminho deve ter 2 nós"


def testar_heuristicas():
    """Testa funcionalidades do módulo heuristics.py"""
    grafo = gerar_grafo_teste(30, 6, 5)
    no1 = grafo.obter_no(0, 0)
    no2 = grafo.obter_no(3, 4)
    
    # Testa distância Manhattan
    dist = distancia_manhattan(no1, no2)
    esperada = abs(0-3) + abs(0-4)
    assert dist == esperada, f"Distância Manhattan incorreta: {dist} != {esperada}"
    
    # Testa heurística combinada
    h = heuristica_combinada(no1, no2, grafo, grafo.obter_nos_com_recompensa())
    assert h >= 0, "Heurística não pode ser negativa"
    
    # Testa cache
    limpar_cache_heuristicas()  # Deve funcionar sem erro


def testar_algoritmo_bfs():
    """Testa algoritmo BFS"""
    grafo = gerar_grafo_teste(30, 8, 6)
    no_inicial, no_objetivo = escolher_nos_aleatorios(grafo)
    
    resultado = busca_bfs(grafo, no_inicial, no_objetivo)
    assert resultado.nome_algoritmo == "BFS", "Nome do algoritmo correto"
    
    if resultado.sucesso:
        assert len(resultado.caminho_encontrado) >= 2, "Caminho deve ter pelo menos 2 nós"
        assert resultado.caminho_encontrado[0] == no_inicial, "Caminho deve começar no nó inicial"
        assert resultado.caminho_encontrado[-1] == no_objetivo, "Caminho deve terminar no objetivo"


def testar_algoritmo_dfs():
    """Testa algoritmo DFS"""
    grafo = gerar_grafo_teste(30, 8, 6)
    no_inicial, no_objetivo = escolher_nos_aleatorios(grafo)
    
    resultado = busca_dfs(grafo, no_inicial, no_objetivo)
    assert resultado.nome_algoritmo == "DFS", "Nome do algoritmo correto"


def testar_algoritmo_gulosa():
    """Testa algoritmo Gulosa"""
    grafo = gerar_grafo_teste(30, 8, 6)
    no_inicial, no_objetivo = escolher_nos_aleatorios(grafo)
    
    resultado = busca_gulosa(grafo, no_inicial, no_objetivo)
    assert resultado.nome_algoritmo == "Gulosa", "Nome do algoritmo correto"


def testar_algoritmo_a_estrela():
    """Testa algoritmo A*"""
    grafo = gerar_grafo_teste(30, 8, 6)
    no_inicial, no_objetivo = escolher_nos_aleatorios(grafo)
    
    resultado = busca_a_estrela(grafo, no_inicial, no_objetivo)
    assert resultado.nome_algoritmo == "A*", "Nome do algoritmo correto"


def testar_execucao_completa():
    """Testa execução de todos os algoritmos"""
    grafo = gerar_grafo_teste(30, 8, 6)
    no_inicial, no_objetivo = escolher_nos_aleatorios(grafo)
    
    resultados = executar_todos_algoritmos(grafo, no_inicial, no_objetivo)
    
    algoritmos_esperados = ["BFS", "DFS", "Gulosa", "A*"]
    for algoritmo in algoritmos_esperados:
        assert algoritmo in resultados, f"Algoritmo {algoritmo} deve estar nos resultados"
        assert isinstance(resultados[algoritmo].nos_expandidos, int), "Nós expandidos deve ser inteiro"
        assert resultados[algoritmo].tempo_execucao >= 0, "Tempo deve ser não-negativo"


def testar_utils():
    """Testa utilitários e visualização"""
    grafo = gerar_grafo_teste(30, 8, 6)
    
    # Testa renderização
    mapa = renderizar_mapa(grafo)
    assert len(mapa) > 0, "Mapa deve ser gerado"
    
    # Testa estatísticas
    stats = obter_estatisticas_grafo(grafo)
    assert "total_nos" in stats, "Estatísticas devem conter total de nós"
    assert stats["total_nos"] >= 30, "Deve reportar pelo menos 30 nós"
    
    # Testa validação
    no_inicial, no_objetivo = escolher_nos_aleatorios(grafo)
    valido, erros = validar_ambiente(grafo, no_inicial, no_objetivo)
    # Pode ser válido ou não, mas não deve dar erro


def testar_results():
    """Testa sistema de resultados"""
    # Cria resultados simulados
    from search_algorithms import ResultadoBusca
    
    resultado1 = ResultadoBusca("BFS")
    resultado1.definir_resultado([], 25.0, 100, 0.05)
    
    resultado2 = ResultadoBusca("A*")
    resultado2.definir_resultado([], 20.0, 80, 0.08)
    
    # Testa comparativo
    comparativo = ResultadoComparativo()
    comparativo.adicionar_resultado(resultado1)
    comparativo.adicionar_resultado(resultado2)
    
    # Testa geração de tabela
    tabela = comparativo.gerar_tabela_comparativa()
    assert len(tabela) > 0, "Tabela deve ser gerada"
    assert "BFS" in tabela, "Tabela deve conter BFS"
    assert "A*" in tabela, "Tabela deve conter A*"
    
    # Testa melhor algoritmo
    melhor = comparativo.obter_melhor_algoritmo()
    assert melhor in ["BFS", "A*"], "Deve escolher um dos algoritmos"


def testar_casos_extremos():
    """Testa casos extremos e edge cases"""
    grafo = gerar_grafo_teste(30, 6, 5)
    
    # Mesmo nó inicial e objetivo
    no = grafo.obter_no(0, 0)
    resultado = busca_bfs(grafo, no, no)
    assert resultado.sucesso, "Deve encontrar caminho para si mesmo"
    assert len(resultado.caminho_encontrado) == 1, "Caminho deve ter 1 nó"
    assert resultado.custo_total == 0, "Custo deve ser 0"


def executar_teste_completo():
    """Executa suite completa de testes"""
    print("[INICIO] TESTES DO SISTEMA DE ALGORITMOS DE BUSCA")
    print("="*60)
    
    runner = TestRunner()
    
    # Lista de testes
    testes = [
        ("Módulo Graph", testar_grafo),
        ("Módulo Agent", testar_agente), 
        ("Módulo Heuristics", testar_heuristicas),
        ("Algoritmo BFS", testar_algoritmo_bfs),
        ("Algoritmo DFS", testar_algoritmo_dfs),
        ("Algoritmo Gulosa", testar_algoritmo_gulosa),
        ("Algoritmo A*", testar_algoritmo_a_estrela),
        ("Execução Completa", testar_execucao_completa),
        ("Módulo Utils", testar_utils),
        ("Módulo Results", testar_results),
        ("Casos Extremos", testar_casos_extremos)
    ]
    
    # Executa cada teste
    for nome, func in testes:
        runner.executar_teste(nome, func)
    
    # Relatório final
    runner.relatorio_final()
    
    return runner.testes_falharam == 0


def executar_demo_teste():
    """Executa demonstração rápida do sistema funcionando"""
    print("\n DEMONSTRAÇÃO DO SISTEMA")
    print("="*40)
    
    try:
        # Gera ambiente
        print("1. Gerando ambiente...")
        grafo = gerar_grafo_teste()
        no_inicial, no_objetivo = escolher_nos_aleatorios(grafo)
        print(f"Ambiente: {len(grafo.nos)} nós")
        print(f"Rota: ({no_inicial.x},{no_inicial.y}) → ({no_objetivo.x},{no_objetivo.y})")
        
        # Executa algoritmos
        print("\n2. Executando algoritmos...")
        resultados = executar_todos_algoritmos(grafo, no_inicial, no_objetivo)
        
        # Mostra resultados resumidos
        print("\n3. Resultados:")
        for nome, resultado in resultados.items():
            status = "OK" if resultado.sucesso else "[X]"
            custo = f"{resultado.custo_total:.1f}" if resultado.sucesso else "N/A"
            print(f"   {status} {nome:<8}: Custo={custo}, Nós={resultado.nos_expandidos}")
        
        # Gera comparativo
        print("\n4. Gerando análise...")
        comparativo = ResultadoComparativo()
        comparativo.definir_info_ambiente(grafo, no_inicial, no_objetivo)
        for resultado in resultados.values():
            comparativo.adicionar_resultado(resultado)
        
        melhor = comparativo.obter_melhor_algoritmo()
        print(f"Melhor algoritmo: {melhor}")
        
        print("\n DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"\n ERRO NA DEMONSTRAÇÃO: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("SISTEMA DE TESTE - ALGORITMOS DE BUSCA")
    print("="*50)
    
    # Verifica argumentos
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Só demonstração
        sucesso = executar_demo_teste()
    else:
        # Testes completos + demonstração
        print("Executando testes completos...\n")
        sucesso_testes = executar_teste_completo()
        
        if sucesso_testes:
            sucesso = executar_demo_teste()
        else:
            print("\n Pulando demonstração devido a falhas nos testes")
            sucesso = False
    
    # Status final
    if sucesso:
        print(f"\n SISTEMA VALIDADO E FUNCIONANDO!")
        sys.exit(0)
    else:
        print(f"\n SISTEMA COM PROBLEMAS - VERIFICAR IMPLEMENTAÇÃO")
        sys.exit(1)
