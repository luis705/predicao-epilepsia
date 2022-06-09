#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Horario:
    def __init__( self, strHorario ):
        tmp = strHorario.split( ':' )
        self.h = int( tmp[ 0 ] )
        self.min = int( tmp[ 1 ] )
        self.s = int( tmp[ 2 ] )
    def __repr__( self ):
        return repr( self.h ).zfill( 2 ) + \
            'h' + repr( self.min ).zfill( 2 ) + \
            'min' + repr( self.s ).zfill( 2 ) + 's'
    def emSegundos( self ):
        return self.h * 3600 + \
            self.min * 60 + self.s
    def __sub__( self, outro ):
        return self.emSegundos() - outro.emSegundos()
    def colocaNoLimite235959( self ):
        if self.h > 23:
            self.h -= 24

class IntervaloSeg:
    def __init__( self, tIni, tFin ):
        self.tIni = tIni # em segundos
        self.tFin = tFin # em segundos
    def __repr__( self ):
        return 'de ' + repr( self.tIni ) + \
            ' s a ' + repr( self.tFin ) + ' s'

class DadosUmArqEdf:
    def __init__( self ):
        self.nomeArqEdf = ''
        self.ltPeriodoIctal = []
        self.dia = -1
        self.horarioIni = Horario( '-1:-1:-1' )
        self.horarioFin = Horario( '-1:-1:-1' )
        self.duracaoArq = -1
    def __repr__( self ):
        return self.nomeArqEdf \
            + '\ndia ' + repr( self.dia ) \
            + ', de ' + repr( self.horarioIni ) \
            + ' a ' + repr( self.horarioFin ) \
            + ', duração: ' + repr( self.duracaoArq ) \
            + ' s, ictais: ' + str( self.ltPeriodoIctal ) + '\n'

class InicPeriodo:
    def __init__( self, tIni, tNoArq, nomePeriodo, nomeArq, antesDeQualCrise = 0 ):
        self.tIni = tIni # em segundos
        self.tNoArq = tNoArq # em segundos
        self.nomePeriodo = nomePeriodo
        self.nomeArq = nomeArq
        self.antesDeQualCrise = antesDeQualCrise
    def __repr__( self ):
        return 't.acum.início: ' \
            + repr( self.tIni ).rjust( 8 ) + ' s, t.no arq: ' \
            + repr( self.tNoArq ).rjust( 6 ) + ' s, ' \
            + repr( self.nomePeriodo ).ljust( 20 ) \
            + repr( self.nomeArq ).ljust( 20 ) \
            + ', antes da crise ' + str( self.antesDeQualCrise )

class TAcumArqEdf:
    def __init__( self, nomeArq, tAcumIni, tAcumFin ):
        self.nomeArq = nomeArq
        self.tAcumIni = tAcumIni
        self.tAcumFin = tAcumFin
    def __repr__( self ):
        return ' ' + self.nomeArq + ' de ' \
            + repr( self.tAcumIni ).rjust( 8 ) + ' s a ' \
            + repr( self.tAcumFin ).rjust( 8 ) + ' s'

class ListaTAcumArqEdf:
    def __init__( self ):
        self.lt = []
    def append( self, elemento ):
        self.lt.append( elemento )
    def print( self ):
        print( *self.lt, sep = '\n' )
    def emQualArq( self, tempo ):
        resNomeArq = 'fora de arquivo'
        resTNoArq = -1
        for it in self.lt:
            if it.tAcumIni <= tempo and tempo <= it.tAcumFin:
                resNomeArq = it.nomeArq
                resTNoArq = tempo - it.tAcumIni
                break
        return resNomeArq, resTNoArq

