import math
import os

import networkx as nx
import numpy as np
import pandas as pd
from tqdm import tqdm


def correlaciona(data, min_lag, max_lag):
    correlacoes = np.zeros((data.shape[1], data.shape[1]))
    for i, arr1 in enumerate(data):
        for j, arr2 in enumerate(data):
            if i < j:
                # Inicialmente calcula o coeficiente de correlação de pearson
                # Porém utilizando uma defasagem variando de acordo com os
                # parâmetros passados
                corr = [
                    np.corrcoef(arr1, np.roll(arr2, k))[0][1] for k in range(min_lag, max_lag + 1)
                ]
                # Em seguida encontra a maior correlação, em módulo, e adiciona
                # esse valor à matriz de adjacências
                correlacoes[i, j] = corr[np.argmax(corr)]

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
    """
    Assim como a eficiência global, a local não possuí uma implementação
    na biblioteca para grafos com pesos, portanto novamente foi feita
    uma adaptação no código utilizado pela biblioteca para a eficiência
    local em grafos sem pesos, para adicionar esse parâmetro.
    """

    eficiencia = {i: 0 for i in grafo}
    nos_vizinhos = grafo.adj.items()

    for i, vizinho in nos_vizinhos:
        vizinhos_i = set(vizinho) - {i}

        # Caso o denominador (grau * (grau -1 )) seja negativo
        # a eficiência local é nula, portanto prossegue para a
        # próxima iteração
        grau = sum(grafo[i][j]["weight"] for j in vizinhos_i)
        denom = grau * (grau - 1)
        if denom <= 0:
            continue

        triangulos = 0
        vistos = set()

        for j in vizinhos_i:
            # Evita calculos desnecessários
            vistos.add(j)
            vizinhos_j = set(grafo[j]) - vistos
            wij = grafo[i][j]["weight"]

            for h in vizinhos_i & vizinhos_j:
                # O subgrafo é criado para encontrar o tamanho do caminho
                # mais curto entre os nós j e h e que passe somente por
                # vizinhoss diretos de i.
                subgrafo = nx.ego_graph(grafo, i, radius=1, center=False)
                distancia = nx.dijkstra_path_length(subgrafo, j, h)
                distancia = (1 / distancia) if distancia >= 0 else 0
                triangulos += (wij * grafo[i][h]["weight"] * distancia) ** (1 / 3)

        # A multiplicação por 2 ocorre para não ser necessário fazer o mesmo
        # cálculo duas vezes. Realizar w_{01} * w_{02} * distancia(1,2) e
        # w_{02} * w_{01} * distancia(1, 2), porém o último não é cálculado
        eficiencia[i] += 2 * triangulos / denom

    return eficiencia


def tempo_decorrelacao(sinais, intervalo, dados):
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
            y = sinal.roll(k)
            auto = abs(np.corrcoef(sinal, y)[0][1])
            if auto <= 0.5 or math.isnan(auto):
                decorr_time.append(k)
                break
    return decorr_time


def salva_caracteristicas(paciente, caminho, arquivo):
    erros = list()

    # Caregamento do conjunto de dados
    sinais = np.loadtxt(os.path.join(caminho, arquivo))

    # Criação dos dataframes para salvar as característica
    vec_carac = np.array(shape(1, 76))
    vec_corr = pd.DataFrame(shape=(1, 153))

    # Gera o grafo e retira as caracteristicas
    try:
        corr = correlaciona(dados, -5, 5)
        corr_vec = np.triu(corr).flatten()
        corr_vec = pd.Series(np.ma.masked_equal(corr_vec, 0).compressed())

        grafo = nx.to_networkx_graph(corr, create_using=nx.Graph)
        caminhos = dict(nx.all_pairs_dijkstra_path_length(grafo))

        # Características locais
        ex = list(nx.eccentricity(grafo, sp=caminhos).values())
        centr = list(
            nx.betweenness_centrality(
                grafo, weight="weight", normalized=True
            ).values()
        )
        ef_local = list(eficiencia_local(grafo).values())
        coef = list(coeficiente_de_agrupamento(grafo).values())
        locais = [ex, centr, ef_local, coef]

        # Características globais
        caminho_carac = nx.average_shortest_path_length(grafo, weight="weight")
        ef_global = eficiencia_global(grafo, caminhos)
        raio = min(ex)
        diametro = max(ex)
        globais = [caminho_carac, ef_global, raio, diametro]

        # Correlações
        decorr_time = tempo_decorrelacao(sinais, intervalo, dados)
        corr_vec = corr_vec.append(pd.Series(decorr_time), ignore_index=True)
        vec_corr = corr_vec.to_numpy()

        # Linha para o df com todas as características
        linha_carac = pd.Series(data=globais)
        for local in locais:
            linha_carac = linha_carac.append(pd.Series(local), ignore_index=True)
        vec_carac = linha_carac.to_numpy()

    except ValueError:
        # Caso haja erros nos EEG's nesse intervalo
        erros.append(intervalo)

    df_carac.to_csv(
        os.path.join("características", paciente, "Todas", arquivo), index=False
    )
    df_distr.to_csv(
        os.path.join("características", paciente, "Distribuições", arquivo),
        index=False,
    )
    df_corr.to_csv(
        os.path.join("características", paciente, "Correlações", arquivo),
        index=False,
    )

    if erros != []:
        with open(
            os.path.join("características", paciente, "Problemas.txt"), mode="a"
        ) as f:
            f.write(f"{arquivo}:\n")
            for erro in erros:
                f.write(f"\t{erro * 5}s até {(erro + 1) * 5}s\n")
    erros = []


if __name__ == "__main__":
    pacientes = ["Paciente 01"]
    for paciente in tqdm(pacientes, desc="Pacientes"):
        for pasta in ["Todas", "Distribuições", "Correlações"]:
            if not os.path.exists(os.path.join("características", paciente, pasta)):
                os.makedirs(os.path.join("características", paciente, pasta))

        terminados = os.listdir(
            os.path.join("características", paciente, "Correlações")
        )
        arquivos = os.listdir(os.path.join("data", paciente))
        falta = [arquivo for arquivo in arquivos if arquivo not in terminados]

        for arquivo in tqdm(falta, desc="Arquivos"):
            salva_caracteristicas(paciente, os.path.join("data", paciente), arquivo)
