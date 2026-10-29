"""
Modelo de Disseminação Cultural de Robert Axelrod (1997)
The Dissemination of Culture: A Model with Local Convergence and Global Polarization

Características modeladas (F = 5):
  1. Sexo: Masculino, Feminino, Outro
  2. Período: 1º ao 10º período
  3. Curso: Ciência da Computação, Engenharia Civil, Direito, Medicina, etc.
  4. Religião: Católica, Evangélica, Espírita, Umbanda/Candomblé, Outra, Sem religião
  5. Origem: Palmas, Gurupi, Araguaína, Porto Nacional, Outro município, Outro estado

Dinâmica:
  1. Sorteia aleatoriamente um sítio ativo s e um vizinho n.
  2. Com probabilidade = similaridade cultural (fração de características iguais),
     ocorre interação: sorteia-se uma característica em que diferem e s adota o traço de n.
  3. O sistema estabiliza quando todos os pares vizinhos possuem similaridade 0 (incompatíveis)
     ou 1 (idênticos).
"""

import random
from collections import deque
import numpy as np
import matplotlib.pyplot as plt


# Definição das 5 características e seus possíveis traços
CARACTERISTICAS = {
    "sexo": [
        "Masculino", 
        "Feminino", 
        "Outro"
    ],
    "periodo": [
        f"{i}º período" for i in range(1, 11)
    ],
    "curso": [
        "Ciência da Computação",
        "Sistemas de Informação",
        "Engenharia Civil",
        "Engenharia Elétrica",
        "Direito",
        "Medicina",
        "Administração",
        "Agronomia",
        "Pedagogia"
    ],
    "religiao": [
        "Católica",
        "Evangélica",
        "Espírita",
        "Matriz Africana (Umbanda/Candomblé)",
        "Outra",
        "Sem religião / Ateu"
    ],
    "origem": [
        "Palmas",
        "Gurupi",
        "Araguaína",
        "Porto Nacional",
        "Outro município do interior",
        "Outro estado"
    ],
}


class ModeloAxelrod:
    def __init__(self, tamanho=10, caracteristicas=CARACTERISTICAS, vizinhanca=4, seed=None):
        """
        Parâmetros:
          - tamanho: Dimensão L da grade (L x L sítios).
          - caracteristicas: Dicionário de características e traços.
          - vizinhanca: 4 (Von Neumann), 8 (Moore) ou 12 (Moore estendida).
          - seed: Semente pseudoaleatória para reprodutibilidade.
        """
        self.L = tamanho
        self.nomes_caracteristicas = list(caracteristicas.keys())
        self.tracos_por_caracteristica = [caracteristicas[n] for n in self.nomes_caracteristicas]
        self.F = len(self.nomes_caracteristicas)
        self.offsets = self._obter_offsets(vizinhanca)
        self.rng = random.Random(seed)

        # Grade (L x L x F): guarda o índice numérico do traço de cada indivíduo
        self.grade = np.array([
            [
                [self.rng.randrange(len(tracos)) for tracos in self.tracos_por_caracteristica]
                for _ in range(self.L)
            ]
            for _ in range(self.L)
        ], dtype=int)

        self.eventos = 0

    @staticmethod
    def _obter_offsets(tipo_vizinhanca):
        base_4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        diag_4 = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        longe_4 = [(-2, 0), (2, 0), (0, -2), (0, 2)]

        if tipo_vizinhanca == 4:
            return base_4
        elif tipo_vizinhanca == 8:
            return base_4 + diag_4
        elif tipo_vizinhanca == 12:
            return base_4 + diag_4 + longe_4
        else:
            raise ValueError("Vizinhança suportada: 4, 8 ou 12.")

    def obter_vizinhos(self, x, y):
        """Retorna lista de coordenadas válidas dos vizinhos na grade (sem wrap-around)."""
        return [
            (x + dx, y + dy)
            for dx, dy in self.offsets
            if 0 <= x + dx < self.L and 0 <= y + dy < self.L
        ]

    def calcular_similaridade(self, pos_a, pos_b):
        """Fração de características idênticas entre dois sítios (0.0 a 1.0)."""
        iguais = np.sum(self.grade[pos_a] == self.grade[pos_b])
        return float(iguais / self.F)

    def passo(self):
        """
        Executa 1 evento elementar da dinâmica de Axelrod:
          - Sorteia sítio ativo e vizinho.
          - Interage proporcionalmente à similaridade cultural.
          - Se interagir, copia um traço divergente do vizinho.
        Retorna True se houve mudança na cultura do sítio ativo.
        """
        self.eventos += 1
        x = self.rng.randrange(self.L)
        y = self.rng.randrange(self.L)
        
        vizinhos = self.obter_vizinhos(x, y)
        nx, ny = self.rng.choice(vizinhos)

        sim = self.calcular_similaridade((x, y), (nx, ny))
        
        # Interação ocorre com probabilidade igual à similaridade
        if self.rng.random() < sim:
            tracos_ativos = self.grade[x, y]
            tracos_vizinho = self.grade[nx, ny]
            
            diferentes = np.flatnonzero(tracos_ativos != tracos_vizinho)
            if len(diferentes) > 0:
                feat_escolhida = self.rng.choice(list(diferentes))
                tracos_ativos[feat_escolhida] = tracos_vizinho[feat_escolhida]
                return True

        return False

    def esta_estavel(self):
        """
        Verifica se o sistema atingiu o estado absorvente (convergência estável).
        Não há mais transições possíveis quando todos os pares vizinhos
        possuem similaridade = 0 ou similaridade = 1.
        """
        for x in range(self.L):
            for y in range(self.L):
                for nx, ny in self.obter_vizinhos(x, y):
                    sim = self.calcular_similaridade((x, y), (nx, ny))
                    if 0 < sim < 1:
                        return False
        return True

    def _contar_componentes(self, condicao_conexao):
        """BFS para contar grupos contíguos de sítios baseados em uma condição."""
        visitado = np.zeros((self.L, self.L), dtype=bool)
        total = 0

        for i in range(self.L):
            for j in range(self.L):
                if visitado[i, j]:
                    continue
                total += 1
                fila = deque([(i, j)])
                visitado[i, j] = True

                while fila:
                    px, py = fila.popleft()
                    for qx, qy in self.obter_vizinhos(px, py):
                        if not visitado[qx, qy] and condicao_conexao((px, py), (qx, qy)):
                            visitado[qx, qy] = True
                            fila.append((qx, qy))
        return total

    def num_regioes(self):
        """Região Cultural: conjunto de sítios contíguos com cultura 100% idêntica."""
        return self._contar_componentes(lambda a, b: self.calcular_similaridade(a, b) == 1.0)

    def num_zonas(self):
        """Zona Cultural: conjunto contíguo de sítios com similaridade > 0 (podem interagir)."""
        return self._contar_componentes(lambda a, b: self.calcular_similaridade(a, b) > 0.0)

    def executar(self, max_eventos=2_000_000, intervalo_checagem=None):
        """Roda a simulação até a estabilidade ou até atingir max_eventos."""
        if intervalo_checagem is None:
            intervalo_checagem = self.L * self.L * 10

        while self.eventos < max_eventos:
            self.passo()
            if self.eventos % intervalo_checagem == 0:
                if self.esta_estavel():
                    break

        return self.esta_estavel()

    def descrever_sitio(self, x, y):
        """Retorna os valores textuais legíveis do indivíduo na posição (x, y)."""
        indices = self.grade[x, y]
        return {
            nome: tracos[idx]
            for nome, tracos, idx in zip(self.nomes_caracteristicas, self.tracos_por_caracteristica, indices)
        }

    def gerar_mapa_regioes(self):
        """Gera uma matriz 2D onde cada cultura única recebe um identificador numérico inteiro."""
        tabela_ids = {}
        mapa = np.zeros((self.L, self.L), dtype=int)
        for i in range(self.L):
            for j in range(self.L):
                cultura = tuple(self.grade[i, j])
                if cultura not in tabela_ids:
                    tabela_ids[cultura] = len(tabela_ids)
                mapa[i, j] = tabela_ids[cultura]
        return mapa


