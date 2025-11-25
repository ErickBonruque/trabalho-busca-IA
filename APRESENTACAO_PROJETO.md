# Apresentação do Projeto: Agentes Inteligentes e Algoritmos de Busca

---

## 1. Introdução e Objetivos

### O Desafio
Desenvolver um sistema de inteligência artificial capaz de navegar autonomamente em ambientes complexos e desconhecidos, simulando cenários reais de busca e otimização.

### Objetivos Principais
*   **Implementação de Agentes de Busca**: Criar agentes capazes de encontrar caminhos ótimos entre um ponto de partida e um objetivo.
*   **Ambientes Dinâmicos**: Gerar mundos procedurais com diferentes tipos de terrenos, custos de movimentação e obstáculos.
*   **Análise Comparativa**: Comparar o desempenho de diferentes algoritmos clássicos de IA (Não-informados vs. Informados).
*   **Coleta de Recursos**: Integrar um sistema de recompensas que influencia a tomada de decisão do agente.

---

## 2. Modelagem do Mundo (Como foi feito)

O ambiente foi construído utilizando técnicas de geração procedural para garantir variabilidade e complexidade nos testes.

### Geração de Mapas
*   **Estrutura do Labirinto**: Utilizado algoritmo **DFS Recursivo (Depth-First Search)** para criar corredores e caminhos conectados, garantindo que sempre haja solução.
*   **Biomas e Terrenos**: Aplicação de **Perlin Noise** para gerar zonas de terrenos orgânicas e realistas, simulando geografia natural.

### Sistema de Terrenos e Custos
Para tornar a busca mais realista, diferentes terrenos impõem custos variados ao movimento:

| Tipo de Terreno | Símbolo | Custo | Descrição |
|:---:|:---:|:---:|---|
| **Sólido** | `.` | **1** | Movimento padrão, baixo custo. |
| **Arenoso** | `~` | **4** | Terreno que dificulta levemente o avanço. |
| **Rochoso** | `^` | **10** | Terreno acidentado, alto custo de travessia. |
| **Pântano** | `&` | **20** | Área de custo extremo, deve ser evitada. |

### Sistema de Recompensas
O projeto implementa um sistema dinâmico de coleta de itens que enriquece a simulação:
*   **Distribuição**: Recompensas são espalhadas estrategicamente pelo mapa, tanto no caminho principal quanto em áreas secundárias.
*   **Mecanismo de Coleta**: 
    *   Quando o agente entra em um nó contendo uma recompensa (`$`), ela é automaticamente coletada.
    *   O sistema registra a coleta e marca o nó como "visitado" (`*`).
    *   Ao final da execução, o relatório contabiliza quantas recompensas foram obtidas no caminho escolhido.
*   **Influência na Busca**: Algoritmos como a Busca Gulosa foram adaptados com heurísticas agressivas para desviar do caminho ótimo se uma recompensa estiver muito próxima (raio de 3 células), incentivando a exploração.

### Representação em Grafo
O mapa visual é convertido internamente em um **Grafo Ponderado**, onde:
*   Cada célula acessível é um **Nó**.
*   Movimentos possíveis são **Arestas**.
*   O **Peso** da aresta é determinado pelo tipo de terreno de destino.

---

## 3. Algoritmos de Busca Utilizados

Foram implementados quatro algoritmos principais, divididos em duas categorias:

### A. Busca Não-Informada (Cega)

#### 1. BFS - Busca em Largura (Breadth-First Search)
*   **Funcionamento**: Explora o grafo em camadas, visitando todos os vizinhos de profundidade $d$ antes de $d+1$.
*   **Característica**: Garante encontrar o caminho com o **menor número de passos** (não necessariamente o menor custo ponderado).
*   **Uso no Projeto**: Baseline para garantia de otimalidade em grafos não ponderados.

