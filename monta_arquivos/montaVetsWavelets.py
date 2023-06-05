#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modo de uso:
# ./nomeDoPrograma -e caminhoArqsJanelasEEG/

import concurrent.futures
import getopt
import multiprocessing
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pywt
from tqdm import tqdm


def um_arq(nomeArqAmostras, caminhoArqsEEG):
    if nomeArqAmostras.find('jan') == 0:
        nomeCompletoArqAmostras = Path(caminhoArqsEEG) / nomeArqAmostras
        amostras = pd.read_parquet(nomeCompletoArqAmostras).to_numpy().T
        amostrasT = amostras.transpose()
        forma = amostrasT.shape
        numCanais = forma[0]
        ltMedias = []
        for indCanal in range(numCanais):
            coefs = pywt.wavedec(amostrasT[indCanal], 'db4', 'periodization')
            nivel = 0
            for c in coefs:
                if nivel > 0:
                    modulo = abs(c)
                    media = np.mean(modulo)
                    ltMedias.append(media)
                nivel += 1
        vtTmp = np.array(ltMedias)
        vetor = vtTmp.reshape(1, -1)
        nomeArqVetores = nomeArqAmostras.replace('jan', 'vetorWavelets_')
        df = pd.DataFrame(abs(vetor.T))
        if df.shape != (1280, 1):
            return
        df.rename(columns={0: '0'}, inplace=True)
        caminho_resultado = (
            Path('vetores')
            / Path(caminhoArqsEEG).stem
            / 'Wavelets'
            / nomeArqVetores
        )
        df.to_parquet(caminho_resultado)


def processa_todos(caminho):
    arquivos = os.listdir(caminho)
    pbar = tqdm(total=len(arquivos))
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=int(multiprocessing.cpu_count() / 1)
    ) as executor:
        future = [
            executor.submit(um_arq, arquivo, caminhoArqsEEG)
            for arquivo in arquivos
        ]
        for _ in concurrent.futures.as_completed(future):
            pbar.update(1)
    pbar.close()


def processa_todos_sem_paralelo(caminho):
    arquivos = os.listdir(caminho)
    for arquivo in tqdm(arquivos):
        um_arq(arquivo, caminhoArqsEEG)


if __name__ == '__main__':
    optlist, args = getopt.gnu_getopt(sys.argv[1:], 'e:')
    for (opcao, argumento) in optlist:
        if opcao == '-e':
            caminhoArqsEEG = argumento
    processa_todos(caminhoArqsEEG)
    # processa_todos_sem_paralelo(caminhoArqsEEG)
