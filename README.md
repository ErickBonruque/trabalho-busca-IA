# Sistema de Algoritmos de Busca com Labirintos Procedurais

Sistema que implementa algoritmos de busca em grafos com geração procedural de labirintos e diferentes tipos de terreno. Desenvolvido para demonstrar conceitos de Inteligência Artificial e análise comparativa de algoritmos.

## Algoritmos Implementados

- **BFS (Busca em Largura)** - Explora nível por nível, garante caminho ótimo em passos
- **DFS (Busca em Profundidade)** - Explora profundamente, eficiente em memória
- **Busca Gulosa** - Foco no objetivo usando heurística agressiva
- **A* (A-Estrela)** - Balanceamento ótimo entre custo real e estimativa

## Estrutura do Projeto

```
trabalho1 - Busca/
├── main.py                    # Interface principal
├── nucleo/                    # Módulos centrais
│   ├── maze_generator.py      # Geração de labirintos (DFS recursivo)
│   ├── biome_generator.py     # Biomas naturais (Perlin Noise)
│   ├── graph.py               # Grafo avançado integrado
│   └── agent.py               # Agente inteligente
├── algoritmos/                # Algoritmos de busca
│   ├── search_algorithms.py   # BFS, DFS, Gulosa, A*
│   └── heuristics.py          # Funções heurísticas otimizadas
├── utilitarios/               # Utilitários e visualização
│   ├── visualization.py       # Renderização e simulação
│   └── results.py             # Análise comparativa
├── resultados/                # Arquivos gerados pelo sistema
└── testes/                    # Testes e validações
```

## Como Executar

### Execução Principal
```bash
python main.py --demo          # Demonstração rápida
python main.py                 # Interface completa
```

### Testes do Sistema
```bash
python testes/test_sistema.py  # Validação completa
```

## Características Principais

### Tipos de Terreno
| Terreno | Símbolo | Custo | Descrição |
|---------|---------|-------|-----------|
| Sólido  | `.`     | 1     | Terreno normal |
| Arenoso | `~`     | 4     | Dificulta movimento |
| Rochoso | `^`     | 10    | Terreno acidentado |
| Pântano | `&`     | 20    | Muito difícil |

### Elementos Especiais
- **S** = Início, **G** = Objetivo, **A** = Agente
- **$** = Recompensa disponível, **\*** = Coletada
- **#** = Parede, **·** = Caminho percorrido

## Exemplo de Resultado

```
======================================================================
                    SISTEMA DE ALGORITMOS DE BUSCA
======================================================================
Ambiente: Labirinto 30x20 (257 nós)
Início: (27, 15) → Objetivo: (1, 1)
Recompensas: 32 distribuídas no ambiente

Resultados dos Algoritmos:
┌─────────┬────────┬──────┬──────────┬────────────┐
│ Alg.    │ Custo  │ Nós  │ Tempo(s) │ Recomp.    │
├─────────┼────────┼──────┼──────────┼────────────┤
│ BFS     │ 197.0  │ 177  │ 0.003    │ 16         │
│ DFS     │ 197.0  │ 101  │ 0.002    │ 16         │  
│ Gulosa  │ 197.0  │  89  │ 0.002    │ 16         │
│ A*      │ 197.0  │ 142  │ 0.004    │ 16         │
└─────────┴────────┴──────┴──────────┴────────────┘
```

## Características do Sistema

### Geração de Ambientes
- **Labirintos**: Estrutura criada com algoritmo DFS recursivo
- **Biomas**: Distribuição de terrenos usando Perlin Noise
- **Recompensas**: Distribuição estratégica pelo ambiente
- **Conectividade**: Garantia que todos os pontos são alcançáveis

### Especificações Técnicas
- **Tamanho**: Ambientes de 30x20 (600 células)
- **Terrenos**: 4 tipos com custos diferentes
- **Análise**: Comparação automática de todos os algoritmos
- **Visualização**: Mapas ASCII com legenda detalhada

---

# DOCUMENTAÇÃO

## Arquitetura do Sistema

### Pipeline de Geração de Ambientes
1. **Maze Generator** - DFS recursivo cria estrutura do labirinto
2. **Biome Generator** - Perlin Noise aplica tipos de terreno
3. **Graph Builder** - Integra labirinto com biomas e conectividade
4. **Reward Distributor** - Posiciona recompensas pelo ambiente

## Algoritmos Implementados

### 1. Gerador de Labirintos (DFS Recursivo)
```python
class MazeGenerator:
    def generate(self, width, height, seed=None):
        # Inicializa grid com paredes
        # Aplica DFS recursivo para criar caminhos
        # Valida conectividade com BFS
        # Redimensiona se necessário
        return maze_grid, valid_positions
```

**Características**:
- Garantia de conectividade total
- Estruturas variadas e desafiadoras
- Validação automática com re-geração

### 2. Gerador de Biomas (Perlin Noise)
```python
class BiomeGenerator:
    def generate_biome_map(self, width, height, scale=0.08):
        # Gera ruído Perlin 2D
        # Mapeia valores para tipos de terreno
        # Cria áreas coerentes de mesmo bioma
        return biome_matrix
```

**Mapeamento de Terrenos**:
- Noise < -0.3: Pântano (custo 20)
- -0.3 ≤ Noise < 0.0: Rochoso (custo 10)  
- 0.0 ≤ Noise < 0.4: Arenoso (custo 4)
- Noise ≥ 0.4: Sólido (custo 1)

### 3. Distribuição de Recompensas
```python
def distribuir_recompensas(grafo, caminho_principal, num_total):
    # Distribui recompensas pelo ambiente
    # Evita concentração em uma área
    # Valida acessibilidade com BFS
    # Garante distribuição equilibrada
    return posicoes_recompensas
```