class DadosSumario:
    def __init__( self, nomeArqSummaryDoPaciente,
                  duracMinutPreIctal, duracMinutPosIctal ):
        self.nomeArqSummaryDoPaciente = nomeArqSummaryDoPaciente
        self.duracSegundosPreIctal = duracMinutPreIctal * 60
        self.duracSegundosPosIctal = duracMinutPosIctal * 60
        self.ltDadosArqEdf = []
        self.ltInicPeriodo = []
        self.ltTAcumArqEdf = ListaTAcumArqEdf()
        self.numCrisesDoPaciente = 0
        self.ltCrisesParaExperimentos = [] # Compatíveis com durações do pré-ictal e do pós-ictal.
        with open( nomeArqSummaryDoPaciente ) as arqSummary:
            dia = 0
            horaIniArqAnterior = 0
            linhaSum = arqSummary.readline()
            while linhaSum:
                if linhaSum.find( "Name" ) > -1:
                    dadosUmArqEdf = DadosUmArqEdf()
                    # linha com nome do arq. EDF:
                    tmp = linhaSum.split( ' ' )
                    dadosUmArqEdf.nomeArqEdf = tmp[ -1 ].strip()
                    # linha com tempo inicial do arq.:
                    linhaSum = arqSummary.readline()
                    tmp = linhaSum.split( ' ' )
                    tempoIni = tmp[ -1 ].strip()
                    dadosUmArqEdf.horarioIni = Horario( tempoIni )
                    # Verifica se mudou o dia:
                    if dadosUmArqEdf.horarioIni.h < horaIniArqAnterior:
                        dia += 1
                    dadosUmArqEdf.dia = dia
                    horaIniArqAnterior = dadosUmArqEdf.horarioIni.h
                    # linha com tempo final do arq.:
                    linhaSum = arqSummary.readline()
                    tmp = linhaSum.split( ' ' )
                    tempoFin = tmp[ -1 ].strip()
                    dadosUmArqEdf.horarioFin = Horario( tempoFin )
                    dadosUmArqEdf.duracaoArq = dadosUmArqEdf.horarioFin \
                                               - dadosUmArqEdf.horarioIni
                    dadosUmArqEdf.horarioFin.colocaNoLimite235959()
                    # linha com número de crises:
                    linhaSum = arqSummary.readline()
                    tmp = linhaSum.split( ' ' )
                    numCrises = int( tmp[ -1 ].strip() )
                    self.numCrisesDoPaciente += numCrises
                    ltPeriodoIctal = []
                    for n in range( numCrises ):
                        linhaSum = arqSummary.readline()
                        tmp = linhaSum.split( ' ' )
                        tIniIctal = int( tmp[ -2 ].strip() )
                        linhaSum = arqSummary.readline()
                        tmp = linhaSum.split( ' ' )
                        tFinIctal = int( tmp[ -2 ].strip() )
                        periodoIctal = IntervaloSeg( tIniIctal, tFinIctal )
                        ltPeriodoIctal.append( periodoIctal )
                    dadosUmArqEdf.ltPeriodoIctal = ltPeriodoIctal.copy()
                    self.ltDadosArqEdf.append( dadosUmArqEdf )
                linhaSum = arqSummary.readline()
        arqSummary.close()
        print( '\nEste paciente teve', self.numCrisesDoPaciente, 'crises.\n' )
        self.preencheLtInicPeriodo()
        print( '\nlista de inícios de períodos:\n' )
        print( *self.ltInicPeriodo, sep = '\n' )
        print( '\nlista de informações sobre os arquivos EDF:\n' )
        print( *self.ltDadosArqEdf, sep = '\n' )
    def criterOrden( elemento ):
        return elemento.tIni
    def preencheLtInicPeriodo( self ):
        # Monta a primeira versão da self.ltInicPeriodo:
        tAcumulado = 0
        primeiro = True
        for itDadosUmArqEdf in self.ltDadosArqEdf:
            if primeiro == True:
                # Deixa um intervalo de segurança no início do
                # primeiro arquivo, como possível pós-ictal de uma
                # crise que poderia estar imediatamente antes dele:
                tmp = InicPeriodo( self.duracSegundosPosIctal,
                                   self.duracSegundosPosIctal, 'interictal',
                                   itDadosUmArqEdf.nomeArqEdf )
                self.ltInicPeriodo.append( tmp )
            if primeiro == False:
                intervalo = itDadosUmArqEdf.horarioIni - tFinal
                if intervalo < 0:
                    intervalo += 24 * 60 * 60
                tmp = InicPeriodo( tAcumulado, 'n.a.', 'intervalo',
                                   'fora de arquivo' )
                self.ltInicPeriodo.append( tmp )
                tAcumulado += intervalo
            tmp = InicPeriodo( tAcumulado, 0, 'início de arquivo', \
                              itDadosUmArqEdf.nomeArqEdf )
            self.ltInicPeriodo.append( tmp )
            tmp = TAcumArqEdf( itDadosUmArqEdf.nomeArqEdf, \
                               tAcumulado, \
                               tAcumulado + itDadosUmArqEdf.duracaoArq )
            self.ltTAcumArqEdf.append( tmp )
            for itPeriodoIctal in itDadosUmArqEdf.ltPeriodoIctal:
                tPreIctal = tAcumulado + itPeriodoIctal.tIni \
                    - self.duracSegundosPreIctal
                if tPreIctal < 0:
                    tPreIctal = 0
                tmp = InicPeriodo( tPreIctal, -1, 'pré-ictal', 'pendente' )
                self.ltInicPeriodo.append( tmp )
                tmp = InicPeriodo( tAcumulado + itPeriodoIctal.tIni, -1, \
                                  'ictal', itDadosUmArqEdf.nomeArqEdf )
                self.ltInicPeriodo.append( tmp )
                tmp = InicPeriodo( tAcumulado + itPeriodoIctal.tFin, -1, \
                                  'pós-ictal', itDadosUmArqEdf.nomeArqEdf )
                self.ltInicPeriodo.append( tmp )
                tmp = InicPeriodo( tAcumulado + itPeriodoIctal.tFin \
                                   + self.duracSegundosPosIctal, -1,
                                  'interictal', 'pendente' )
                self.ltInicPeriodo.append( tmp )
            tAcumulado += itDadosUmArqEdf.duracaoArq
            tFinal = itDadosUmArqEdf.horarioFin
            primeiro = False
        # Insere em self.ltInicPeriodo os nomes dos arquivos em que eles estão:
        for itInicPeriodo in self.ltInicPeriodo:
            if itInicPeriodo.nomeArq == 'pendente':
                itInicPeriodo.nomeArq, tNoArq = self.ltTAcumArqEdf.emQualArq( itInicPeriodo.tIni )
        self.ltInicPeriodo.sort( key = DadosSumario.criterOrden )
        tIniArq = 0
        for itInicPeriodo in self.ltInicPeriodo:
            if itInicPeriodo.nomePeriodo.find( 'início' ) > -1:
                tIniArq = itInicPeriodo.tIni
            if itInicPeriodo.nomePeriodo.find( 'ictal' ) > -1:
                itInicPeriodo.tNoArq = itInicPeriodo.tIni - tIniArq
        # Ajusta o campo antesDeQualCrise em todos os registros:
        if self.numCrisesDoPaciente > 0:
            auxAntesDeQualCrise = 1
            for itInicPeriodo in self.ltInicPeriodo:
                itInicPeriodo.antesDeQualCrise = auxAntesDeQualCrise
                if itInicPeriodo.nomePeriodo == 'ictal':
                    if auxAntesDeQualCrise < self.numCrisesDoPaciente:
                        auxAntesDeQualCrise += 1
                    else:
                        auxAntesDeQualCrise = 0
        # Verifica se a duração do pré-ictal está compatível com o tempo entre
        # ictais e com o início do primeiro arquivo:
        auxUltTempo = 0
        print( '\nVerificação da compatibilidade entre duração de pré-ictais' )
        print( 'e os intervalos entre os ictais:' )
        for itInicPeriodo in self.ltInicPeriodo:
            if itInicPeriodo.nomePeriodo == 'ictal':
                print( '\nictal', itInicPeriodo.antesDeQualCrise,
                       'iniciado em', itInicPeriodo.tIni, 's' )
                # Não é a primeira crise:
                if itInicPeriodo.antesDeQualCrise > 1:
                    intervalo = itInicPeriodo.tIni - auxUltTempo
                    print( 'intervalo desde o fim da última crise:',
                           intervalo, 's =', int( intervalo / 60 ), 'min' )
                    if intervalo > self.duracSegundosPreIctal:
                        print( 'Está suficientemente distante da crise anterior.' )
                        self.ltCrisesParaExperimentos.append( itInicPeriodo.antesDeQualCrise )
                    else:
                        print( 'Não está suficientemente distante da crise anterior.' )
                else: # É a primeira crise:
                    if itInicPeriodo.tIni > self.duracSegundosPosIctal + self.duracSegundosPreIctal + 10:
                        print( 'Está suficientemente distante do início geral do tempo.' )
                        self.ltCrisesParaExperimentos.append( itInicPeriodo.antesDeQualCrise )
                    else:
                        print( 'Não está suficientemente distante do início geral do tempo.' )
            elif itInicPeriodo.nomePeriodo == 'pós-ictal':
                auxUltTempo = itInicPeriodo.tIni
        print( '\nCrises adequadas para experimentos,' )
        print( 'levando-se em conta as durações dos períodos:', self.ltCrisesParaExperimentos )
