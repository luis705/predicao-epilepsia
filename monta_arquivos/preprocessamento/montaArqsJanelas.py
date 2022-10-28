#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import leSummary
import eegUmArqPhysionet
import math
from os import listdir
from os.path import isfile, join
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

class Packing:
    def __init__( self, objeto_Tk ):
        self.numAmostrasPorSegundo = 256
        objeto_Tk.title( "Monta arquivos com janelas de amostras de EEG segundo Tsiouris et al.." )

        self.frNomeArqSumario = Frame( objeto_Tk )
        self.frNomeArqSumario.pack()
        self.txtVarNomeArqSumario = StringVar()
        self.txtVarNomeArqSumario.set( 'arq. com sumário do paciente:' )
        self.lbNomeArqSumario = Label( self.frNomeArqSumario,
                                       textvariable = self.txtVarNomeArqSumario,
                                       fg = 'darkblue',
                                       height = 3 ).pack( side = LEFT )
        self.entryNomeArqSumario = Entry( self.frNomeArqSumario, width = 80 )
        self.entryNomeArqSumario.insert( END,
                                         '/home/luis/git/predicao-epilepsia/physionet.org/files/chbmit/1.0.0/' )
        self.entryNomeArqSumario.pack( side = LEFT )
        self.btNomeArqSumario = Button( self.frNomeArqSumario, text = 'procura',
                                        command = self.prssBtNomeArqSumario )
        self.btNomeArqSumario.pack( side = LEFT )

        self.frParams = Frame( objeto_Tk )
        self.frParams.pack()
        self.txtVarDuracaoPreIctal = StringVar()
        self.txtVarDuracaoPreIctal.set( 'duração do pré-ictal (minutos):' )
        self.lbDuracaoPreIctal = Label( self.frParams,
                                        textvariable = self.txtVarDuracaoPreIctal,
                                        fg = 'darkblue',
                                        height = 3 ).pack( side = LEFT )
        self.entryDuracaoPreIctal = Entry( self.frParams, width = 3 )
        self.entryDuracaoPreIctal.insert( END, '45' )
        self.entryDuracaoPreIctal.pack( side = LEFT )

        self.txtVarDuracaoPosIctal = StringVar()
        self.txtVarDuracaoPosIctal.set( 'duração do pós-ictal (minutos):' )
        self.lbDuracaoPosIctal = Label( self.frParams,
                                        textvariable = self.txtVarDuracaoPosIctal,
                                        fg = 'darkblue',
                                        height = 3 ).pack( side = LEFT )
        self.entryDuracaoPosIctal = Entry( self.frParams, width = 3 )
        self.entryDuracaoPosIctal.insert( END, '10' )
        self.entryDuracaoPosIctal.pack( side = LEFT )

        self.txtVarDuracaoJanela = StringVar()
        self.txtVarDuracaoJanela.set( 'duração de cada janela de EEG (segundos):' )
        self.lbDuracaoJanela = Label( self.frParams,
                                      textvariable = self.txtVarDuracaoJanela,
                                      fg = 'darkblue',
                                      height = 3 ).pack( side = LEFT )
        self.entryDuracaoJanela = Entry( self.frParams, width = 3 )
        self.entryDuracaoJanela.insert( END, '5' )
        self.entryDuracaoJanela.pack( side = LEFT )

        self.frLocArqEEG = Frame( objeto_Tk )
        self.frLocArqEEG.pack()
        self.lbLocArqEEG = Label( self.frLocArqEEG,
                                  text = 'arquivos com EEG estão em:',
                                  fg = 'darkblue',
                                  height = 3 ).pack( side = LEFT )
        self.entryLocArqEEG = Entry( self.frLocArqEEG, width = 80 )
        self.entryLocArqEEG.insert( END, '/home/luis/git/predicao-epilepsia/sinais/' )
        self.entryLocArqEEG.pack( side = LEFT )
        self.btLocArqEEG = Button( self.frLocArqEEG, text = 'procura',
                                   command = self.prssBtLocArqEEG )
        self.btLocArqEEG.pack( side = LEFT )

        self.frLocJanEEG = Frame( objeto_Tk )
        self.frLocJanEEG.pack()
        self.lbLocJanEEG = Label( self.frLocJanEEG,
                                  text = 'arquivos com janelas de EEG serão colocados em:',
                                  fg = 'darkblue',
                                  height = 3 ).pack( side = LEFT )
        self.entryLocJanEEG = Entry( self.frLocJanEEG, width = 80 )
        self.entryLocJanEEG.insert( END, '/home/luis/git/predicao-epilepsia/janelas/novo/' )
        self.entryLocJanEEG.pack( side = LEFT )
        self.btLocJanEEG = Button( self.frLocJanEEG, text = 'procura',
                                   command = self.prssBtLocJanEEG )
        self.btLocJanEEG.pack( side = LEFT )

        self.frLerSumario = Frame( objeto_Tk )
        self.frLerSumario.pack()
        self.btLerSumario = Button( self.frLerSumario, text = 'ler sumário',
                                    command = self.prssBtLerSumario )
        self.btLerSumario.pack( side = LEFT )

        self.frNumCrisesDoPaciente = Frame( objeto_Tk )
        self.txtVarNumCrises = StringVar()
        self.lbNumCrisesDoPaciente = Label( self.frNumCrisesDoPaciente,
                                            textvariable = self.txtVarNumCrises,
                                            fg = 'darkblue',
                                            height = 4 )

        self.frLtsCrises = Frame( objeto_Tk )
        self.frLtCrisesTreino = Frame( self.frLtsCrises )
        self.frLtCrisesTeste = Frame( self.frLtsCrises )

        self.txtVarCrisesTreino = StringVar()
        self.txtVarCrisesTreino.set( 'crises p/ treino' )
        self.lbCrisesTreino = Label( self.frLtCrisesTreino,
                                     textvariable = self.txtVarCrisesTreino,
                                     fg = 'darkblue',
                                     height = 4 )
        self.lBxLtCrisesTreino = Listbox( self.frLtCrisesTreino,
                                          selectmode = MULTIPLE,
                                          state = DISABLED )

        self.btEscolherCrisesTreino = Button( self.frLtCrisesTreino,
                                              text = 'escolher crises',
                                              state = DISABLED,
                                              command = self.prssBtEscolherCrisesTreino )

        self.txtVarCrisesTeste = StringVar()
        self.txtVarCrisesTeste.set( 'crises p/ teste' )
        self.lbCrisesTeste = Label( self.frLtCrisesTeste,
                                    textvariable = self.txtVarCrisesTeste,
                                    fg = 'red',
                                    height = 4 )
        self.lBxLtCrisesTeste = Listbox( self.frLtCrisesTeste,
                                         selectmode = MULTIPLE,
                                         state = DISABLED )

        self.btEscolherCrisesTeste = Button( self.frLtCrisesTeste,
                                             text = 'escolher crises',
                                             state = DISABLED,
                                             command = self.prssBtEscolherCrisesTeste )

        self.frBtEscolhaCrisesConcluida = Frame( objeto_Tk )
        self.btEscolhaCrisesConcluida = Button( self.frBtEscolhaCrisesConcluida,
                                                text = 'escolha concluída',
                                                command = self.prssBtEscolhaCrisesConcluida )

        strAux = 'proporção p/ treino (%)\n' + \
                 'calculada em relação a cada classe'
        self.lbEscolherPropTreino = Label( self.frLtCrisesTreino,
                                           text =  strAux )
        self.intVarEscolherPropTreino = IntVar()
        self.scEscolherPropTreino = Scale( self.frLtCrisesTreino,
                                           orient = HORIZONTAL,
                                           variable = self.intVarEscolherPropTreino )

        strAux = 'proporção p/ teste (%)\n' + \
                 'calculada em relação a cada classe'
        self.lbEscolherPropTeste = Label( self.frLtCrisesTeste,
                                           text =  strAux )
        self.intVarEscolherPropTeste = IntVar()
        self.scEscolherPropTeste = Scale( self.frLtCrisesTeste,
                                          orient = HORIZONTAL,
                                          variable = self.intVarEscolherPropTeste )

        self.btEscolhaPropTreinoTesteConcluida = Button( self.frLtsCrises,
                                                         text = 'escolhas concluídas',
                                                         command = self.prssBtEscolhaPropTreinoTesteConcluida )

        self.frBtSai = Frame( objeto_Tk )
        self.frBtSai.pack( side = BOTTOM )
        self.btSai = Button( self.frBtSai, text = 'sair', command = quit )
        self.btSai.pack( side = BOTTOM )

    def prssBtNomeArqSumario( self ):
        self.strNomeArqSumario = \
            filedialog.askopenfilename( initialdir='/home/luis/git/predicao-epilepsia/physionet.org/files/chbmit/1.0.0/', filetypes = [ ( 'txt', '*.txt' ),
                                                      ( 'todos', '*' ) ] )
        self.entryNomeArqSumario.delete( 0, END )
        self.entryNomeArqSumario.insert( 0, self.strNomeArqSumario )

    def prssBtLocArqEEG( self ):
        self.strLocArqEEG = filedialog.askdirectory(initialdir='/home/luis/git/predicao-epilepsia/sinais/')
        self.entryLocArqEEG.delete( 0, END )
        self.entryLocArqEEG.insert( 0, self.strLocArqEEG )

    def prssBtLocJanEEG( self ):
        self.strLocJanEEG = filedialog.askdirectory(initialdir='/home/luis/git/predicao-epilepsia/janelas/novo/')
        self.entryLocJanEEG.delete( 0, END )
        self.entryLocJanEEG.insert( 0, self.strLocJanEEG )

    def prssBtEscolherCrisesTreino( self ):
        selecionados = self.lBxLtCrisesTreino.curselection()
        self.ltCrisesParaTreino = []
        for indice in selecionados:
            numUmaCriseTreino = self.dadosSumario.ltCrisesParaExperimentos[ indice ]
            self.ltCrisesParaTreino.append( numUmaCriseTreino )
        self.txtVarNumCrises.set( '' )
        self.txtVarCrisesTreino.set( 'crises p/ treino: ' +
                                     str( self.ltCrisesParaTreino ) )
        print( '\ninterictais para treino:\n' )
        self.tTotalInterictalTreino = 0
        self.ltInterictaisPTreino = []
        esperaPreIctal = False
        for itInicPeriodo in self.dadosSumario.ltInicPeriodo:
            if itInicPeriodo.antesDeQualCrise in self.ltCrisesParaTreino:
                if itInicPeriodo.nomePeriodo == 'interictal':
                    print( itInicPeriodo )
                    tIniInterictal = itInicPeriodo.tIni
                    print( 'tempo início:', tIniInterictal, 's' )
                    esperaPreIctal = True
                elif itInicPeriodo.nomePeriodo == 'pré-ictal' and esperaPreIctal:
                    print( itInicPeriodo )
                    tIniPreIctal = itInicPeriodo.tIni
                    print( 'tempo fim:   ', tIniPreIctal, 's' )
                    intrvAux = leSummary.IntervaloSeg( tIniInterictal, tIniPreIctal )
                    self.ltInterictaisPTreino.append( intrvAux )
                    esperaPreIctal = False
                    duracInterictal = tIniPreIctal - tIniInterictal
                    print( 'duração do interictal:', duracInterictal, 's\n' )
                    self.tTotalInterictalTreino += duracInterictal
        print( 'tempo total de interictal para treino:', self.tTotalInterictalTreino, 's' )
        print( 'lista de interictais para treino:' )
        print( *self.ltInterictaisPTreino, sep = '\n' )
        self.numJanTotalInterictalTreino = int( self.tTotalInterictalTreino / self.duracJanelaSegundos )
        strMensagem = '\nt. total interictal p/ treino: ' + \
            str( self.tTotalInterictalTreino ) + ' s (' + \
            str( self.numJanTotalInterictalTreino ) + ' janelas)'
        strAux = self.txtVarCrisesTreino.get()
        strAux += strMensagem
        self.txtVarCrisesTreino.set( strAux )

        print( '\npré-ictais para treino:\n' )
        self.tTotalPreIctalTreino = 0
        self.ltPreIctaisPTreino = []
        esperaPreIctal = False
        for itInicPeriodo in self.dadosSumario.ltInicPeriodo:
            if itInicPeriodo.antesDeQualCrise in self.ltCrisesParaTreino:
                if itInicPeriodo.nomePeriodo == 'pré-ictal' and not esperaPreIctal:
                    print( itInicPeriodo )
                    tIniPreIctal = itInicPeriodo.tIni
                    print( 'tempo início:', tIniPreIctal, 's' )
                    esperaPreIctal = True
                elif itInicPeriodo.nomePeriodo == 'ictal':
                    print( itInicPeriodo )
                    tIniIctal = itInicPeriodo.tIni
                    print( 'tempo fim:   ', tIniIctal, 's' )
                    intrvAux = leSummary.IntervaloSeg( tIniPreIctal, tIniIctal )
                    self.ltPreIctaisPTreino.append( intrvAux )
                    duracPreIctal = tIniIctal - tIniPreIctal
                    print( 'duração do pré-ictal:', duracPreIctal, 's\n' )
                    self.tTotalPreIctalTreino += duracPreIctal
                    esperaPreIctal = False
        print( 'tempo total de pré-ictal para treino:', self.tTotalPreIctalTreino, 's' )
        print( 'lista de pré-ictais para treino:' )
        print( *self.ltPreIctaisPTreino, sep = '\n' )
        self.numJanTotalPreIctalTreino = int( self.tTotalPreIctalTreino / self.duracJanelaSegundos )
        strMensagem = '\nt. total pré-ictal p/ treino: ' + \
            str( self.tTotalPreIctalTreino ) + ' s (' + \
            str( self.numJanTotalPreIctalTreino ) + ' janelas)'
        strAux = self.txtVarCrisesTreino.get()
        strAux += strMensagem
        self.txtVarCrisesTreino.set( strAux )

    def prssBtEscolherCrisesTeste( self ):
        selecionados = self.lBxLtCrisesTeste.curselection()
        self.ltCrisesParaTeste = []
        for indice in selecionados:
            numUmaCriseTeste = self.dadosSumario.ltCrisesParaExperimentos[ indice ]
            self.ltCrisesParaTeste.append( numUmaCriseTeste )
        self.txtVarNumCrises.set( '' )
        self.txtVarCrisesTeste.set( 'crises p/ teste: ' +
                                    str( self.ltCrisesParaTeste ) )
        self.frNumCrisesDoPaciente.destroy()
        print( '\ninterictais para teste:\n' )
        self.tTotalInterictalTeste = 0
        self.ltInterictaisPTeste = []
        esperaPreIctal = False
        for itInicPeriodo in self.dadosSumario.ltInicPeriodo:
            if itInicPeriodo.antesDeQualCrise in self.ltCrisesParaTeste:
                if itInicPeriodo.nomePeriodo == 'interictal':
                    print( itInicPeriodo )
                    tIniInterictal = itInicPeriodo.tIni
                    print( 'tempo início:', tIniInterictal, 's' )
                    esperaPreIctal = True
                elif itInicPeriodo.nomePeriodo == 'pré-ictal' and esperaPreIctal:
                    print( itInicPeriodo )
                    tIniPreIctal = itInicPeriodo.tIni
                    print( 'tempo fim:   ', tIniPreIctal, 's' )
                    intrvAux = leSummary.IntervaloSeg( tIniInterictal, tIniPreIctal )
                    self.ltInterictaisPTeste.append( intrvAux )
                    esperaPreIctal = False
                    duracInterictal = tIniPreIctal - tIniInterictal
                    print( 'duração do interictal:', duracInterictal, 's\n' )
                    self.tTotalInterictalTeste += duracInterictal
        print( 'tempo total de interictal para teste:', self.tTotalInterictalTeste, 's' )
        print( 'lista de interictais para teste:' )
        print( *self.ltInterictaisPTeste, sep = '\n' )
        self.numJanTotalInterictalTeste = int( self.tTotalInterictalTeste / self.duracJanelaSegundos )
        strMensagem = '\nt. total interictal p/ teste: ' + \
            str( self.tTotalInterictalTeste ) + ' s (' + \
            str( self.numJanTotalInterictalTeste ) + ' janelas)'
        strAux = self.txtVarCrisesTeste.get()
        strAux += strMensagem
        self.txtVarCrisesTeste.set( strAux )

        print( '\npré-ictais para teste:\n' )
        self.tTotalPreIctalTeste = 0
        self.ltPreIctaisPTeste = []
        esperaPreIctal = False
        for itInicPeriodo in self.dadosSumario.ltInicPeriodo:
            if itInicPeriodo.antesDeQualCrise in self.ltCrisesParaTeste:
                if itInicPeriodo.nomePeriodo == 'pré-ictal' and not esperaPreIctal:
                    print( itInicPeriodo )
                    tIniPreIctal = itInicPeriodo.tIni
                    print( 'tempo início:', tIniPreIctal, 's' )
                    esperaPreIctal = True
                elif itInicPeriodo.nomePeriodo == 'ictal':
                    print( itInicPeriodo )
                    tIniIctal = itInicPeriodo.tIni
                    print( 'tempo fim:   ', tIniIctal, 's' )
                    intrvAux = leSummary.IntervaloSeg( tIniPreIctal, tIniIctal )
                    self.ltPreIctaisPTeste.append( intrvAux )
                    duracPreIctal = tIniIctal - tIniPreIctal
                    print( 'duração do pré-ictal:', duracPreIctal, 's\n' )
                    self.tTotalPreIctalTeste += duracPreIctal
                    esperaPreIctal = False
        print( 'tempo total de pré-ictal para teste:', self.tTotalPreIctalTeste, 's' )
        print( 'lista de pré-ictais para teste:' )
        print( *self.ltPreIctaisPTeste, sep = '\n' )
        self.numJanTotalPreIctalTeste = int( self.tTotalPreIctalTeste / self.duracJanelaSegundos )
        strMensagem = '\nt. total pré-ictal p/ teste: ' + \
            str( self.tTotalPreIctalTeste ) + ' s (' + \
            str( self.numJanTotalPreIctalTeste ) + ' janelas)'
        strAux = self.txtVarCrisesTeste.get()
        strAux += strMensagem
        self.txtVarCrisesTeste.set( strAux )

    def prssBtLerSumario( self ):
        nomeArqSummaryDoPaciente = self.entryNomeArqSumario.get()
        duracMinutPreIctal = int( self.entryDuracaoPreIctal.get() )
        duracMinutPosIctal = int( self.entryDuracaoPosIctal.get() )
        self.duracJanelaSegundos = int( self.entryDuracaoJanela.get() )
        self.numAmostrasPorJanela = self.duracJanelaSegundos * \
            self.numAmostrasPorSegundo
        self.caminhoPArqsEEGcompactados = self.entryLocArqEEG.get()
        self.caminhoPArqsJanelasEEG = self.entryLocJanEEG.get()
        self.dadosSumario = leSummary.DadosSumario( nomeArqSummaryDoPaciente,
                                                    duracMinutPreIctal,
                                                    duracMinutPosIctal )
        self.txtVarNumCrises.set( 'Este paciente teve ' +
                                  str( self.dadosSumario.numCrisesDoPaciente )
                                  + ' crises.\nSelecione abaixo as que devem ser usadas no treino e no teste.\n'
                                  + 'Apenas crises suficientemente distantes entre si poderão ser usadas.\n'
                                  + 'Após escolhê-las com o mouse, clique nos botões abaixo da lista.' )
        self.lBxLtCrisesTreino[ 'state' ] = NORMAL
        self.btEscolherCrisesTreino[ 'state' ] = NORMAL
        for indCrise in self.dadosSumario.ltCrisesParaExperimentos:
            opcao = 'crise ' + str( indCrise )
            self.lBxLtCrisesTreino.insert( indCrise, opcao )
        self.lBxLtCrisesTeste[ 'state' ] = NORMAL
        self.btEscolherCrisesTeste[ 'state' ] = NORMAL
        for indCrise in self.dadosSumario.ltCrisesParaExperimentos:
            opcao = 'crise ' + str( indCrise )
            self.lBxLtCrisesTeste.insert( indCrise, opcao )
        print( '\nself.caminhoPArqsEEGcompactados =', self.caminhoPArqsEEGcompactados )
        arqsNoCaminho = [ arq for arq in listdir( self.caminhoPArqsEEGcompactados )
                          if isfile( join( self.caminhoPArqsEEGcompactados, arq ) ) ]
        print( '\narqsNoCaminho:' )
        print( arqsNoCaminho )
        print( '\narquivos citados em self.dadosSumario:' )
        self.dicEdfAscii = { }
        for itDadosUmArqEdf in self.dadosSumario.ltDadosArqEdf:
            nomeArqEDF = itDadosUmArqEdf.nomeArqEdf
            print( nomeArqEDF )
            dividido = nomeArqEDF.split( '.' )
            for itArqCaminho in arqsNoCaminho:
                if itArqCaminho.find( dividido[ 0 ] ) == 0:
                    print( 'Corresponde ao arquivo', itArqCaminho )
                    self.dicEdfAscii[ nomeArqEDF ] = itArqCaminho
                    break
        print( '\nself.dicEdfAscii:\n', self.dicEdfAscii )
        strAux = self.txtVarNomeArqSumario.get()
        strAux += ' '
        strAux += self.entryNomeArqSumario.get()
        self.txtVarNomeArqSumario.set( strAux )
        self.entryNomeArqSumario.destroy()
        self.btNomeArqSumario.destroy()

        strAux = self.txtVarDuracaoPreIctal.get()
        strAux += ' '
        strAux += self.entryDuracaoPreIctal.get()
        strAux += ', '
        self.txtVarDuracaoPreIctal.set( strAux )
        self.entryDuracaoPreIctal.destroy()

        strAux = self.txtVarDuracaoPosIctal.get()
        strAux += ' '
        strAux += self.entryDuracaoPosIctal.get()
        self.txtVarDuracaoPosIctal.set( strAux )
        self.entryDuracaoPosIctal.destroy()

        self.btLocArqEEG.destroy()
        self.entryLocArqEEG.destroy()
        self.frLocArqEEG.destroy()
        self.btLocJanEEG.destroy()
        self.entryLocJanEEG.destroy()
        self.frLocJanEEG.destroy()
        self.btLerSumario.destroy()
        self.frLerSumario.destroy()
        self.frNumCrisesDoPaciente.pack( side = TOP )
        self.lbNumCrisesDoPaciente.pack( side = LEFT )
        self.frLtsCrises.pack( side = TOP )
        self.frLtCrisesTreino.pack( side = LEFT )
        self.frLtCrisesTeste.pack( side = RIGHT )
        self.lbCrisesTreino.pack( side = TOP )
        self.lBxLtCrisesTreino.pack( side = TOP )
        self.btEscolherCrisesTreino.pack( side = BOTTOM )
        self.lbCrisesTeste.pack( side = TOP )
        self.lBxLtCrisesTeste.pack( side = TOP )
        self.btEscolherCrisesTeste.pack( side = BOTTOM )
        self.frBtEscolhaCrisesConcluida.pack()
        self.btEscolhaCrisesConcluida.pack( side = BOTTOM )

    def prssBtEscolhaCrisesConcluida( self ):
        self.lBxLtCrisesTreino.destroy()
        self.btEscolherCrisesTreino.destroy()
        self.lBxLtCrisesTeste.destroy()
        self.btEscolherCrisesTeste.destroy()
        self.frBtEscolhaCrisesConcluida.destroy()
        self.btEscolhaCrisesConcluida.destroy()
        self.lbEscolherPropTreino.pack( side = BOTTOM )
        self.scEscolherPropTreino.pack( side = BOTTOM )
        self.lbEscolherPropTeste.pack( side = BOTTOM )
        self.scEscolherPropTeste.pack( side = BOTTOM )
        self.btEscolhaPropTreinoTesteConcluida.pack( side = BOTTOM )

    def prssBtEscolhaPropTreinoTesteConcluida( self ):
        self.lbEscolherPropTreino.destroy()
        self.scEscolherPropTreino.destroy()
        self.lbEscolherPropTeste.destroy()
        self.scEscolherPropTeste.destroy()
        self.btEscolhaPropTreinoTesteConcluida.destroy()
        self.propTreino = self.intVarEscolherPropTreino.get()

        print( '\nproporção treino (%):', self.propTreino )
        self.numJanInterictalTreino = int( self.numJanTotalInterictalTreino * self.propTreino / 100 )
        print( 'número de janelas interictais para treino:', self.numJanInterictalTreino )
        self.numJanPreIctalTreino = int( self.numJanTotalPreIctalTreino * self.propTreino / 100 )
        print( 'número de janelas pré-ictais para treino:', self.numJanPreIctalTreino )
        strMensagem = '\nnúmero de janelas p/ treino: ' + \
            str(  self.numJanInterictalTreino ) + ' interictais e ' + \
            str(  self.numJanPreIctalTreino ) + ' pré-ictais.'
        strAux = self.txtVarCrisesTreino.get()
        strAux += strMensagem
        self.txtVarCrisesTreino.set( strAux )
        self.propTeste = self.intVarEscolherPropTeste.get()
        print( 'proporção teste (%):', self.propTeste )
        self.numJanInterictalTeste = int( self.numJanTotalInterictalTeste * self.propTeste / 100 )
        print( 'número de janelas interictais para teste:', self.numJanInterictalTeste )
        self.numJanPreIctalTeste = int( self.numJanTotalPreIctalTeste * self.propTeste / 100 )
        print( 'número de janelas pré-ictais para teste:', self.numJanPreIctalTeste )
        strMensagem = '\nnúmero de janelas p/ teste: ' + \
            str(  self.numJanInterictalTeste ) + ' interictais e ' + \
            str(  self.numJanPreIctalTeste ) + ' pré-ictais.'
        strAux = self.txtVarCrisesTeste.get()
        strAux += strMensagem
        self.txtVarCrisesTeste.set( strAux )
        self.intervaloInicJanInterictalTreino = self.tTotalInterictalTreino / self.numJanInterictalTreino
        print( '\nintervalo entre inícios de janelas interictais treino:',
               self.intervaloInicJanInterictalTreino, 's' )
        self.intervaloInicJanPreIctalTreino = self.tTotalPreIctalTreino / self.numJanPreIctalTreino
        print( 'intervalo entre inícios de janelas pré-ictais treino:',
               self.intervaloInicJanPreIctalTreino, 's' )
        self.intervaloInicJanInterictalTeste = self.tTotalInterictalTeste / self.numJanInterictalTeste
        print( 'intervalo entre inícios de janelas interictais teste:',
               self.intervaloInicJanInterictalTeste, 's' )
        self.intervaloInicJanPreIctalTeste = self.tTotalPreIctalTeste / self.numJanPreIctalTeste
        print( 'intervalo entre inícios de janelas pré-ictais teste:',
               self.intervaloInicJanPreIctalTeste, 's' )
        print( '\ninícios de janelas para treino e teste:\n' )
        numAlgarismosArqInterictalTreino = math.ceil( math.log10( self.numJanInterictalTreino ) )
        numAlgarismosArqPreIctalTreino = math.ceil( math.log10( self.numJanPreIctalTreino ) )
        self.ltTInicJanIntericTreino = []
        numJan = 1
        for it in self.ltInterictaisPTreino:
            inicJan = it.tIni
            limite = it.tFin - self.duracJanelaSegundos
            nomeArqEDFanterior = ' '
            while inicJan < limite:
                nomeArqEDF, tNoArq = self.dadosSumario.ltTAcumArqEdf.emQualArq( inicJan )
                if nomeArqEDF.find( 'fora' ) < 0:
                    if nomeArqEDF != nomeArqEDFanterior:
                        umEEG = eegUmArqPhysionet.EEGumArqPhysionet( self.caminhoPArqsEEGcompactados + \
                                                                     '/' + self.dicEdfAscii[ nomeArqEDF ] )
                        nomeArqEDFanterior = nomeArqEDF
                    self.ltTInicJanIntericTreino.append( ( self.dicEdfAscii[ nomeArqEDF ], int( tNoArq ) ) )
                    nomeArqJan = self.caminhoPArqsJanelasEEG + \
                        '/janTreinoInterictal_' + \
                        str( numJan ).zfill( numAlgarismosArqInterictalTreino ) + '.txt'
                    umEEG.gravaArqJanela( nomeArqJan,
                                          int( tNoArq * self.numAmostrasPorSegundo ),
                                          self.numAmostrasPorJanela )
                    numJan += 1
                inicJan += self.intervaloInicJanInterictalTreino
        print( 'lista de tempos de inícios de janelas interictais para treino:' )
        print( self.ltTInicJanIntericTreino )

        self.ltTInicJanPreIcTreino = []
        numJan = 1
        for it in self.ltPreIctaisPTreino:
            inicJan = it.tIni
            limite = it.tFin - self.duracJanelaSegundos
            nomeArqEDFanterior = ' '
            while inicJan < limite:
                nomeArqEDF, tNoArq = self.dadosSumario.ltTAcumArqEdf.emQualArq( inicJan )
                if nomeArqEDF.find( 'fora' ) < 0:
                    if nomeArqEDF != nomeArqEDFanterior:
                        umEEG = eegUmArqPhysionet.EEGumArqPhysionet( self.caminhoPArqsEEGcompactados + \
                                                                     '/' + self.dicEdfAscii[ nomeArqEDF ] )
                        nomeArqEDFanterior = nomeArqEDF
                    self.ltTInicJanPreIcTreino.append( ( self.dicEdfAscii[ nomeArqEDF ], int( tNoArq ) ) )
                    nomeArqJan = self.caminhoPArqsJanelasEEG + \
                        '/janTreinoPreIctal_' + \
                        str( numJan ).zfill( numAlgarismosArqPreIctalTreino ) + '.txt'
                    umEEG.gravaArqJanela( nomeArqJan,
                                          int( tNoArq * self.numAmostrasPorSegundo ),
                                          self.numAmostrasPorJanela )
                    numJan += 1
                inicJan += self.intervaloInicJanPreIctalTreino
        print( '\nlista de tempos de inícios de janelas pré-ictais para treino:' )
        print( self.ltTInicJanPreIcTreino )
        numAlgarismosArqInterictalTeste = math.ceil( math.log10( self.numJanInterictalTeste ) )
        numAlgarismosArqPreIctalTeste = math.ceil( math.log10( self.numJanPreIctalTeste ) )
        self.ltTInicJanIntericTeste = []
        numJan = 1
        for it in self.ltInterictaisPTeste:
            inicJan = it.tIni
            limite = it.tFin - self.duracJanelaSegundos
            nomeArqEDFanterior = ' '
            while inicJan < limite:
                nomeArqEDF, tNoArq = self.dadosSumario.ltTAcumArqEdf.emQualArq( inicJan )
                if nomeArqEDF.find( 'fora' ) < 0:
                    if nomeArqEDF != nomeArqEDFanterior:
                        umEEG = eegUmArqPhysionet.EEGumArqPhysionet( self.caminhoPArqsEEGcompactados + \
                                                                     '/' + self.dicEdfAscii[ nomeArqEDF ] )
                        nomeArqEDFanterior = nomeArqEDF
                    self.ltTInicJanIntericTeste.append( ( self.dicEdfAscii[ nomeArqEDF ], int( tNoArq ) ) )
                    nomeArqJan = self.caminhoPArqsJanelasEEG + \
                        '/janTesteInterictal_' + \
                        str( numJan ).zfill( numAlgarismosArqInterictalTeste ) + '.txt'
                    umEEG.gravaArqJanela( nomeArqJan,
                                          int( tNoArq * self.numAmostrasPorSegundo ),
                                          self.numAmostrasPorJanela )
                    numJan += 1
                inicJan += self.intervaloInicJanInterictalTeste
        print( '\nlista de tempos de inícios de janelas interictais para teste:' )
        print( self.ltTInicJanIntericTeste )

        self.ltTInicJanPreIcTeste = []
        numJan = 1
        for it in self.ltPreIctaisPTeste:
            inicJan = it.tIni
            limite = it.tFin - self.duracJanelaSegundos
            nomeArqEDFanterior = ' '
            while inicJan < limite:
                nomeArqEDF, tNoArq = self.dadosSumario.ltTAcumArqEdf.emQualArq( inicJan )
                if nomeArqEDF.find( 'fora' ) < 0:
                    if nomeArqEDF != nomeArqEDFanterior:
                        umEEG = eegUmArqPhysionet.EEGumArqPhysionet( self.caminhoPArqsEEGcompactados + \
                                                                     '/' + self.dicEdfAscii[ nomeArqEDF ] )
                        nomeArqEDFanterior = nomeArqEDF
                    self.ltTInicJanPreIcTeste.append( ( self.dicEdfAscii[ nomeArqEDF ], int( tNoArq ) ) )
                    nomeArqJan = self.caminhoPArqsJanelasEEG + \
                        '/janTestePreIctal_' + \
                        str( numJan ).zfill( numAlgarismosArqPreIctalTeste ) + '.txt'
                    umEEG.gravaArqJanela( nomeArqJan,
                                          int( tNoArq * self.numAmostrasPorSegundo ),
                                          self.numAmostrasPorJanela )
                    numJan += 1
                inicJan += self.intervaloInicJanPreIctalTeste
        print( '\nlista de tempos de inícios de janelas pré-ictais para teste:' )
        print( self.ltTInicJanPreIcTeste )
        print( '\nMontagem de janelas concluída.\n' )
raiz = Tk()
Packing( raiz )
raiz.mainloop()