## Estrutura de Classes Principais

### Classe Graph (Núcleo)
```python
class Graph:
    def __init__(self):
        self.nos = {}              # Dicionário de nós
        self.adjacencias = {}      # Lista de adjacências com custos
        self.metadata = {}         # Informações do ambiente
        
    def adicionar_no(self, no):    # Adiciona nó ao grafo
    def conectar_nos(self, no1, no2, custo):  # Conecta dois nós
    def obter_vizinhos(self, no):  # Retorna vizinhos de um nó
    def validar_conectividade(self): # Verifica se grafo é conectado
```

### Classe MazeGenerator
```python
class MazeGenerator:
    def _dfs_carve(self, x, y, grid):
        # Implementação DFS recursivo
        # Carve caminhos aleatoriamente
        # Marca células como visitadas
        
    def _ensure_connectivity(self, grid):
        # Usa BFS para verificar conectividade
        # Conecta áreas isoladas se necessário
        # Garante grafo totalmente conectado
```

### Classe BiomeGenerator
```python
class BiomeGenerator:
    def __init__(self, seed=None):
        self.perlin = PerlinNoise(seed)  # Gerador de ruído
        
    def generate_biome_for_position(self, x, y, scale):
        # Calcula ruído Perlin para posição
        # Aplica múltiplas oitavas
        # Mapeia para tipo de terreno
        return terrain_type
```

## Algoritmos de Busca Implementados

### BFS (Busca em Largura)
```python
def busca_bfs(grafo, no_inicial, no_objetivo):
    fila = deque([AgentEstado(no_inicial, [], 0.0, set())])
    visitados = set()
    nos_expandidos = 0
    
    while fila:
        estado = fila.popleft()
        # ... lógica de expansão nível por nível
    
    return ResultadoBusca(sucesso, caminho, custo, nos_expandidos, tempo, recompensas)
```

### A* (A-Estrela)
```python
def busca_a_estrela(grafo, no_inicial, no_objetivo, heuristica):
    heap = [(0.0, AgentEstado(no_inicial, [], 0.0, set()))]
    custos_g = {no_inicial: 0.0}
    nos_expandidos = 0
    
    while heap:
        f_atual, estado = heappop(heap)
        g_atual = estado.custo_acumulado
        h_atual = heuristica(estado.no, no_objetivo, grafo)
        # ... lógica de expansão com prioridade f(n) = g(n) + h(n)
    
    return ResultadoBusca(sucesso, caminho, custo, nos_expandidos, tempo, recompensas)
```

### Heurísticas Implementadas
```python
def distancia_manhattan(no1, no2, grafo=None):
    # Distância de Manhattan básica
    return abs(no1.x - no2.x) + abs(no1.y - no2.y)

def heuristica_combinada(no_atual, no_objetivo, grafo):
    # Combina distância + análise de terreno + recompensas próximas
    dist_base = distancia_manhattan(no_atual, no_objetivo)
    fator_terreno = _calcular_fator_terreno(no_atual, no_objetivo, grafo)
    bonus_recompensas = _calcular_bonus_recompensas(no_atual, grafo)
    return dist_base * fator_terreno - bonus_recompensas
```

## Ferramentas de Visualização

### Sistema de Renderização ASCII
```python
def renderizar_mapa_com_legenda(grafo, caminho=None, agente_pos=None):
    # Gera matriz visual do ambiente
    # Aplica símbolos para cada tipo de elemento
    # Adiciona legenda explicativa
    # Destaca caminho encontrado
    return mapa_ascii, legenda
```

### Simulação Animada
```python
def simular_caminho_animado(grafo, caminho, delay=0.5):
    # Limpa tela a cada frame
    # Move agente pela sequência do caminho  
    # Mostra coleta de recompensas em tempo real
    # Atualiza estatísticas dinamicamente
```

## Sistema de Análise Comparativa

### Métricas Coletadas
```python
class ResultadoBusca:
    def __init__(self, sucesso, caminho, custo_total, nos_expandidos, 
                 tempo_execucao, recompensas_coletadas):
        self.sucesso = sucesso
        self.caminho = caminho or []
        self.custo_total = custo_total
        self.nos_expandidos = nos_expandidos
        self.tempo_execucao = tempo_execucao
        self.recompensas_coletadas = recompensas_coletadas
        self.tamanho_caminho = len(caminho) if caminho else 0
```

### Análise de Eficiência
```python
def analisar_resultados(resultados):
    # Identifica melhor solução por custo
    # Algoritmo mais rápido em execução
    # Mais eficiente em nós expandidos
    # Melhor coleta de recompensas
    # Gera recomendações contextuais
    return analise_comparativa
```

## Sistema de Testes e Validação

### Testes Automatizados
```python
def testar_gerador_labirintos():
    # Valida geração de múltiplos labirintos
    # Verifica conectividade garantida
    # Testa diferentes sementes
    # Confirma dimensões corretas

def testar_algoritmos_basicos():
    # Executa todos os 4 algoritmos
    # Valida encontrar solução
    # Compara resultados esperados
    # Verifica coleta de recompensas
```

### Validações de Integridade
- **Conectividade**: BFS verifica todos os nós alcançáveis
- **Dimensões**: Ambientes atendem tamanho mínimo (30+ nós)
- **Recompensas**: Distribuição adequada pelo ambiente
- **Algoritmos**: Todos encontram soluções válidas
- **Performance**: Execução dentro de limites aceitáveis

---

*Sistema desenvolvido para disciplina de **Inteligência Artificial***