# FLUXO COMPLETO DE PROCESSAMENTO DO SISTEMA

Este documento detalha o fluxo completo de execução do Sistema de Algoritmos de Busca, desde a inicialização até a geração dos resultados finais.

## VISÃO GERAL DO FLUXO

```
Inicialização → Geração do Ambiente → Execução de Algoritmos → Análise → Relatórios
     ↓                    ↓                      ↓              ↓           ↓
  main.py          nucleo/graph.py        algoritmos/    utilitarios/  resultados/
```

---

## ETAPA 1: INICIALIZAÇÃO DO SISTEMA

### 1.1 Ponto de Entrada (`main.py`)

**Comando de execução:**
```bash
python main.py --demo
```

**Código de inicialização:**
```python
def main():
    # Carrega dependências e módulos
    from nucleo.graph import gerar_grafo_labirinto_com_biomas
    from algoritmos.search_algorithms import executar_todos_algoritmos
    
    # Exibe banner do sistema
    exibir_banner()
    
    # Inicializa ambiente
    grafo, no_inicial, no_objetivo, agente = inicializar_ambiente()
```

**Parâmetros de inicialização:**
- **Dimensões**: 30x20 (600 células total)
- **Seed**: 12345 (para reprodutibilidade)
- **Número mínimo de nós**: 30
- **Recompensas mínimas**: 5

---

## ETAPA 2: GERAÇÃO DO AMBIENTE

### 2.1 FASE 1: Geração do Labirinto (`nucleo/maze_generator.py`)

**Algoritmo DFS Recursivo:**
```python
class MazeGenerator:
    def gerar_labirinto(self, largura, altura):
        # Inicializa grid com paredes
        grid = [[True for _ in range(largura)] for _ in range(altura)]
        
        # Escolhe ponto inicial aleatório
        inicio_x = self.random.randrange(1, largura, 2)
        inicio_y = self.random.randrange(1, altura, 2)
        
        # Aplica DFS recursivo
        self._dfs_carve(grid, inicio_x, inicio_y, largura, altura)
        
        return grid
    
    def _dfs_carve(self, grid, x, y, largura, altura):
        grid[y][x] = False  # Marca como caminho
        
        direcoes = [(0, -2), (0, 2), (2, 0), (-2, 0)]
        self.random.shuffle(direcoes)
        
        for dx, dy in direcoes:
            nx, ny = x + dx, y + dy
            
            if 0 <= nx < largura and 0 <= ny < altura and grid[ny][nx]:
                grid[y + dy//2][x + dx//2] = False  # Remove parede
                self._dfs_carve(grid, nx, ny, largura, altura)  # Recursão
```

**Verificação de conectividade:**
```python
def _validar_conectividade_bfs(self, grid):
    # BFS para verificar se todos os pontos livres são alcançáveis
    inicio = self._encontrar_primeiro_livre(grid)
    visitados = set()
    fila = deque([inicio])
    
    while fila:
        x, y = fila.popleft()
        if (x, y) in visitados:
            continue
        visitados.add((x, y))
        
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and
                not grid[ny][nx] and (nx, ny) not in visitados):
                fila.append((nx, ny))
    
    livres_total = sum(1 for row in grid for cell in row if not cell)
    return len(visitados) == livres_total
```

### 2.2 FASE 2: Geração de Biomas (`nucleo/biome_generator.py`)

**Algoritmo Perlin Noise:**
```python
class BiomeGenerator:
    def gerar_mapa_biomas(self, largura, altura):
        mapa_biomas = [[TipoTerreno.SOLIDO for _ in range(largura)] 
                       for _ in range(altura)]
        
        for y in range(altura):
            for x in range(largura):
                noise_value = self._perlin_noise_2d(x, y, 0.08)
                tipo_terreno = self._mapear_ruido_para_terreno(noise_value)
                mapa_biomas[y][x] = tipo_terreno
        
        return mapa_biomas
    
    def _mapear_ruido_para_terreno(self, noise_value):
        if noise_value < -0.3:
            return TipoTerreno.PANTANO    # Custo 20
        elif noise_value < 0.0:
            return TipoTerreno.ROCHOSO    # Custo 10
        elif noise_value < 0.4:
            return TipoTerreno.ARENOSO    # Custo 4
        else:
            return TipoTerreno.SOLIDO     # Custo 1
```

### 2.3 FASE 3: Construção do Grafo

**Integração Labirinto + Biomas:**
```python
def _construir_grafo_integrado(grid_labirinto, mapa_biomas):
    grafo = Graph()
    nos_criados = {}
    
    # Cria nós para células livres
    for y in range(len(grid_labirinto)):
        for x in range(len(grid_labirinto[0])):
            if not grid_labirinto[y][x]:  # Se não é parede
                tipo_terreno = mapa_biomas[y][x]
                no = No(x, y, tipo_terreno)
                grafo.adicionar_no(no)
                nos_criados[(x, y)] = no
    
    # Conecta nós adjacentes (4-conectividade)
    for (x, y), no in nos_criados.items():
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in nos_criados:
                vizinho = nos_criados[(nx, ny)]
                custo = vizinho.tipo_terreno.value
                grafo.conectar_nos(no, vizinho, custo)
    
    return grafo, nos_criados
```

