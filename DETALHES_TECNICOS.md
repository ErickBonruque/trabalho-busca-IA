# Detalhes Técnicos e Fluxo do Sistema

Este documento detalha a engenharia por trás da modelagem do mundo, o funcionamento dos algoritmos procedurais e o fluxo de execução do projeto.

---

## 1. Modelagem do Mundo (Passo a Passo)

A construção do ambiente segue um pipeline sequencial para garantir que o mundo seja navegável, interessante e logicamente consistente.

### Etapa 1: Estrutura do Labirinto (MazeGenerator)
**Objetivo**: Criar a "ossatura" do mundo, definindo onde é parede e onde é caminho caminhável.
1.  **Inicialização**: Começa com uma grade preenchida inteiramente por paredes (`True`).
2.  **Escavação (DFS Recursivo)**:
    *   O algoritmo começa em `(1,1)`.
    *   Escolhe uma direção aleatória (Norte, Sul, Leste, Oeste).
    *   Pula duas células na direção escolhida. Se a célula de destino for uma parede, remove a parede entre elas e a parede de destino.
    *   Chama a si mesmo recursivamente na nova posição.
    *   Isso cria corredores longos e sinuosos ("Perfect Maze").
3.  **Conectividade**: Um algoritmo de `Flood Fill` verifica se todas as áreas abertas são acessíveis. Se houver ilhas isoladas, elas são conectadas à força à área principal.

### Etapa 2: Aplicação de Biomas (BiomeGenerator)
**Objetivo**: Dar "vida" ao labirinto, atribuindo tipos de terreno (custos) aos caminhos criados.
1.  **Geração de Ruído**: Para cada coordenada `(x, y)` do labirinto, gera-se um valor de ruído Perlin (entre -1 e 1).
2.  **Mapeamento de Terrenos**: O valor do ruído define o tipo de terreno:
    *   **Pântano** (Custo 20): Ruído < -0.3
    *   **Rochoso** (Custo 10): -0.3 <= Ruído < 0.0
    *   **Arenoso** (Custo 4): 0.0 <= Ruído < 0.4
    *   **Sólido** (Custo 1): Ruído >= 0.4
3.  **Resultado**: O mapa agora tem regiões coerentes (ex: um grande pântano no canto, uma planície no centro), e não apenas terrenos aleatórios espalhados.

### Etapa 3: Construção do Grafo (Graph Builder)
**Objetivo**: Converter a matriz visual em uma estrutura de dados para algoritmos de busca.
1.  Cada célula de "caminho" vira um **Nó**.
2.  O sistema verifica os 4 vizinhos (N, S, L, O) de cada nó.
3.  Se um vizinho é acessível, cria-se uma **Aresta** direcionada.
4.  **Peso da Aresta**: É determinado pelo custo do terreno do nó de *destino*. (Ex: Ir para um pântano custa 20).

### Etapa 4: Distribuição de Objetivos
1.  **Início e Fim**: Definidos aleatoriamente em posições válidas distantes entre si.
2.  **Recompensas**: Espalhadas pelo mapa em posições válidas aleatórias, garantindo que não bloqueiem passagens estreitas.

---

## 2. O que o Agente "Vê" na Busca

Diferente de um ser humano que olha o mapa de cima, o agente tem uma visão limitada e baseada em dados estruturados durante a execução dos algoritmos.

### Informações Conhecidas (A Priori)
*   **Estado Inicial**: Coordenadas `(x, y)` de onde ele está.
*   **Objetivo Final**: Coordenadas `(x, y)` de onde ele precisa chegar. O agente sabe *onde* é o destino, permitindo calcular distâncias (heurísticas), mas não sabe *como* chegar lá.

### Informações Descobertas (Durante a Exploração)
Ao expandir um nó atual, o agente descobre:
1.  **Vizinhos**: Quais células adjacentes são acessíveis (não são paredes).
2.  **Custo de Movimento**: Quanto custa mover-se para cada vizinho (baseado no terreno).
3.  **Recompensas**: Se o vizinho contém uma recompensa (usado para heurísticas avançadas).

### O que o Agente NÃO Sabe
*   O caminho completo (até encontrá-lo).
*   Obstáculos distantes (só descobre paredes quando tenta expandir para elas).
*   O "formato" global do labirinto.

---

## 3. Como Funciona o Perlin Noise

O Perlin Noise é um algoritmo de **ruído gradiente** usado para gerar texturas naturais. Ao contrário do `random()` puro, que cria "ruído branco" caótico, o Perlin Noise cria transições suaves.

### Mecânica Interna (Implementação no Projeto)

1.  **Grade de Vetores (Lattice)**:
    *   Imagine uma grade invisível sobre o mapa. Em cada ponto inteiro dessa grade, escolhemos um vetor de gradiente pseudo-aleatório.
    
2.  **Interpolação (Lerp e Fade)**:
    *   Para calcular o valor em um ponto qualquer `(x, y)` dentro de uma célula da grade, calculamos a distância para os 4 cantos.
    *   **Dot Product**: Calculamos o produto escalar entre o vetor de distância e o vetor de gradiente de cada canto.
    *   **Suavização (Fade)**: Usamos a função `6t^5 - 15t^4 + 10t^3` (curva S) para suavizar a transição.
    *   **Interpolação Linear**: Misturamos os valores dos 4 cantos baseados na proximidade.

3.  **Resultado Visual**:
    *   Isso gera ondas suaves de valores altos e baixos.
    *   Valores próximos no espaço têm valores numéricos próximos, criando "manchas" ou "regiões" (os biomas), em vez de pixels aleatórios.

---

## 4. Fluxo Geral do Projeto

O ciclo de vida da aplicação segue esta ordem cronológica:

### A. Inicialização (`main.py`)
1.  O sistema carrega módulos e define configurações iniciais.
2.  Chama `gerar_grafo_labirinto_com_biomas()` para criar o mundo.
3.  Instancia a classe `Agent` com as posições de início e fim.

### B. Geração (`maze_generator.py` + `biome_generator.py`)
1.  Cria a matriz de paredes/caminhos.
2.  Calcula o mapa de ruído para biomas.
3.  Combina ambos para criar o objeto `Graph`.
4.  Valida se existe caminho possível do Início ao Fim (conectividade).

### C. Execução dos Algoritmos (`search_algorithms.py`)
Quando o usuário solicita uma simulação:
1.  O sistema roda **todos** os 4 algoritmos (BFS, DFS, Gulosa, A*) sequencialmente no **mesmo** mapa.
2.  Cada algoritmo retorna um objeto `ResultadoBusca` contendo:
    *   Caminho encontrado (lista de nós).
    *   Custo total.
    *   Nós expandidos (esforço computacional).
    *   Tempo de execução.

### D. Análise e Visualização (`visualization.py`)
1.  Os resultados são comparados automaticamente.
2.  O sistema gera representações ASCII do mapa, desenhando o caminho do algoritmo vencedor ou solicitado.
3.  Animação passo-a-passo mostra o agente percorrendo o labirinto no terminal.

### E. Persistência (`results.py`)
1.  O usuário pode salvar os dados.
2.  O sistema gera um arquivo `.txt` com o relatório estatístico.
3.  Gera também uma "foto" do mapa em texto para referência futura.