#### 2. DFS - Busca em Profundidade (Depth-First Search)
*   **Funcionamento**: Explora um caminho até o fim antes de retroceder (backtracking).
*   **Característica**: Baixo consumo de memória, mas **não garante** caminho ótimo e pode ficar preso em caminhos longos ineficientes.
*   **Uso no Projeto**: Comparação de eficiência de memória vs. qualidade da solução.

### B. Busca Informada (Heurística)

#### 3. Busca Gulosa (Greedy Best-First Search)
*   **Funcionamento**: Escolhe sempre o nó que parece estar mais próximo do objetivo, ignorando o custo já percorrido.
*   **Característica**: Extremamente rápida, mas **sub-ótima** (frequentemente encontra caminhos não ideais).
*   **Heurística Específica**: Utiliza a **`heuristica_gulosa_agressiva`**.
    *   Baseia-se na distância Manhattan.
    *   Possui um modificador de comportamento: se detectar uma recompensa a menos de 3 passos de distância, reduz drasticamente o custo estimado, "atraindo" o agente para coletar o item antes de seguir para o objetivo.

#### 4. A* (A-Star)
*   **Funcionamento**: Combina o custo real percorrido ($g(n)$) com a estimativa até o objetivo ($h(n)$). $f(n) = g(n) + h(n)$.
*   **Característica**: O "padrão ouro" em pathfinding. Garante o caminho de **menor custo total** se a heurística for admissível.
*   **Heurística Específica**: Utiliza a **`heuristica_terreno`**.
    *   Calcula a **Distância Manhattan** ($|x_1 - x_2| + |y_1 - y_2|$) multiplicada pelo custo mínimo de terreno do mapa.
    *   Isso garante a propriedade de **admissibilidade** (nunca superestima o custo real), essencial para que o A* encontre a solução ótima matemática sem ser "enganado" por terrenos complexos.

---

## 4. Resultados e Análise Comparativa

Os testes foram realizados em ambientes de 30x20 células (600 nós), comparando métricas de eficiência.

### Resumo de Performance (Exemplo Típico)

| Algoritmo | Custo do Caminho | Nós Visitados (Memória) | Tempo (s) | Análise |
|:---|:---:|:---:|:---:|---|
| **BFS** | 197.0 | 177 | 0.003 | Ótimo em passos, mas explora demais. |
| **DFS** | 197.0 | 101 | 0.002 | Rápido e econômico, mas caminho pode ser ruim. |
| **Gulosa** | 197.0 | **89** | **0.002** | Mais rápida e visita menos nós, risco de não ser ótimo. |
| **A*** | **197.0** | 142 | 0.004 | **Equilíbrio ideal**. Garante o melhor custo com exploração direcionada. |

### Principais Descobertas

1.  **Impacto do Terreno**: Em mapas com muitos pântanos e rochas, o **BFS** degrada rapidamente pois trata todos os nós como iguais, enquanto o **A\*** contorna eficientemente as áreas de alto custo.
2.  **Eficiência vs. Otimização**: A **Busca Gulosa** provou ser a mais rápida para encontrar *qualquer* caminho, ideal para cenários onde tempo de resposta é crítico e a perfeição não é necessária.
3.  **Consistência**: O **A\*** manteve-se como a solução mais robusta, adaptando-se a terrenos complexos sem sacrificar a otimalidade do caminho, justificando seu uso extensivo em jogos e robótica.

---

## 5. Conclusão

O projeto demonstrou com sucesso a aplicação prática de algoritmos de busca em IA.

*   **Conclusão Técnica**: A implementação de custos de terreno variáveis transformou um problema simples de labirinto em um problema complexo de otimização de custos, onde algoritmos não informados (BFS/DFS) mostram suas limitações.
*   **Vencedor Geral**: O algoritmo **A\*** (A-Star) com heurística combinada ofereceu o melhor balanceamento entre custo computacional e qualidade da solução.
*   **Destaque**: A integração de geração procedural (Perlin Noise) garantiu que os agentes fossem testados em cenários imprevisíveis, validando a robustez da implementação.
