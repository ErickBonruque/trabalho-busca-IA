"""
Gerador de biomas usando Perlin Noise para criar distribuição natural de terrenos.
Mapeia valores contínuos para diferentes tipos de terreno.
"""

import random
import math
from enum import Enum
import config


class TipoTerreno(Enum):
    """Enumera os tipos de terreno e seus custos de deslocamento"""
    SOLIDO = (config.TERRENO_CONFIG['SOLIDO']['custo'], config.TERRENO_CONFIG['SOLIDO']['simbolo'])
    ARENOSO = (config.TERRENO_CONFIG['ARENOSO']['custo'], config.TERRENO_CONFIG['ARENOSO']['simbolo'])
    ROCHOSO = (config.TERRENO_CONFIG['ROCHOSO']['custo'], config.TERRENO_CONFIG['ROCHOSO']['simbolo'])
    PANTANO = (config.TERRENO_CONFIG['PANTANO']['custo'], config.TERRENO_CONFIG['PANTANO']['simbolo'])
    
    def __init__(self, custo, simbolo):
        self.custo = custo
        self.simbolo = simbolo


class PerlinNoise:
    """
    Implementação simplificada de Perlin Noise para geração de biomas.
    Baseada no algoritmo clássico de Ken Perlin.
    """
    
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        
        # Tabela de permutação para Perlin Noise
        self.permutation = list(range(256))
        random.shuffle(self.permutation)
        self.permutation *= 2  # Duplica para evitar overflow
        
        # Vetores de gradiente 2D
        self.gradients = [
            (1, 1), (-1, 1), (1, -1), (-1, -1),
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]
    
    def fade(self, t):
        """Função de suavização para Perlin Noise"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def lerp(self, t, a, b):
        """Interpolação linear"""
        return a + t * (b - a)
    
    def grad(self, hash_val, x, y):
        """Função de gradiente para Perlin Noise"""
        gradient = self.gradients[hash_val % len(self.gradients)]
        return gradient[0] * x + gradient[1] * y
    
    def noise(self, x, y):
        """
        Gera valor de ruído Perlin para coordenadas (x, y)
        
        Args:
            x (float): Coordenada X
            y (float): Coordenada Y
            
        Returns:
            float: Valor entre -1 e 1
        """
        # Encontra célula da grade
        X = int(x) & 255
        Y = int(y) & 255
        
        # Posições relativas dentro da célula
        x -= int(x)
        y -= int(y)
        
        # Calcula curvas de suavização
        u = self.fade(x)
        v = self.fade(y)
        
        # Hash das coordenadas dos 4 cantos da célula
        A = self.permutation[X] + Y
        AA = self.permutation[A]
        AB = self.permutation[A + 1]
        B = self.permutation[X + 1] + Y
        BA = self.permutation[B]
        BB = self.permutation[B + 1]
        
        # Interpola os resultados dos 4 cantos
        return self.lerp(v,
            self.lerp(u, self.grad(self.permutation[AA], x, y),
                         self.grad(self.permutation[BA], x - 1, y)),
            self.lerp(u, self.grad(self.permutation[AB], x, y - 1),
                         self.grad(self.permutation[BB], x - 1, y - 1)))
    
    def octave_noise(self, x, y, octaves=4, persistence=0.5, scale=0.1):
        """
        Gera ruído com múltiplas oitavas para maior realismo
        
        Args:
            x, y (float): Coordenadas
            octaves (int): Número de camadas de ruído
            persistence (float): Quão rapidamente amplitudes diminuem
            scale (float): Escala do ruído (valores menores = terreno mais suave)
            
        Returns:
            float: Valor normalizado entre 0 e 1
        """
        value = 0
        amplitude = 1
        frequency = scale
        max_value = 0
        
        for _ in range(octaves):
            value += self.noise(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2
        
        # Normaliza para [0, 1]
        return (value / max_value + 1) * 0.5


class BiomeGenerator:
    """Gera biomas naturais usando Perlin Noise"""
    
    def __init__(self, seed=None):
        self.noise_generator = PerlinNoise(seed)
        
        # Configurações dos biomas carregadas do config
        self.biome_ranges = []
        
        for min_val, max_val, nome_terreno in config.BIOMA_DISTRIBUICAO:
            if hasattr(TipoTerreno, nome_terreno):
                self.biome_ranges.append((min_val, max_val, getattr(TipoTerreno, nome_terreno)))
            else:
                # Fallback seguro caso configuração esteja errada
                print(f"AVISO: Tipo de terreno '{nome_terreno}' não encontrado. Usando SOLIDO.")
                self.biome_ranges.append((min_val, max_val, TipoTerreno.SOLIDO))
    
    def generate_biome_map(self, width, height, scale=config.BIOMA_ESCALA, octaves=config.BIOMA_OITAVAS):
        """
        Gera mapa de biomas para grid especificado
        
        Args:
            width, height (int): Dimensões do mapa
            scale (float): Escala do ruído (menor = terreno mais suave)
            octaves (int): Complexidade do terreno
            
        Returns:
            list[list[TipoTerreno]]: Matriz de tipos de terreno
        """
        biome_map = []
        
        for y in range(height):
            row = []
            for x in range(width):
                # Gera valor de ruído para posição
                noise_value = self.noise_generator.octave_noise(
                    x, y, octaves=octaves, scale=scale
                )
                
                # Mapeia valor para tipo de terreno
                terrain_type = self._map_noise_to_terrain(noise_value)
                row.append(terrain_type)
            
            biome_map.append(row)
        
        return biome_map
    
    def _map_noise_to_terrain(self, noise_value):
        """Mapeia valor de ruído para tipo de terreno"""
        for min_val, max_val, terrain_type in self.biome_ranges:
            if min_val <= noise_value < max_val:
                return terrain_type
        
        # Fallback para último tipo se valor estiver fora do range
        if self.biome_ranges:
            return self.biome_ranges[-1][2]
        return TipoTerreno.SOLIDO
    
    def generate_biome_for_position(self, x, y, scale=config.BIOMA_ESCALA, octaves=config.BIOMA_OITAVAS):
        """
        Gera bioma para posição específica
        
        Args:
            x, y (int): Coordenadas
            scale (float): Escala do ruído
            octaves (int): Complexidade
            
        Returns:
            TipoTerreno: Tipo de terreno para posição
        """
        noise_value = self.noise_generator.octave_noise(
            x, y, octaves=octaves, scale=scale
        )
        return self._map_noise_to_terrain(noise_value)
    
    def get_biome_statistics(self, biome_map):
        """
        Calcula estatísticas de distribuição dos biomas
        
        Args:
            biome_map (list[list[TipoTerreno]]): Mapa de biomas
            
        Returns:
            dict: Estatísticas de cada tipo de terreno
        """
        stats = {terrain_type: 0 for terrain_type in TipoTerreno}
        total = 0
        
        for row in biome_map:
            for terrain in row:
                stats[terrain] += 1
                total += 1
        
        # Converte para porcentagens
        percentages = {
            terrain: (count / total) * 100 if total > 0 else 0
            for terrain, count in stats.items()
        }
        
        return {
            'counts': stats,
            'percentages': percentages,
            'total': total
        }


def gerar_biomas_naturais(width, height, seed=None, scale=config.BIOMA_ESCALA, octaves=config.BIOMA_OITAVAS):
    """
    Função utilitária para gerar biomas naturais
    
    Args:
        width, height (int): Dimensões
        seed (int): Semente para reprodução
        scale (float): Suavidade do terreno (0.05 = muito suave, 0.2 = muito variado)
        octaves (int): Complexidade (mais oitavas = mais detalhes)
        
    Returns:
        tuple: (biome_map, statistics) onde biome_map é matriz de TipoTerreno
    """
    generator = BiomeGenerator(seed)
    biome_map = generator.generate_biome_map(width, height, scale, octaves)
    statistics = generator.get_biome_statistics(biome_map)
    
    return biome_map, statistics


# Teste básico do módulo
if __name__ == "__main__":
    print("Testando gerador de biomas...")
    
    # Gera mapa pequeno para teste
    biome_map, stats = gerar_biomas_naturais(20, 10, seed=42, scale=config.BIOMA_ESCALA)
    
    print(f"Mapa de biomas 20x10:")
    for row in biome_map:
        print(''.join(terrain.simbolo for terrain in row))
    
    print(f"\nEstatísticas:")
    for terrain, percentage in stats['percentages'].items():
        print(f"  {terrain.name}: {percentage:.1f}% ({stats['counts'][terrain]} células)")