def exibir_resumo_simulacao(modelo_inicial, modelo_final):
    """Gera visualização comparativa do estado inicial e final da cultura."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    # Estado Inicial
    mapa_ini = modelo_inicial.gerar_mapa_regioes()
    im1 = axes[0].imshow(mapa_ini, cmap="nipy_spectral", interpolation="nearest")
    axes[0].set_title(f"Estado Inicial\n{modelo_inicial.num_regioes()} Regiões | {modelo_inicial.num_zonas()} Zonas", fontsize=11)
    axes[0].set_xticks([])
    axes[0].set_yticks([])

    # Estado Final
    mapa_fim = modelo_final.gerar_mapa_regioes()
    im2 = axes[1].imshow(mapa_fim, cmap="nipy_spectral", interpolation="nearest")
    axes[1].set_title(f"Estado Final (Estável)\n{modelo_final.num_regioes()} Regiões Estáveis | {modelo_final.eventos:,} Eventos", fontsize=11)
    axes[1].set_xticks([])
    axes[1].set_yticks([])

    plt.suptitle("Disseminação Cultural (Axelrod, 1997) - Convergência e Polarização", fontsize=13, weight="bold")
    plt.tight_layout()
    plt.savefig("resultado_disseminacao_cultural.png", dpi=300, bbox_inches="tight")
    print("Gráfico salvo como: resultado_disseminacao_cultural.png")
    plt.show()


if __name__ == "__main__":
    import copy

    print("=" * 65)
    print("SIMULAÇÃO DE DISSEMINAÇÃO CULTURAL (MODELO DE AXELROD)")
    print("Características: Sexo, Período, Curso, Religião e Origem")
    print("=" * 65)

    # Inicializa modelo 10x10 com 4 vizinhos (Von Neumann)
    modelo = ModeloAxelrod(tamanho=10, vizinhanca=4, seed=42)
    modelo_inicial = copy.deepcopy(modelo)

    print(f"\n[INÍCIO]")
    print(f"Dimensão da grade: {modelo.L}x{modelo.L} ({modelo.L * modelo.L} indivíduos)")
    print(f"Número de regiões culturais no início: {modelo.num_regioes()}")
    print(f"Número de zonas culturais no início:    {modelo.num_zonas()}")
    print("\nExemplo de indivíduo no sítio (0, 0):")
    for chave, valor in modelo.descrever_sitio(0, 0).items():
        print(f"  - {chave.capitalize()}: {valor}")

    print("\nExecutando dinâmica de convergência local...")
    estavel = modelo.executar(max_eventos=2_000_000)

    print(f"\n[FINAL]")
    print(f"Status: {'Estabilidade alcançada (Equilíbrio)' if estavel else 'Limite de eventos atingido'}")
    print(f"Total de eventos simulados: {modelo.eventos:,}")
    print(f"Número de regiões estáveis finais: {modelo.num_regioes()}")
    print(f"Número de zonas culturais finais:  {modelo.num_zonas()}")

    print("\nExemplo de indivíduo no sítio (0, 0) no final:")
    for chave, valor in modelo.descrever_sitio(0, 0).items():
        print(f"  - {chave.capitalize()}: {valor}")

    exibir_resumo_simulacao(modelo_inicial, modelo)
