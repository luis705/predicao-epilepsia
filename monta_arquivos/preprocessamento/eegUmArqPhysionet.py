#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

class EEGumArqPhysionet:
    def __init__( self, nomeArqPhysionet ):
        self.nomeArqPhysionet = nomeArqPhysionet
        eeg = pd.read_csv( nomeArqPhysionet )
        eegCanaisSelec = eeg[ [ '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                                '11', '12', '13', '14', '15', '16', '17', '18' ] ]
        # No formato de numpy:
        self.npEEG_canaisSelec = eegCanaisSelec.values
    def gravaArqJanela( self, nomeArqSaida, linhaInic, numLinhas ):
        print( 'Em gravaArqJanela, nomeArqSaida =', nomeArqSaida )
        print( '  do arquivo', self.nomeArqPhysionet )
        print( '  linhaInic =', linhaInic, ', numLinhas =', numLinhas )
        linhaFinal = linhaInic + numLinhas
        np.savetxt( nomeArqSaida, self.npEEG_canaisSelec[ linhaInic:linhaFinal ] )
