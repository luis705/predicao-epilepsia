#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modo de uso:
# ./nomeDoPrograma -e caminhoArqsJanelasEEG/

import getopt
import numpy as np
import os
import sys
from scipy import stats

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
        resultado = stats.describe( amostras )
        juntos = np.array( [ resultado.mean, resultado.variance, resultado.skewness, resultado.kurtosis ] )
        vetor = juntos.reshape( 1, -1 )
        nomeArqVetorEstatisticos = nomeArqAmostras.replace( 'jan', 'vetorEstatisticos_' )
        np.savetxt( nomeArqVetorEstatisticos, abs( vetor ) )
