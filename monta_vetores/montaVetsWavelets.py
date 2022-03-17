#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modo de uso:
# ./nomeDoPrograma -e caminhoArqsJanelasEEG/

import getopt
import numpy as np
import os
import pywt
import sys

optlist, args = getopt.gnu_getopt( sys.argv[1:], 'e:' )
for ( opcao, argumento ) in optlist:
    if opcao == '-e':
        caminhoArqsEEG = argumento
arqsDirs = os.listdir( caminhoArqsEEG )
print( '\narquivos com nomes iniciados em jan:\n' )
for nomeArqAmostras in arqsDirs:
    if nomeArqAmostras.find( 'jan' ) == 0:
        print( nomeArqAmostras )
        nomeCompletoArqAmostras = caminhoArqsEEG + nomeArqAmostras
        amostras = np.loadtxt( nomeCompletoArqAmostras )
        amostrasT = amostras.transpose()
        forma = amostrasT.shape
        numCanais = forma[ 0 ]
        ltMedias = []
        for indCanal in range( numCanais ):
            coefs = pywt.wavedec( amostrasT[ indCanal ], 'db4',
                                  'periodization' )
            nivel = 0
            for c in coefs:
                if nivel > 0:
                    modulo = abs( c )
                    media = np.mean( modulo )
                    ltMedias.append( media )
                nivel += 1
        vtTmp = np.array( ltMedias )
        vetor = vtTmp.reshape( 1, -1 )
        nomeArqVetores = nomeArqAmostras.replace( 'jan', 'vetorWavelets_' )
        np.savetxt( nomeArqVetores, abs( vetor ) )
