"""
Módulo responsável pela análise e comparação dos resultados dos algoritmos.
Gera tabelas comparativas e métricas de performance.
"""

import time
from algoritmos.search_algorithms import ResultadoBusca


class ResultadoComparativo:
    """Armazena e analisa resultados comparativos entre algoritmos"""
    
    def __init__(self):
        self.resultados = {}  # {nome_algoritmo: ResultadoBusca}
        self.ambiente_info = {}
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
    def adicionar_resultado(self, resultado):
        """Adiciona resultado de um algoritmo"""
        if isinstance(resultado, ResultadoBusca):
            self.resultados[resultado.nome_algoritmo] = resultado
            
    def definir_info_ambiente(self, grafo, no_inicial, no_objetivo):
        """Define informações do ambiente testado"""
        self.ambiente_info = {
            "total_nos": len(grafo.nos),
            "dimensoes": f"{grafo.largura}x{grafo.altura}",
            "no_inicial": (no_inicial.x, no_inicial.y),
            "no_objetivo": (no_objetivo.x, no_objetivo.y),
            "recompensas_disponiveis": len(grafo.obter_nos_com_recompensa()),
            "timestamp": self.timestamp
        }
        
    def gerar_tabela_comparativa(self):
        """
        Gera tabela ASCII comparativa dos resultados
        
        Returns:
            str: Tabela formatada em ASCII
        """
        if not self.resultados:
            return "Nenhum resultado para comparar"
            
        # Cabeçalho da tabela
        linhas = []
        linhas.append("=" * 85)
        linhas.append("                      COMPARAÇÃO DE ALGORITMOS DE BUSCA")
        linhas.append("=" * 85)
        
        # Informações do ambiente
        if self.ambiente_info:
            linhas.append(f"Ambiente: {self.ambiente_info['dimensoes']} "
                         f"({self.ambiente_info['total_nos']} nós)")
            linhas.append(f"Inicio: {self.ambiente_info['no_inicial']} -> "
                         f"Objetivo: {self.ambiente_info['no_objetivo']}")
            linhas.append(f"Recompensas disponíveis: {self.ambiente_info['recompensas_disponiveis']}")
            linhas.append(f"Executado em: {self.ambiente_info['timestamp']}")
            linhas.append("-" * 85)
        
        # Cabeçalho das colunas
        header = f"{'Algoritmo':<10} | {'Sucesso':<7} | {'Custo':<8} | {'Nos':<6} | " \
                f"{'Tempo(s)':<8} | {'Recomp.':<7} | {'Passos':<6}"
        linhas.append(header)
        linhas.append("-" * 85)
        
        # Dados de cada algoritmo
        for nome, resultado in self.resultados.items():
            sucesso = "[OK]" if resultado.sucesso else "[X]"
            custo = f"{resultado.custo_total:.1f}" if resultado.sucesso else "-"
            nos = str(resultado.nos_expandidos)
            tempo = f"{resultado.tempo_execucao:.3f}"
            recompensas = str(len(resultado.recompensas_no_caminho))
            passos = str(len(resultado.caminho_encontrado) - 1) if resultado.sucesso else "-"
            
            linha = f"{nome:<10} | {sucesso:<7} | {custo:<8} | {nos:<6} | " \
                   f"{tempo:<8} | {recompensas:<7} | {passos:<6}"
            linhas.append(linha)
        
        linhas.append("=" * 85)
        
        return "\n".join(linhas)
        
    def gerar_analise_detalhada(self):
        """
        Gera análise detalhada dos resultados
        
        Returns:
            str: Análise detalhada
        """
        if not self.resultados:
            return "Nenhum resultado para analisar"
            
        linhas = []
        linhas.append("\n" + "=" * 60)
        linhas.append("                 ANÁLISE DETALHADA")
        linhas.append("=" * 60)
        
        # Separa algoritmos que encontraram solução
        sucessos = {k: v for k, v in self.resultados.items() if v.sucesso}
        falhas = {k: v for k, v in self.resultados.items() if not v.sucesso}
        
        if sucessos:
            linhas.append("\nALGORITMOS QUE ENCONTRARAM SOLUCAO:")
            linhas.append("-" * 40)
            
            # Ordena por custo (melhor solução primeiro)
            sucessos_ordenados = sorted(sucessos.items(), 
                                      key=lambda x: x[1].custo_total)
            
            for i, (nome, resultado) in enumerate(sucessos_ordenados):
                rank = i + 1
                marca = "[1]" if rank == 1 else "[2]" if rank == 2 else "[3]" if rank == 3 else "[+]"
                
                linhas.append(f"\n{marca} {rank}o - {nome}")
                linhas.append(f"   Custo da solução: {resultado.custo_total:.1f}")
                linhas.append(f"   Nós expandidos: {resultado.nos_expandidos}")
                linhas.append(f"   Tempo de execução: {resultado.tempo_execucao:.3f}s")
                linhas.append(f"   Recompensas coletadas: {len(resultado.recompensas_no_caminho)}")
                linhas.append(f"   Tamanho do caminho: {len(resultado.caminho_encontrado)} nós")
                
                if resultado.recompensas_no_caminho:
                    pos_recompensas = [(r.x, r.y) for r in resultado.recompensas_no_caminho]
                    linhas.append(f"   Posições das recompensas: {pos_recompensas}")
        
        if falhas:
            linhas.append(f"\nALGORITMOS QUE FALHARAM ({len(falhas)}):")
            linhas.append("-" * 40)
            
            for nome, resultado in falhas.items():
                linhas.append(f"- {nome}: {resultado.nos_expandidos} nos expandidos "
                             f"em {resultado.tempo_execucao:.3f}s")
        
        # Análise de eficiência
        if len(sucessos) > 1:
            linhas.append(f"\nANALISE DE EFICIENCIA:")
            linhas.append("-" * 30)
            
            # Melhor custo
            melhor_custo = min(r.custo_total for r in sucessos.values())
            algoritmo_melhor_custo = [nome for nome, r in sucessos.items() 
                                    if r.custo_total == melhor_custo][0]
            linhas.append(f"Melhor solução: {algoritmo_melhor_custo} (custo {melhor_custo:.1f})")
            
            # Mais eficiente em tempo
            melhor_tempo = min(r.tempo_execucao for r in sucessos.values())
            algoritmo_melhor_tempo = [nome for nome, r in sucessos.items() 
                                    if r.tempo_execucao == melhor_tempo][0]
            linhas.append(f"Mais rápido: {algoritmo_melhor_tempo} ({melhor_tempo:.3f}s)")
            
            # Menos nós expandidos
            menos_nos = min(r.nos_expandidos for r in sucessos.values())
            algoritmo_menos_nos = [nome for nome, r in sucessos.items() 
                                 if r.nos_expandidos == menos_nos][0]
            linhas.append(f"Mais eficiente: {algoritmo_menos_nos} ({menos_nos} nós)")
            
            # Mais recompensas
            if any(len(r.recompensas_no_caminho) > 0 for r in sucessos.values()):
                mais_recompensas = max(len(r.recompensas_no_caminho) for r in sucessos.values())
                algoritmo_mais_recompensas = [nome for nome, r in sucessos.items() 
                                            if len(r.recompensas_no_caminho) == mais_recompensas][0]
                linhas.append(f"Mais recompensas: {algoritmo_mais_recompensas} ({mais_recompensas})")
        
        linhas.append("\n" + "=" * 60)
        
        return "\n".join(linhas)
        
    def gerar_recomendacoes(self):
        """
        Gera recomendações baseadas nos resultados
        
        Returns:
            str: Recomendações de uso
        """
        if not self.resultados:
            return "Sem dados para recomendações"
            
        sucessos = {k: v for k, v in self.resultados.items() if v.sucesso}
        
        if not sucessos:
            return "[X] Nenhum algoritmo encontrou solucao"
            
        linhas = []
        linhas.append("\nRECOMENDACOES DE USO")
        linhas.append("=" * 40)
        
        # Cenários específicos
        linhas.append("\nPara diferentes cenarios:")
        
        # Qualidade da solução
        if len(sucessos) > 1:
            melhor_custo = min(r.custo_total for r in sucessos.values())
            algoritmos_otimos = [nome for nome, r in sucessos.items() 
                               if abs(r.custo_total - melhor_custo) < 0.1]
            
            linhas.append(f"- Melhor qualidade: {', '.join(algoritmos_otimos)}")
        
        # Velocidade
        if 'BFS' in sucessos or 'DFS' in sucessos:
            rapidos = []
            if 'BFS' in sucessos:
                rapidos.append('BFS')
            if 'DFS' in sucessos:
                rapidos.append('DFS')
            linhas.append(f"- Execucao rapida: {', '.join(rapidos)}")
        
        # Balanceamento
        if 'A*' in sucessos:
            linhas.append("- Melhor balanceamento: A* (qualidade + eficiencia)")
        
        if 'Gulosa' in sucessos:
            linhas.append("- Foco em objetivo: Gulosa (ignora custos)")
        
        # Coleta de recompensas
        algoritmos_com_recompensas = [nome for nome, r in sucessos.items() 
                                    if len(r.recompensas_no_caminho) > 0]
        if algoritmos_com_recompensas:
            linhas.append(f"- Coleta de recompensas: {', '.join(algoritmos_com_recompensas)}")
        
        # Recomendação geral
        linhas.append(f"\nRECOMENDACAO GERAL:")
        if 'A*' in sucessos:
            linhas.append("Use A* para a maioria dos casos (otimo + eficiente)")
        elif sucessos:
            melhor_geral = min(sucessos.items(), 
                              key=lambda x: (x[1].custo_total, x[1].tempo_execucao))[0]
            linhas.append(f"Use {melhor_geral} (melhor resultado obtido)")
        
        return "\n".join(linhas)
        
    def salvar_relatorio(self, nome_arquivo="relatorio_busca.txt"):
        """
        Salva relatório completo em arquivo
        
        Args:
            nome_arquivo (str): Nome do arquivo de saída
        """
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("RELATÓRIO DE ALGORITMOS DE BUSCA\n")
                f.write("Generated by: Sistemas de Busca v1.0\n\n")
                f.write(self.gerar_tabela_comparativa())
                f.write("\n")
                f.write(self.gerar_analise_detalhada())
                f.write("\n")
                f.write(self.gerar_recomendacoes())
                f.write("\n\n--- FIM DO RELATÓRIO ---")
            
            print(f"[OK] Relatorio salvo em: {nome_arquivo}")
            return True
        except Exception as e:
            print(f"[X] Erro ao salvar relatorio: {e}")
            return False
            
    def obter_melhor_algoritmo(self):
        """
        Determina o melhor algoritmo baseado em múltiples critérios
        
        Returns:
            str: Nome do melhor algoritmo
        """
        sucessos = {k: v for k, v in self.resultados.items() if v.sucesso}
        
        if not sucessos:
            return None
            
        # Score baseado em múltiplos fatores
        scores = {}
        
        # Normaliza métricas
        custos = [r.custo_total for r in sucessos.values()]
        tempos = [r.tempo_execucao for r in sucessos.values()]
        nos_expandidos = [r.nos_expandidos for r in sucessos.values()]
        
        max_custo = max(custos) if custos else 1
        max_tempo = max(tempos) if tempos else 1
        max_nos = max(nos_expandidos) if nos_expandidos else 1
        
        for nome, resultado in sucessos.items():
            # Score menor é melhor (normalizado entre 0 e 1)
            score_custo = resultado.custo_total / max_custo
            score_tempo = resultado.tempo_execucao / max_tempo
            score_nos = resultado.nos_expandidos / max_nos
            
            # Bônus por recompensas
            bonus_recompensas = len(resultado.recompensas_no_caminho) * 0.1
            
            # Score total (peso: custo=0.5, tempo=0.2, nós=0.2, recompensas=0.1)
            score_total = (score_custo * 0.5 + score_tempo * 0.2 + 
                          score_nos * 0.2 - bonus_recompensas)
            
            scores[nome] = score_total
        
        # Retorna algoritmo com menor score (melhor)
        return min(scores.items(), key=lambda x: x[1])[0]


