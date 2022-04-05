#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modo de uso:
# ./nomeDoPrograma -e caminhoArqsJanelasEEG/

import getopt
import os
import sys

import numpy as np
from scipy import stats
from tqdm import tqdm

optlist, args = getopt.gnu_getopt(sys.argv[1:], "e:")
for (opcao, argumento) in optlist:
    if opcao == "-e":
        caminhoArqsEEG = argumento
arqsDirs = os.listdir(caminhoArqsEEG)
for nomeArqAmostras in tqdm(arqsDirs):
    if nomeArqAmostras.find("jan") == 0:
        nomeCompletoArqAmostras = caminhoArqsEEG + nomeArqAmostras
        amostras = np.loadtxt(nomeCompletoArqAmostras)
        resultado = stats.describe(amostras)
        juntos = np.array(
            [
                resultado.mean,
                resultado.variance,
                resultado.skewness,
                resultado.kurtosis,
            ]
        )
        vetor = juntos.reshape(1, -1)
        nomeArqVetorEstatisticos = nomeArqAmostras.replace(
            "jan", "vetorEstatisticos_"
        )
        np.savetxt(nomeArqVetorEstatisticos, abs(vetor))
