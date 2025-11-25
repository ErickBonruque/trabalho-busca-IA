"""
Arquivo de configuração centralizado do projeto.
Contém configurações de mapa, geração de biomas, simulação e interface.
"""

# Configurações Gerais
# Seed global para reprodução de resultados (None = aleatório)
SEED = None

# Configurações do Mapa e Ambiente
MAPA_LARGURA = 75   
MAPA_ALTURA = 75
MAPA_TAMANHO_MIN = 1000  # Tamanho mínimo de nós acessíveis para validar geração

# Configurações de Terreno (Custos e Símbolos)
# Utilizado para definir as propriedades de cada tipo de terreno
TERRENO_CONFIG = {
    'SOLIDO': {'custo': 1, 'simbolo': '.'},
    'ARENOSO': {'custo': 4, 'simbolo': '~'},
    'ROCHOSO': {'custo': 10, 'simbolo': '^'},
    'PANTANO': {'custo': 20, 'simbolo': '&'}
}

# Configurações de Geração de Biomas
BIOMA_ESCALA = 0.1    # Suavidade do terreno (0.05 = muito suave, 0.2 = muito variado)
BIOMA_OITAVAS = 4     # Complexidade do terreno (mais oitavas = mais detalhes)

# Distribuição dos Biomas (Intervalos de ruído Perlin [0.0 - 1.0])
# Formato: (limite_inferior, limite_superior, nome_chave_terreno)
BIOMA_DISTRIBUICAO = [
    (0.0, 0.4, 'SOLIDO'),   # 40% - Terreno sólido
    (0.4, 0.6, 'ARENOSO'),  # 20% - Terreno arenoso
    (0.6, 0.8, 'ROCHOSO'),  # 20% - Terreno rochoso
    (0.8, 1.0, 'PANTANO')   # 20% - Pântano
]

# Configurações de Simulação
SIMULACAO_VELOCIDADE_PADRAO = 1.0  # Segundos por passo na visualização

# Configurações de Resultados e Relatórios
DIR_RESULTADOS = "resultados"
ARQUIVO_RELATORIO_PADRAO = "relatorio_busca.txt"
ARQUIVO_DEMO_RELATORIO = "demo_relatorio.txt"
ARQUIVO_DEMO_MAPA = "mapa_atual.txt"
