import getopt
import math
import os
import sys

import networkx as nx
import numpy as np
import pandas as pd
from tqdm import tqdm


def correlaciona(data, min_lag, max_lag):
    correlacoes = np.zeros((data.shape[1], data.shape[1]))
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if i < j:
                # Inicialmente calcula o coeficiente de correlação de pearson
                # Porém utilizando uma defasagem variando de acordo com os
                # parâmetros passados
                corr = [
                    np.corrcoef(data[i], np.roll(data[j], k))[0][1]
                    for k in range(min_lag, max_lag + 1)
                ]

                # Em seguida encontra a maior correlação, em módulo, e adiciona
                # esse valor à matriz de adjacências
                correlacoes[i, j] = corr[np.argmax(np.abs(corr))]

    # Torna a matriz simétrica
    correlacoes += correlacoes.T

    return np.abs(correlacoes)


def eficiencia_global(grafo, caminhos):
    """
    A biblioteca networkx já possuí uma função que calcula a eficiência
    global, porém nessa implementação os pesos do grafo não são levados
    em consideração. Dessa forma a fuexinção foi recriada, com base na original
    levando em conta os pesos das ligações dos nós.
    """

    n = len(grafo)
    denom = n * (n - 1)
    if denom == 0:
        return 0

    g_eff = 0
    for destinos in caminhos.values():
        for distancia in destinos.values():
            if distancia > 0:
                # Soma os inversos de todos os pesos do grafo
                g_eff += 1 / distancia

    return g_eff / denom


def numero_de_triangulos(grafo):
    """
    Função auxiliar para o cálculo do coeficiente de agrupamento.

    ---
    Retorna:
       generator : (nó, grau, triangulos)
            nó: string contendo o nome do nó
            grau: grau do nó (soma dos pesos dos links desse nó)
            triangulos: número de triângulos que esse nó participa
    """

    nos_vizinhos = grafo.adj.items()

    for i, vizinho in nos_vizinhos:
        vizinhos_i = set(vizinho) - {i}
        grau = sum(grafo[i][j]["weight"] for j in vizinhos_i)
        triangulos = 0
        vistos = set()

        for j in vizinhos_i:
            # Evita calculos desnecessários
            vistos.add(j)
            vizinhos_j = set(grafo[j]) - vistos
            wij = grafo[i][j]["weight"]
            triangulos += sum(
                (wij * grafo[i][h]["weight"] * grafo[j][h]["weight"])
                ** (1 / 3)
                for h in vizinhos_i & vizinhos_j
            )
        yield (i, grau, triangulos)


def coeficiente_de_agrupamento(grafo):
    """
    Uma forma de calcular a quantidade de triângulos para grafos
    com pesos é a partir da média geométrica dos pesos. Tanto Rubinov
    quanto a implementação da biblioteca utilizam essa forma. A
    diferença é que na biblioteca os pesos são normalizados antes.
    Além disso a implementação da bilioteca considera o grau de um nó
    como a quantidade de conexões dele, já Rubinov afirma que em grafos
    com pesos o grafo é a soma dos pesos de um nó, por isso a função
    foi reimplementada, para garantir que o grau seja calculado como
    enunciado por Rubinov.
    """

    td_iter = numero_de_triangulos(grafo)
    clusterc = {
        no: 0
        if grau * (grau - 1) <= 0
        else 2 * triangulos / (grau * (grau - 1))
        for no, grau, triangulos in td_iter
    }

    return clusterc


def tempo_decorrelacao(sinais, dados):
    """
    Calcula os tempos de decorrelação de cada um dos 17 canais
    o tempo de decorrelação é o tempo que a correlação de um
    sinal com ele mesmo demora para cair a menos que 0,5 dessa
    forma ele é o valor de k tal que corr(x[t], x[t+k]) <= 0,5
    """
    decorr_time = list()
    max_k = len(sinais) - 1280
    for sinal in sinais:
        for k in range(1, max_k):
            y = sinais[sinal][k : k + 1280].reset_index(drop=True)
            auto = abs(dados[sinal].corr(y))
            if auto <= 0.5 or math.isnan(auto):
                decorr_time.append(k)
                break
    return decorr_time


def salva_caracteristicas(paciente, caminho, arquivo):
    erros = list()

    # Carregando a janela
    janela = np.loadtxt(os.path.join(caminho, arquivo))

    # Calcula caracteristicas de correlações
    corr = correlaciona(janela, -5, 5)
    corr_vec_idx = np.triu_indices(corr.shape[0], k=1)
    corr_vec = corr[corr_vec_idx].flatten()
    decorr_time = tempo_decorrelacao(janela, janela)
    # Criação do grafo e variáveis auxiliares
    grafo = nx.to_networkx_graph(corr, create_using=nx.Graph)
    caminhos = dict(nx.all_pairs_dijkstra_path_length(grafo))

    # Características locais
    ex = list(nx.eccentricity(grafo, sp=caminhos))
    centr = list(
        nx.betweenness_centrality(
            grafo, weight='weight', normalized=True
        ).values()
    )
    ef_local = nx.efficiency_measures.local_efficiency(grafo)
    coef = list(coeficiente_de_agrupamento(grafo).values())
    locais = [ex, centr, ef_local, coef]

    # Características globais
    caminho_carac = nx.average_shortest_path_length(grafo, weight="weight")
    ef_global = eficiencia_global(grafo, caminhos)
    raio = min(ex)
    diametro = max(ex)
    globais = [caminho_carac, ef_global, raio, diametro]

    # Vetor de teoria de grafos
    carac = globais
    for local in locais:
        try:
            for valor in local:
                carac.append(valor)
        except TypeError:
            carac.append(local)

    # Criando listas para salvar características
    carac = np.array(carac)

    # Salvando os vetores
    pasta_base = os.path.join('características', paciente)
    nome_base = arquivo[3:]
    np.savetxt(
        os.path.join(pasta_base, 'Grafos', 'vetorGrafos' + nome_base), carac
    )
    np.savetxt(
        os.path.join(
            pasta_base, 'Correlações', 'vetor_correlações' + nome_base
        ),
        corr,
    )


if __name__ == "__main__":
    optlist, args = getopt.gnu_getopt(sys.argv, 'p:d:')
    for opcao, argumento in optlist:
        if opcao == '-d':
            diretorio = argumento
        elif opcao == '-p':
            paciente = argumento
    for pasta in ["Grafos", "Correlações"]:
        if not os.path.exists(
            os.path.join("características", paciente, pasta)
        ):
            os.makedirs(os.path.join("características", paciente, pasta))

        os.path.join("características", paciente, "Correlações")
    arquivos = os.listdir(diretorio)

    for arquivo in tqdm(arquivos, desc="Arquivos"):

        salva_caracteristicas(paciente, diretorio, arquivo)