---

## ETAPA 3: EXECUÇÃO DOS ALGORITMOS

### 3.1 BFS (Busca em Largura)

```python
def busca_bfs(grafo, no_inicial, no_objetivo):
    fila = deque([AgentEstado(no_inicial, 0, 0, None)])
    visitados = set([no_inicial])
    nos_expandidos = 0
    
    while fila:
        estado_atual = fila.popleft()
        nos_expandidos += 1
        
        if estado_atual.no == no_objetivo:
            caminho = _reconstruir_caminho(estado_atual)
            custo_total = calcular_custo_caminho(caminho, grafo)
            return ResultadoBusca(True, caminho, custo_total, nos_expandidos)
        
        for vizinho, custo_aresta in grafo.adjacencias[estado_atual.no]:
            if vizinho not in visitados:
                visitados.add(vizinho)
                novo_estado = AgentEstado(vizinho, estado_atual.custo_g + custo_aresta, 0, estado_atual)
                fila.append(novo_estado)
```

### 3.2 A* (A-Estrela)

```python
def busca_a_estrela(grafo, no_inicial, no_objetivo):
    h_inicial = heuristica_combinada(no_inicial, no_objetivo, grafo)
    fila_prioridade = [AgentEstado(no_inicial, 0, h_inicial, None)]
    visitados = {}
    
    while fila_prioridade:
        estado_atual = heapq.heappop(fila_prioridade)
        
        if estado_atual.no == no_objetivo:
            return _construir_resultado(estado_atual, grafo)
        
        for vizinho, custo_aresta in grafo.adjacencias[estado_atual.no]:
            novo_custo_g = estado_atual.custo_g + custo_aresta
            
            if novo_custo_g < visitados.get(vizinho, float('inf')):
                visitados[vizinho] = novo_custo_g
                h_vizinho = heuristica_combinada(vizinho, no_objetivo, grafo)
                f_vizinho = novo_custo_g + h_vizinho
                novo_estado = AgentEstado(vizinho, novo_custo_g, f_vizinho, estado_atual)
                heapq.heappush(fila_prioridade, novo_estado)
```

---

## ETAPA 4: ANÁLISE E RELATÓRIOS

### 4.1 Análise Comparativa

```python
class ResultadoComparativo:
    def _analisar_resultados(self):
        sucessos = [r for r in self.resultados.values() if r.sucesso]
        
        if sucessos:
            self.melhor_custo = min(sucessos, key=lambda x: x.custo_total)
            self.mais_rapido = min(sucessos, key=lambda x: x.tempo_execucao)
            self.mais_eficiente = min(sucessos, key=lambda x: x.nos_expandidos)
            self.mais_recompensas = max(sucessos, key=lambda x: len(x.recompensas_no_caminho))
```

### 4.2 Geração de Relatórios

**Salvamento organizado:**
```python
def salvar_relatorios_finais():
    # Cria pasta resultados se não existir
    os.makedirs("resultados", exist_ok=True)
    
    # Salva relatório completo
    relatorio_path = "resultados/demo_relatorio.txt"
    comparativo.salvar_relatorio(relatorio_path)
    
    # Salva mapa separadamente
    mapa_path = "resultados/mapa_atual.txt"
    mapa_conteudo = f"""MAPA DO AMBIENTE ATUAL
Ambiente: {grafo.largura}x{grafo.altura} ({len(grafo.nos)} nós)
Início: ({no_inicial.x}, {no_inicial.y}) -> Objetivo: ({no_objetivo.x}, {no_objetivo.y})
Recompensas: {len([n for n in grafo.nos.values() if n.tem_recompensa])}

{renderizar_mapa_com_legenda(grafo, agente)}
"""
    
    with open(mapa_path, 'w', encoding='utf-8') as f:
        f.write(mapa_conteudo)
```

---

## VERIFICAÇÕES E VALIDAÇÕES

### Validações Automáticas

1. **Conectividade do Grafo**: BFS verifica se todos os nós são alcançáveis
2. **Dimensões Mínimas**: Garante pelo menos 30 nós
3. **Recompensas Suficientes**: Mínimo de 5 recompensas distribuídas
4. **Alcançabilidade do Objetivo**: Testa caminho do início ao objetivo
5. **Integridade dos Algoritmos**: Verifica se todos encontram soluções

### Métricas Coletadas

- **Custo da solução** (soma dos custos de terreno)
- **Nós expandidos** (eficiência computacional)
- **Tempo de execução** (performance)
- **Recompensas coletadas** (estratégia de coleta)
- **Tamanho do caminho** (número de passos)

### Arquivos de Saída

- `resultados/demo_relatorio.txt` - Relatório completo com análise
- `resultados/mapa_atual.txt` - Visualização ASCII do ambiente
- Console - Feedback em tempo real do progresso

---

**Sistema implementa pipeline completo: Geração → Busca → Análise → Relatório, com validações em cada etapa e métricas detalhadas para comparação de algoritmos.**
