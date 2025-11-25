"""
Gerador de labirintos usando algoritmo DFS recursivo.
Cria estruturas labirínticas conectadas para servir de base para o grafo.
"""

import random
from collections import deque


class MazeGenerator:
    """Gera labirintos usando DFS recursivo"""
    
    def __init__(self, width, height, seed=None):
        self.width = width
        self.height = height
        if seed is not None:
            random.seed(seed)
        
        # Grid inicializado com paredes (True = parede, False = caminho)
        self.grid = [[True for _ in range(width)] for _ in range(height)]
        
    def generate(self):
        """
        Gera labirinto usando algoritmo DFS recursivo
        
        Returns:
            list[list[bool]]: Grid onde True = parede, False = caminho
        """
        # Certifica que dimensões são ímpares para algoritmo funcionar
        actual_width = self.width if self.width % 2 == 1 else self.width - 1
        actual_height = self.height if self.height % 2 == 1 else self.height - 1
        
        # Reinicializa grid com dimensões corretas
        self.grid = [[True for _ in range(actual_width)] for _ in range(actual_height)]
        
        # Começa do canto superior esquerdo (posição ímpar)
        start_x, start_y = 1, 1
        self.grid[start_y][start_x] = False
        
        # DFS recursivo
        self._dfs_carve(start_x, start_y, actual_width, actual_height)
        
        # Garante que há pelo menos um caminho conectado
        self._ensure_connectivity(actual_width, actual_height)
        
        # Redimensiona para o tamanho original se necessário
        if actual_width != self.width or actual_height != self.height:
            self._resize_grid(actual_width, actual_height, self.width, self.height)
        
        return self.grid
    
    def _dfs_carve(self, x, y, width, height):
        """Algoritmo DFS recursivo para escavar caminhos"""
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]  # Norte, Leste, Sul, Oeste
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # Verifica se nova posição é válida e ainda é parede
            if (0 < nx < width - 1 and 0 < ny < height - 1 and 
                self.grid[ny][nx] == True):
                
                # Remove parede entre posição atual e nova posição
                wall_x, wall_y = x + dx // 2, y + dy // 2
                self.grid[wall_y][wall_x] = False
                self.grid[ny][nx] = False
                
                # Recursão
                self._dfs_carve(nx, ny, width, height)
    
    def _ensure_connectivity(self, width, height):
        """Garante que todo o labirinto está conectado usando flood fill"""
        # Encontra primeira célula de caminho
        start_pos = None
        for y in range(height):
            for x in range(width):
                if not self.grid[y][x]:  # Se é caminho
                    start_pos = (x, y)
                    break
            if start_pos:
                break
        
        if not start_pos:
            # Sem caminhos, cria um básico
            self.grid[1][1] = False
            return
        
        # Flood fill para marcar área conectada
        visited = [[False for _ in range(width)] for _ in range(height)]
        queue = deque([start_pos])
        visited[start_pos[1]][start_pos[0]] = True
        
        while queue:
            x, y = queue.popleft()
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                
                if (0 <= nx < width and 0 <= ny < height and
                    not visited[ny][nx] and not self.grid[ny][nx]):
                    visited[ny][nx] = True
                    queue.append((nx, ny))
        
        # Conecta áreas desconectadas criando passagens
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if not self.grid[y][x] and not visited[y][x]:
                    # Encontra caminho mais próximo e conecta
                    self._connect_to_main_area(x, y, visited, width, height)
    
    def _connect_to_main_area(self, x, y, visited, width, height):
        """Conecta área isolada à área principal"""
        # Busca direção para área conectada
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            for distance in range(1, max(width, height)):
                nx, ny = x + dx * distance, y + dy * distance
                
                if (0 <= nx < width and 0 <= ny < height and
                    not self.grid[ny][nx] and visited[ny][nx]):
                    
                    # Cria caminho até área conectada
                    for i in range(1, distance):
                        path_x = x + dx * i
                        path_y = y + dy * i
                        if 0 <= path_x < width and 0 <= path_y < height:
                            self.grid[path_y][path_x] = False
                            visited[path_y][path_x] = True
                    return
    
    def _resize_grid(self, old_width, old_height, new_width, new_height):
        """Redimensiona grid para tamanho desejado"""
        new_grid = [[True for _ in range(new_width)] for _ in range(new_height)]
        
        # Copia grid antigo
        for y in range(min(old_height, new_height)):
            for x in range(min(old_width, new_width)):
                new_grid[y][x] = self.grid[y][x]
        
        # Preenche áreas extras se necessário
        if new_width > old_width or new_height > old_height:
            self._extend_maze(new_grid, old_width, old_height, new_width, new_height)
        
        self.grid = new_grid
    
    def _extend_maze(self, grid, old_w, old_h, new_w, new_h):
        """Estende labirinto para preencher área extra"""
        # Estratégia simples: adiciona alguns caminhos extras
        if new_w > old_w:
            # Adiciona caminhos verticais na borda direita
            for y in range(1, min(new_h, old_h), 2):
                if random.random() < 0.3:
                    grid[y][old_w] = False
                    if old_w + 1 < new_w:
                        grid[y][old_w + 1] = False
        
        if new_h > old_h:
            # Adiciona caminhos horizontais na borda inferior
            for x in range(1, min(new_w, old_w), 2):
                if random.random() < 0.3:
                    grid[old_h][x] = False
                    if old_h + 1 < new_h:
                        grid[old_h + 1][x] = False
    
    def get_valid_positions(self):
        """
        Retorna lista de posições válidas (caminhos) no labirinto
        
        Returns:
            list[tuple[int, int]]: Lista de coordenadas (x, y) de caminhos
        """
        positions = []
        for y in range(self.height):
            for x in range(self.width):
                if not self.grid[y][x]:  # Se é caminho (não parede)
                    positions.append((x, y))
        return positions
    
    def is_path(self, x, y):
        """Verifica se posição é caminho válido"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return not self.grid[y][x]
        return False
    
    def print_maze(self, symbol_wall='#', symbol_path='.'):
        """Imprime labirinto para debug"""
        for row in self.grid:
            print(''.join(symbol_wall if cell else symbol_path for cell in row))


def gerar_labirinto_conectado(width, height, seed=None):
    """
    Função utilitária para gerar labirinto conectado
    
    Args:
        width (int): Largura do labirinto
        height (int): Altura do labirinto  
        seed (int): Semente para reprodução
        
    Returns:
        tuple: (grid, valid_positions) onde grid é matriz booleana e valid_positions são coordenadas de caminhos
    """
    generator = MazeGenerator(width, height, seed)
    grid = generator.generate()
    valid_positions = generator.get_valid_positions()
    
    return grid, valid_positions


# Teste básico do módulo
if __name__ == "__main__":
    print("Testando gerador de labirintos...")
    
    # Gera labirinto pequeno para teste
    generator = MazeGenerator(15, 11, seed=42)
    grid = generator.generate()
    
    print(f"Labirinto {generator.width}x{generator.height}:")
    generator.print_maze()
    
    positions = generator.get_valid_positions()
    print(f"\nPosições válidas: {len(positions)}")
    print(f"Primeiras 10: {positions[:10]}")
