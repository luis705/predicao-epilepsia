#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modo de uso:
# ./nomeDoPrograma -e caminhoArqsJanelasEEG/

import getopt
import os
import sys

import numpy as np
from tqdm import tqdm

optlist, args = getopt.gnu_getopt(sys.argv[1:], 'e:')
for (opcao, argumento) in optlist:
    if opcao == '-e':
        caminhoArqsEEG = argumento
arqsDirs = os.listdir(caminhoArqsEEG)
for nomeArqAmostras in tqdm(arqsDirs):
    with open(os.path.join(caminhoArqsEEG, nomeArqAmostras), mode='r') as arq:
        tamanho = len(arq.readlines())
    if tamanho != 1280:
        print(
            f'Arquivo {nomeArqAmostras} inválido com apenas {tamanho} linhas'
        )
        continue
    # print(tamanho, nomeArqAmostras)
    if nomeArqAmostras.find('jan') == 0:
        nomeCompletoArqAmostras = caminhoArqsEEG + nomeArqAmostras
        amostras = np.loadtxt(nomeCompletoArqAmostras)
        amostrasT = amostras.transpose()
        A = np.fft.fft(amostrasT)
        AT = A.transpose()
        moduloFFT = abs(AT)
        # Calcular as médias das raias em cada faixa:
        faixaDelta = moduloFFT[1:16]
        mediaDelta = np.mean(faixaDelta, 0)
        faixaTheta = moduloFFT[20:36]
        mediaTheta = np.mean(faixaTheta, 0)
        faixaAlpha = moduloFFT[40:66]
        mediaAlpha = np.mean(faixaAlpha, 0)
        faixaBeta = moduloFFT[70:151]
        mediaBeta = np.mean(faixaBeta, 0)
        faixaGamma_1 = moduloFFT[150:276]
        mediaGamma_1 = np.mean(faixaGamma_1, 0)
        faixaGamma_2 = moduloFFT[325:551]
        mediaGamma_2 = np.mean(faixaGamma_2, 0)
        medias = np.array(
            [
                mediaDelta,
                mediaTheta,
                mediaAlpha,
                mediaBeta,
                mediaGamma_1,
                mediaGamma_2,
            ]
        )
        vetor = medias.reshape(1, -1)
        nomeArqVetorFFT = nomeArqAmostras.replace('jan', 'vetorFFT_')
        np.savetxt(nomeArqVetorFFT, abs(vetor))
