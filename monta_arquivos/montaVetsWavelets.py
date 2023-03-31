#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modo de uso:
# ./nomeDoPrograma -e caminhoArqsJanelasEEG/

import getopt
import os
import sys
import concurrent.futures
import multiprocessing

import numpy as np
import pywt
import pandas as pd
from tqdm import tqdm

def str_float(linha):
    valores = list(linha.str.split())[0]
    return pd.Series([float(a) for a in valores])



def um_arq(nomeArqAmostras, caminhoArqsEEG):
    if nomeArqAmostras.find("jan") == 0:
        nomeCompletoArqAmostras = caminhoArqsEEG + nomeArqAmostras
        try:
            amostras = pd.read_parquet(nomeCompletoArqAmostras)
            amostras = amostras.apply(str_float, axis=1).to_numpy()
        except Exception as e:
            print(e)
            return
        amostrasT = amostras.transpose()
        forma = amostrasT.shape
        numCanais = forma[0]
        ltMedias = []
        for indCanal in range(numCanais):
            coefs = pywt.wavedec(amostrasT[indCanal], "db4", "periodization")
            nivel = 0
            for c in coefs:
                if nivel > 0:
                    modulo = abs(c)
                    media = np.mean(modulo)
                    ltMedias.append(media)
                nivel += 1
        vtTmp = np.array(ltMedias)
        vetor = vtTmp.reshape(1, -1)
        nomeArqVetores = nomeArqAmostras.replace("jan", "vetorWavelets_")
        df = pd.DataFrame(abs(vetor.T))
        df.rename(columns={0: '0'}, inplace=True)
        df.to_parquet(nomeArqVetores)


def processa_todos(caminho):
    arquivos = os.listdir(caminho)
    pbar = tqdm(total=len(arquivos))
    with concurrent.futures.ProcessPoolExecutor(max_workers=int(multiprocessing.cpu_count() / 1)) as executor:
        future = [executor.submit(um_arq, arquivo, caminhoArqsEEG) for arquivo in arquivos]
        for _ in concurrent.futures.as_completed(future):
            pbar.update(1)
    pbar.close()

    #for arquivo in tqdm(arquivos):
    #    um_arq(arquivo)

if __name__ == '__main__':
    optlist, args = getopt.gnu_getopt(sys.argv[1:], "e:")
    for (opcao, argumento) in optlist:
        if opcao == "-e":
            caminhoArqsEEG = argumento
    processa_todos(caminhoArqsEEG)