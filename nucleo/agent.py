"""
Módulo responsável pela representação e lógica do agente inteligente.
Gerencia posição, objetivo, coleta de recompensas e histórico de movimento.
"""

from .graph import Graph, No, TipoTerreno


class Agent:
    
    def __init__(self, posicao_inicial, objetivo):
        """
        Inicializa o agente
{{ ... }}
        
        Args:
            posicao_inicial (No): Nó de posição inicial
            objetivo (No): Nó objetivo/destino
        """
        self.posicao_inicial = posicao_inicial
        self.posicao_atual = posicao_inicial
        self.objetivo = objetivo
        self.recompensas_coletadas = []
        self.caminho_percorrido = [posicao_inicial]
        self.custo_acumulado = 0
        
    def mover_para(self, no, custo_movimento):
        """
        Move o agente para um novo nó
        
        Args:
            no (No): Nó de destino
            custo_movimento (int): Custo do movimento
        """
        self.posicao_atual = no
        self.caminho_percorrido.append(no)
        self.custo_acumulado += custo_movimento
        
        # Verifica se há recompensa no nó atual
        self.coletar_recompensa(no)
        
    def coletar_recompensa(self, no):
        """
        Coleta recompensa se disponível no nó atual
        
        Args:
            no (No): Nó atual para verificar recompensa
            
        Returns:
            bool: True se coletou recompensa, False caso contrário
        """
        if no.tem_recompensa and not no.recompensa_coletada:
            no.recompensa_coletada = True
            self.recompensas_coletadas.append(no)
            return True
        return False
        
    def calcular_custo_total(self):
        """Calcula o custo total do caminho percorrido"""
        return self.custo_acumulado
        
    def chegou_ao_objetivo(self):
        """Verifica se o agente chegou ao objetivo"""
        return self.posicao_atual == self.objetivo
        
    def obter_caminho(self):
        """Retorna o caminho completo percorrido"""
        return self.caminho_percorrido.copy()
        
    def obter_recompensas_coletadas(self):
        """Retorna lista de recompensas coletadas"""
        return self.recompensas_coletadas.copy()
        
    def resetar_estado(self):
        """Reseta o agente para o estado inicial"""
        self.posicao_atual = self.posicao_inicial
        self.caminho_percorrido = [self.posicao_inicial]
        self.custo_acumulado = 0
        
        # Limpa recompensas coletadas mas não reseta o estado no grafo
        # (isso é responsabilidade do grafo)
        self.recompensas_coletadas = []
        
    def obter_estatisticas(self):
        """
        Retorna estatísticas do agente
        
        Returns:
            dict: Dicionário com estatísticas
        """
        return {
            'posicao_atual': (self.posicao_atual.x, self.posicao_atual.y),
            'objetivo': (self.objetivo.x, self.objetivo.y),
            'custo_total': self.custo_acumulado,
            'passos_dados': len(self.caminho_percorrido) - 1,
            'recompensas_coletadas': len(self.recompensas_coletadas),
            'chegou_objetivo': self.chegou_ao_objetivo()
        }
        
    def obter_caminho_coordenadas(self):
        """
        Retorna o caminho como lista de coordenadas (x, y)
        
        Returns:
            list: Lista de tuplas (x, y) representando o caminho
        """
        return [(no.x, no.y) for no in self.caminho_percorrido]
        
    def simular_caminho(self, caminho_nos, grafo):
        """
        Simula o agente percorrendo um caminho específico
        
        Args:
            caminho_nos (list): Lista de nós do caminho
            grafo (Graph): Grafo do ambiente
            
        Returns:
            bool: True se conseguiu simular todo o caminho
        """
        if not caminho_nos or caminho_nos[0] != self.posicao_inicial:
            return False
            
        self.resetar_estado()
        
        for i in range(1, len(caminho_nos)):
            no_anterior = caminho_nos[i-1]
            no_atual = caminho_nos[i]
            
            # Encontra o custo do movimento entre os nós
            vizinhos = grafo.obter_vizinhos(no_anterior)
            custo_movimento = None
            
            for vizinho, custo in vizinhos:
                if vizinho == no_atual:
                    custo_movimento = custo
                    break
                    
            if custo_movimento is None:
                # Nós não são adjacentes - caminho inválido
                return False
                
            self.mover_para(no_atual, custo_movimento)
            
        return True
        
    def __str__(self):
        pos_atual = f"({self.posicao_atual.x}, {self.posicao_atual.y})"
        objetivo = f"({self.objetivo.x}, {self.objetivo.y})"
        return f"Agent[Pos: {pos_atual}, Obj: {objetivo}, Custo: {self.custo_acumulado}]"
        
    def __repr__(self):
        return self.__str__()


class AgentEstado:
    """
    Classe para capturar um estado específico do agente
    Útil para algoritmos de busca que precisam rastrear estados
    """
    
    def __init__(self, no, custo_g=0, custo_f=0, pai=None):
        """
        Inicializa um estado do agente
        
        Args:
            no (No): Nó atual
            custo_g (float): Custo real do caminho até aqui
            custo_f (float): Custo total (g + h) para A*
            pai (AgentEstado): Estado pai no caminho
        """
        self.no = no
        self.custo_g = custo_g
        self.custo_f = custo_f
        self.pai = pai
        
    def reconstruir_caminho(self):
        """
        Reconstrói o caminho desde o estado inicial até este estado
        
        Returns:
            list: Lista de nós do caminho
        """
        caminho = []
        estado_atual = self
        
        while estado_atual is not None:
            caminho.append(estado_atual.no)
            estado_atual = estado_atual.pai
            
        return list(reversed(caminho))
        
    def __eq__(self, other):
        return isinstance(other, AgentEstado) and self.no == other.no
        
    def __hash__(self):
        return hash(self.no)
        
    def __lt__(self, other):
        """Comparação para fila de prioridade (menor custo_f tem prioridade)"""
        if self.custo_f != other.custo_f:
            return self.custo_f < other.custo_f
        # Desempate por coordenadas para consistência
        return (self.no.x, self.no.y) < (other.no.x, other.no.y)
        
    def __str__(self):
        pos = f"({self.no.x}, {self.no.y})"
        return f"Estado[Pos: {pos}, g: {self.custo_g:.1f}, f: {self.custo_f:.1f}]"


# Teste básico do módulo
if __name__ == "__main__":
    print("Testando módulo agent.py...")
    
    from graph import gerar_grafo_teste
    
    # Gera grafo de teste
    grafo = gerar_grafo_teste()
    
    # Cria agente
    no_inicial = grafo.obter_no(0, 0)
    no_objetivo = grafo.obter_no(7, 5)
    
    if no_inicial and no_objetivo:
        agente = Agent(no_inicial, no_objetivo)
        print(f"Agente criado: {agente}")
        
        # Testa movimento
        vizinhos = grafo.obter_vizinhos(no_inicial)
        if vizinhos:
            vizinho, custo = vizinhos[0]
            agente.mover_para(vizinho, custo)
            print(f"Após movimento: {agente}")
            
        print(f"Estatísticas: {agente.obter_estatisticas()}")
    else:
        print("Erro: Não foi possível criar nós inicial/objetivo")
