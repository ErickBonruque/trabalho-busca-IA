"""
Ponto de entrada principal do sistema de algoritmos de busca.
Orquestra a execução dos algoritmos e interface do usuário.
"""

import sys
import os
import config

# Adiciona o diretório atual ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nucleo.graph import gerar_grafo_labirinto_com_biomas
from nucleo.agent import Agent
from algoritmos.search_algorithms import executar_todos_algoritmos
from utilitarios.visualization import renderizar_mapa_com_legenda, obter_estatisticas_grafo, escolher_nos_aleatorios, limpar_console
from utilitarios.results import ResultadoComparativo


def exibir_banner():
    """Exibe banner inicial do sistema"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                SISTEMA DE ALGORITMOS DE BUSCA                ║
║                      Trabalho Acadêmico                      ║
║                    Inteligência Artificial                   ║
╠══════════════════════════════════════════════════════════════╣
║  Implementa e compara: BFS, DFS, Busca Gulosa e A*           ║
║  Com suporte a terrenos variados e coleta de recompensas     ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def inicializar_ambiente():
    """
    Inicializa o ambiente de teste
    
    Returns:
        tuple: (grafo, no_inicial, no_objetivo, agente)
    """
    print("Gerando labirinto com biomas...")
    
    # Gera grafo avançado com labirinto e biomas
    resultado = gerar_grafo_labirinto_com_biomas(
        tamanho_min=config.MAPA_TAMANHO_MIN, 
        largura=config.MAPA_LARGURA, 
        altura=config.MAPA_ALTURA, 
        seed=config.SEED
    )
    
    if not resultado:
        return None, None, None, None
    
    grafo, no_inicial, no_objetivo = resultado
    
    # Cria agente
    agente = Agent(no_inicial, no_objetivo)
    
    # Valida conectividade
    if not grafo.validar_conectividade():
        print("Aviso: Grafo nao eh completamente conectado")
    
    # Exibe estatísticas
    stats = obter_estatisticas_grafo(grafo)
    print(f"[OK] Ambiente criado:")
    print(f"   Dimensões: {stats['dimensoes']}")
    print(f"   Total de nós: {stats['total_nos']}")
    print(f"   Recompensas: {stats['recompensas']}")
    print(f"   Conectividade: {stats['conectividade']}")
    print(f"   Inicio: ({no_inicial.x}, {no_inicial.y}) -> Objetivo: ({no_objetivo.x}, {no_objetivo.y})")
    
    return grafo, no_inicial, no_objetivo, agente


def executar_simulacao_completa(grafo, no_inicial, no_objetivo, agente):
    """
    Executa simulação completa de todos os algoritmos
    
    Returns:
        ResultadoComparativo: Resultados da simulação
    """
    print("\n" + "="*60)
    print("EXECUTANDO SIMULACAO DOS ALGORITMOS")
    print("="*60)
    
    # Executa todos os algoritmos
    resultados = executar_todos_algoritmos(grafo, no_inicial, no_objetivo)
    
    # Cria objeto comparativo
    comparativo = ResultadoComparativo()
    comparativo.definir_info_ambiente(grafo, no_inicial, no_objetivo)
    
    # Adiciona resultados
    for resultado in resultados.values():
        comparativo.adicionar_resultado(resultado)
    
    return comparativo, resultados


def menu_principal():
    """
    Exibe menu principal e gerencia interações
    """
    while True:
        print("\n" + "="*50)
        print("           MENU PRINCIPAL")
        print("="*50)
        print("1. Executar simulacao completa")
        print("2. Ver mapa do ambiente atual")
        print("3. Simular movimento de algoritmo")
        print("4. Gerar novo ambiente")
        print("5. Salvar relatorio")
        print("6. Sair")
        print("="*50)
        
        try:
            opcao = input("Escolha uma opção (1-6): ").strip()
            
            if opcao == "1":
                return "executar_simulacao"
            elif opcao == "2":
                return "ver_mapa"
            elif opcao == "3":
                return "simular_movimento"
            elif opcao == "4":
                return "novo_ambiente"
            elif opcao == "5":
                return "salvar_relatorio"
            elif opcao == "6":
                print("Encerrando programa...")
                return "sair"
            else:
                print("[X] Opcao invalida! Escolha entre 1-6.")
                
        except KeyboardInterrupt:
            print("\nEncerrando programa...")
            return "sair"
        except Exception as e:
            print(f"[X] Erro: {e}")


def escolher_algoritmo_para_simulacao():
    """Permite escolher algoritmo para simulação visual"""
    print("\nEscolha o algoritmo para simular:")
    print("1. BFS (Busca em Largura)")
    print("2. DFS (Busca em Profundidade)")
    print("3. Gulosa (Busca Gulosa)")
    print("4. A* (A-Estrela)")
    print("5. Voltar ao menu")
    
    try:
        opcao = input("Escolha (1-5): ").strip()
        algoritmos = {
            "1": "BFS",
            "2": "DFS", 
            "3": "Gulosa",
            "4": "A*"
        }
        
        if opcao in algoritmos:
            return algoritmos[opcao]
        elif opcao == "5":
            return None
        else:
            print("[X] Opcao invalida!")
            return None
            
    except Exception as e:
        print(f"[X] Erro: {e}")
        return None


def main():
    """Função principal do sistema"""
    # Estado global da aplicação
    grafo = None
    no_inicial = None
    no_objetivo = None
    agente = None
    ultimo_comparativo = None
    ultimos_resultados = None
    
    try:
        # Banner inicial
        exibir_banner()
        
        # Inicializa ambiente inicial
        grafo, no_inicial, no_objetivo, agente = inicializar_ambiente()
        if not grafo:
            print("[X] Falha na inicializacao. Encerrando...")
            return
        
        # Loop principal
        while True:
            opcao = menu_principal()
            
            if opcao == "sair":
                break
                
            elif opcao == "executar_simulacao":
                if grafo and no_inicial and no_objetivo:
                    comparativo, resultados = executar_simulacao_completa(
                        grafo, no_inicial, no_objetivo, agente)
                    
                    # Exibe resultados
                    print("\n" + comparativo.gerar_tabela_comparativa())
                    print(comparativo.gerar_analise_detalhada())
                    print(comparativo.gerar_recomendacoes())
                    
                    # Salva para uso posterior
                    ultimo_comparativo = comparativo
                    ultimos_resultados = resultados
                    
                    print("\n[INFO] Simulacao concluida! Retornando ao menu principal...")
                else:
                    print("[X] Ambiente nao inicializado!")
                    
            elif opcao == "ver_mapa":
                if grafo:
                    limpar_console()
                    print("MAPA DO AMBIENTE ATUAL")
                    print("="*50)
                    print(renderizar_mapa_com_legenda(grafo, agente))
                    print("\n[INFO] Retornando ao menu principal...")
                else:
                    print("[X] Nenhum ambiente carregado!")
                    
            elif opcao == "simular_movimento":
                if ultimos_resultados:
                    algoritmo = escolher_algoritmo_para_simulacao()
                    if algoritmo and algoritmo in ultimos_resultados:
                        resultado = ultimos_resultados[algoritmo]
                        if resultado.sucesso:
                            print(f"\nSimulando {algoritmo}...")
                            agente.resetar_estado()
                            grafo.resetar_recompensas()
                            
                            try:
                                entrada = input(f"Velocidade (segundos por passo, padrão {config.SIMULACAO_VELOCIDADE_PADRAO}): ")
                                velocidade = float(entrada) if entrada else config.SIMULACAO_VELOCIDADE_PADRAO
                            except:
                                velocidade = config.SIMULACAO_VELOCIDADE_PADRAO
                            
                            simular_movimento(grafo, agente, resultado.caminho_encontrado, velocidade)
                            print("\n[INFO] Simulacao de movimento concluida! Retornando ao menu principal...")
                        else:
                            print(f"[X] {algoritmo} nao encontrou solucao!")
                    elif algoritmo:
                        print(f"[X] Algoritmo {algoritmo} nao foi executado!")
                else:
                    print("[X] Execute uma simulacao primeiro!")
                    
            elif opcao == "novo_ambiente":
                print("Gerando novo ambiente...")
                grafo, no_inicial, no_objetivo, agente = inicializar_ambiente()
                ultimo_comparativo = None
                ultimos_resultados = None
                if grafo:
                    print("[OK] Novo ambiente criado com sucesso!")
                    
            elif opcao == "salvar_relatorio":
                if ultimo_comparativo:
                    nome_padrao = config.ARQUIVO_RELATORIO_PADRAO
                    nome_arquivo = input(f"Nome do arquivo (padrão: {nome_padrao}): ").strip()
                    if not nome_arquivo:
                        nome_arquivo = nome_padrao
                    
                    # Garante extensão .txt e previne .py
                    if nome_arquivo.endswith('.py'):
                        nome_arquivo = nome_arquivo[:-3]
                    if not nome_arquivo.endswith('.txt'):
                        nome_arquivo += ".txt"
                    
                    # Garante que será salvo na pasta resultados
                    dir_resultados = config.DIR_RESULTADOS
                    relatorio_path = os.path.join(dir_resultados, nome_arquivo)
                    mapa_path = os.path.join(dir_resultados, f"mapa_{nome_arquivo.replace('.txt', '')}.txt")
                    
                    # Cria pasta resultados se não existir
                    os.makedirs(dir_resultados, exist_ok=True)
                    
                    if ultimo_comparativo.salvar_relatorio(relatorio_path):
                        print(f"[OK] Relatorio salvo em: {relatorio_path}")
                        
                        # Salva mapa separadamente se disponível
                        if grafo:
                            try:
                                mapa_conteudo = f"""MAPA DO AMBIENTE ATUAL - SISTEMA DE ALGORITMOS DE BUSCA
