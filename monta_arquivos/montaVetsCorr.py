# Modo de uso:
# ./nomeDoPrograma -e caminhoArqsJanelasEEG/

import concurrent.futures
import getopt
import math
import multiprocessing
import os
import sys
from pathlib import Path
from warnings import filterwarnings

import numpy as np
import pandas as pd
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
                    correlation = np.corrcoef(l1, d2)
                    corr.append(correlation[0, 1])
                # Em seguida encontra a maior correlação, em módulo, e adiciona
                # esse valor à matriz de adjacências
                correlacoes[i, j] = np.max(np.abs(corr))
    # Torna a matriz simétrica
    correlacoes += correlacoes.T
    return np.abs(correlacoes)


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
            auto = abs(to_corr[sinal].corr(y))
            if auto <= 0.5 or math.isnan(auto):
                decorr_time.append(k)
                break
    del to_corr
    return decorr_time


def str_float(linha):
    valores = list(linha.str.split())[0]
    return pd.Series([float(a) for a in valores])


def salva_caracteristicas(caminho, arquivo):
    dados = pd.read_parquet(Path(caminho, arquivo)).to_numpy().T

    # Criação dos dataframes para salvar as característica
    corr = np.abs(correlaciona(dados, -5, 5))
    corr = np.nan_to_num(corr)

    mask = np.triu(np.ones(corr.shape), 1) == 1
    corr_vec = corr[mask]

    # Correlações
    decorr_time = tempo_decorrelacao(dados, dados)
    corr_vec = np.append(corr_vec, decorr_time)

    # Adicionando as linhas aos dfs
    corr_vec = pd.DataFrame(corr_vec)
    caminho_resultado = Path(
        'vetores', caminho.stem, 'Corr', 'vetorCorr' + arquivo[3:]
    )
    corr_vec.to_parquet(caminho_resultado)


def processa_todos(caminho):
    arquivos = os.listdir(caminho)
    pbar = tqdm(total=len(arquivos))
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=int(multiprocessing.cpu_count() / 1)
    ) as executor:
        future = [
            executor.submit(salva_caracteristicas, caminho, arquivo)
            for arquivo in arquivos
        ]
        for _ in concurrent.futures.as_completed(future):
            pbar.update(1)
    pbar.close()


def processa_sem_paralelo(caminho):
    arquivos = os.listdir(caminho)
    for arquivo in tqdm(arquivos):
        salva_caracteristicas(caminho, arquivo)


if __name__ == '__main__':
    np.seterr(all='ignore')
    filterwarnings('ignore')
    optlist, args = getopt.gnu_getopt(sys.argv[1:], 'e:')
    for (opcao, argumento) in optlist:
        if opcao == '-e':
            caminhoArqsEEG = Path(argumento)

    processa_todos(caminhoArqsEEG)
    # processa_sem_paralelo(caminhoArqsEEG)