# Funções utilitárias para análise rápida
def comparar_resultados_simples(resultados_dict):
    """
    Comparação rápida de resultados em formato simplificado
    
    Args:
        resultados_dict (dict): Dicionário {nome: ResultadoBusca}
        
    Returns:
        str: Comparação simplificada
    """
    if not resultados_dict:
        return "Nenhum resultado fornecido"
    
    linhas = []
    linhas.append("COMPARAÇÃO RÁPIDA:")
    linhas.append("-" * 30)
    
    for nome, resultado in resultados_dict.items():
        if resultado.sucesso:
            status = f"[OK] Custo: {resultado.custo_total:.1f}"
            status += f", Tempo: {resultado.tempo_execucao:.3f}s"
            status += f", Recompensas: {len(resultado.recompensas_no_caminho)}"
        else:
            status = "[X] Falhou"
            
        linhas.append(f"{nome:<8}: {status}")
    
    return "\n".join(linhas)


# Teste básico do módulo
if __name__ == "__main__":
    print("Testando módulo results.py...")
    
    # Simula alguns resultados para teste
    resultado1 = ResultadoBusca("BFS")
    resultado1.definir_resultado([], 25.5, 150, 0.032)
    resultado1.adicionar_recompensa("dummy_reward")
    
    resultado2 = ResultadoBusca("A*")
    resultado2.definir_resultado([], 20.1, 89, 0.045)
    resultado2.adicionar_recompensa("dummy_reward")
    resultado2.adicionar_recompensa("dummy_reward2")
    
    # Cria comparativo
    comparativo = ResultadoComparativo()
    comparativo.adicionar_resultado(resultado1)
    comparativo.adicionar_resultado(resultado2)
    
    print(comparativo.gerar_tabela_comparativa())
    print(comparativo.gerar_analise_detalhada())
    print(comparativo.gerar_recomendacoes())
    
    print(f"Melhor algoritmo: {comparativo.obter_melhor_algoritmo()}")
    print("\nTeste concluído!")