============================================================
Ambiente: {grafo.largura}x{grafo.altura} ({len(grafo.nos)} nós)
Início: ({no_inicial.x}, {no_inicial.y}) -> Objetivo: ({no_objetivo.x}, {no_objetivo.y})
Recompensas disponíveis: {len([n for n in grafo.nos.values() if n.tem_recompensa])}
Gerado em: {ultimo_comparativo.timestamp}

{renderizar_mapa_com_legenda(grafo, agente)}
============================================================
"""
                                with open(mapa_path, 'w', encoding='utf-8') as f:
                                    f.write(mapa_conteudo)
                                print(f"[OK] Mapa salvo em: {mapa_path}")
                            except Exception as e:
                                print(f"[AVISO] Erro ao salvar mapa: {e}")
                    else:
                        print("[X] Erro ao salvar relatorio!")
                else:
                    print("[X] Execute uma simulacao primeiro!")
                    print("\n[INFO] Retornando ao menu principal...")
            
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuario.")
    except Exception as e:
        print(f"\n[X] Erro inesperado: {e}")
    finally:
        print("Obrigado por usar o Sistema de Algoritmos de Busca!")


def executar_demo_rapida():
    """Executa demonstração rápida sem interação do usuário"""
    print("DEMONSTRACAO RAPIDA - ALGORITMOS DE BUSCA")
    print("="*60)
    
    # Gera ambiente
    grafo, no_inicial, no_objetivo, agente = inicializar_ambiente()
    if not grafo:
        print("[X] Falha na inicializacao da demo")
        return
    
    # Executa algoritmos
    comparativo, resultados = executar_simulacao_completa(grafo, no_inicial, no_objetivo, agente)
    
    # Mostra resultados
    print(comparativo.gerar_tabela_comparativa())
    print(comparativo.gerar_analise_detalhada())
    print(comparativo.gerar_recomendacoes())
    
    # Salva relatório automaticamente na pasta resultados
    dir_resultados = config.DIR_RESULTADOS
    relatorio_path = os.path.join(dir_resultados, config.ARQUIVO_DEMO_RELATORIO)
    mapa_path = os.path.join(dir_resultados, config.ARQUIVO_DEMO_MAPA)
    
    # Cria pasta resultados se não existir
    os.makedirs(dir_resultados, exist_ok=True)
    
    # Salva relatório completo
    comparativo.salvar_relatorio(relatorio_path)
    
    # Salva mapa separadamente
    mapa_conteudo = f"""MAPA DO AMBIENTE ATUAL - SISTEMA DE ALGORITMOS DE BUSCA
============================================================
Ambiente: {grafo.largura}x{grafo.altura} ({len(grafo.nos)} nós)
Início: ({no_inicial.x}, {no_inicial.y}) -> Objetivo: ({no_objetivo.x}, {no_objetivo.y})
Recompensas disponíveis: {len([n for n in grafo.nos.values() if n.tem_recompensa])}
Gerado em: {comparativo.timestamp}

{renderizar_mapa_com_legenda(grafo, agente)}
============================================================
"""
    
    try:
        with open(mapa_path, 'w', encoding='utf-8') as f:
            f.write(mapa_conteudo)
        print(f"\n[OK] Demonstracao concluida!")
        print(f"[OK] Relatorio salvo em: {relatorio_path}")
        print(f"[OK] Mapa salvo em: {mapa_path}")
    except Exception as e:
        print(f"\n[X] Erro ao salvar mapa: {e}")
        print(f"[OK] Relatorio salvo em: {relatorio_path}")


if __name__ == "__main__":
    # Verifica se deve executar demo rápida
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        executar_demo_rapida()
    else:
        main()
