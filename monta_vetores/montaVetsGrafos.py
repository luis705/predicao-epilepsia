#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modo de uso:
# ./nomeDoPrograma -e caminhoArqsJanelasEEG/

import getopt
import math
import os
import sys

import networkx as nx
import numpy as np
from tqdm import tqdm


def correlaciona(data, min_lag, max_lag):
    correlacoes = np.zeros((data.shape[0], data.shape[0]))
    for i, l1 in enumerate(data):
        for j, l2 in enumerate(data):
            if i < j:
                # Inicialmente calcula o coeficiente de correlação de pearson
                # Porém utilizando uma defasagem variando de acordo com os
                # parâmetros passados
                corr = []
                for lag in range(min_lag, max_lag + 1):
                    d2 = np.roll(l2, lag)
                    corr.append(np.corrcoef(l1, d2)[0, 1])
                # Em seguida encontra a maior correlação, em módulo, e adiciona
                # esse valor à matriz de adjacências
                correlacoes[i, j] = np.max(np.abs(corr))

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
                (wij * grafo[i][h]["weight"] * grafo[j][h]["weight"]) ** (1 / 3)
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
        no: 0 if grau * (grau - 1) <= 0 else 2 * triangulos / (grau * (grau - 1))
        for no, grau, triangulos in td_iter
    }

    return clusterc


def eficiencia_local(grafo):
    return nx.local_efficiency(grafo)


def tempo_decorrelacao(sinais, dados):
    """
    Calcula os tempos de decorrelação de cada um dos 17 canais
    o tempo de decorrelação é o tempo que a correlação de um
    sinal com ele mesmo demora para cair a menos que 0,5 dessa
    forma ele é o valor de k tal que corr(x[t], x[t+k]) <= 0,5
    """
    decorr_time = list()
    max_k = len(sinais) - 1280
    to_corr = dados
    for sinal in sinais.T:
        for k in range(1, max_k):
            y = sinais[sinal][k:]
            auto = np.abs(np.corrcoef(to_corr[sinal], y))
            auto = abs(to_corr[sinal].corr(y))
            if auto <= 0.5 or math.isnan(auto):
                decorr_time.append(k)
                break
    del to_corr
    return decorr_time


def salva_caracteristicas(caminho):
    for arquivo in tqdm(os.listdir(caminho)):
        try:
            # Caregamento do conjunto de dados
            try:
                dados = np.loadtxt(os.path.join(caminho, arquivo)).T
            except:
                continue
            # Criação dos dataframes para salvar as característica
            corr_vec = []

            # Gera o grafo e retira as caracteristicas
            corr = np.abs(correlaciona(dados, -5, 5))
            corr = np.nan_to_num(corr)
            corr_vec = np.triu(corr).flatten()
            if np.any(corr_vec < 0):
                print(corr_vec)

            grafo = nx.to_networkx_graph(corr, create_using=nx.Graph)

            caminhos = dict(nx.all_pairs_dijkstra_path_length(grafo))
            # Características locais
            try:
                ex = list(nx.eccentricity(grafo, sp=caminhos).values())
            except nx.NetworkXException:
                ex = [0 for _, _ in enumerate(corr)]
            centr = list(
                nx.betweenness_centrality(
                    grafo, weight="weight", normalized=True
                ).values()
            )
            ef_local = [eficiencia_local(grafo)]
            coef = list(coeficiente_de_agrupamento(grafo).values())
            locais = [ex, centr, ef_local, coef]
            # Características globais
            try:
                caminho_carac = nx.average_shortest_path_length(grafo, weight="weight")
            except nx.NetworkXException:
                caminho_carac = 0
            ef_global = eficiencia_global(grafo, caminhos)
            raio = min(ex)
            diametro = max(ex)
            globais = [caminho_carac, ef_global, raio, diametro]

            # Correlações
            decorr_time = tempo_decorrelacao(dados, dados)
            corr_vec = np.append(corr_vec, decorr_time)

            # Vetor de características de Teoria de Grafos
            linha_carac = globais
            for local in locais:
                linha_carac = np.append(linha_carac, local)

            # Adicionando as linhas aos dfs
            np.savetxt(f"grafos{arquivo[3:]}", linha_carac.T)
            np.savetxt(f"corr{arquivo[3:]}", corr_vec.T)
        except ValueError as e:
            print(e)
            continue


if __name__ == "__main__":
    optlist, args = getopt.gnu_getopt(sys.argv[1:], "e:")
    for (opcao, argumento) in optlist:
        if opcao == "-e":
            caminhoArqsEEG = argumento
    salva_caracteristicas(caminhoArqsEEG)
