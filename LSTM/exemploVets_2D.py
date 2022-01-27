#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modo de uso:
# ./nomeDoPrograma.py -e numEpocas \
#                     -n numCamadas numNeuronios1Camada,numNeuronios2camada,...,numNeuroniosNCamada \
#                     -d nomePastaDadosTreinoTeste/ \
#                     -p nomeArqPredicoes.txt
# O programa supõe que, na pasta indicada, haja arquivos texto contendo
# sequências, arquivos esses cujos nomes começam com 'seq' e têm seus nomes
# numerados, e que haja arquivos texto contendo os rótulos correspondentes,
# em arquivos cujos nomes começam com 'rot' e que também têm seus nomes
# numerados, de acordo com os arquivos contendo as sequências.

def pires():
    import getopt
    import os
    import sys

    import numpy as np
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense
    from tensorflow.keras.layers import LSTM

    # INPUTS
    numEpocas = None
    camadas = None
    numCamadas = None
    nomeArqPredicoes = None
    nomeDirDados = None

    optlist, args = getopt.gnu_getopt(sys.argv[1:], 'd:e:n:p:c')
    for(opcao, argumento) in optlist:
        if opcao == '-e':
            numEpocas = int(argumento)
        elif opcao == '-n':
            camadas = argumento.split(',')
            print(camadas)
            camadas = list(map(int, camadas))
            numCamadas = camadas.pop(0)
            if len(camadas) != numCamadas:
                print('A quantidade de numeros de neurônios deve ser igual à quantidade de camadas')
                sys.exit(1)
        elif opcao == '-p':
            nomeArqPredicoes = argumento
        elif opcao == '-d':
            nomeDirDados = argumento

    if not nomeDirDados:
        nomeDirDados = input('Qual o nome do diretório com os arquivos para treino/teste? ')
    if not nomeArqPredicoes:
        nomeArqPredicoes = input('Qual o nome do arquivo que as predições devem ser salvas? ')
    if not numEpocas:
        numEpocas = int(input('Qual o número de épocas de treinamento? '))
    if not numCamadas:
        numCamadas = int(input('Qual o número de camadas LSTM da rede? '))

        camadas = []
        for i in range(numCamadas):
            camadas.append(int(input(f"Quantas células de memória tem a camada número {i + 1}? ")))

    # Lendo os dados
    arqsDirs = os.listdir(nomeDirDados)
    print('\nO que foi encontrado na pasta', nomeDirDados, ':\n')
    print(arqsDirs)
    ltArqsSeq = []
    ltArqsRot = []
    for elemento in arqsDirs:
        if elemento.find('.txt', -4) > -1:
            if elemento.find('seq', 0) > -1:
                ltArqsSeq.append(elemento)
            elif elemento.find('rot', 0) > -1:
                ltArqsRot.append(elemento)
    numSeqs = len(ltArqsSeq)
    print('\nnumSeqs =', numSeqs, '\n')
    numRots = len(ltArqsRot)
    print('\nnumRots =', numRots, '\n')
    if numSeqs != numRots:
        print('O número de sequências deve ser igual ao número de rótulos.')
        sys.exit(1)
    ltArqsSeq.sort()
    ltArqsRot.sort()
    print('\narquivos contendo sequências:\n', ltArqsSeq)
    print('\narquivos contendo rótulos:\n', ltArqsRot)
    primeira = True
    for umArqSeq in ltArqsSeq:
        print('\narquivo', umArqSeq)
        umaSeq = np.loadtxt(os.path.join(nomeDirDados, umArqSeq))
        print(umaSeq)
        print('\nformato de umaSeq:', umaSeq.shape)
        if primeira:
            npSeqs = np.array([umaSeq])
            print('\nformato de npSeqs:', npSeqs.shape)
            primeira = False
        else:
            npSeqs = np.append(npSeqs, np.array([umaSeq]), 0)
            print('\nformato de npSeqs:', npSeqs.shape)
    print('\nnpSeqs\n', npSeqs)
    print('\nformato de npSeqs:', npSeqs.shape)
    # Falta fazer a normalização (ajuste de escala).
    primeira = True
    for umArqRot in ltArqsRot:
        print('\narquivo', umArqRot)
        umRot = np.loadtxt(os.path.join(nomeDirDados, umArqRot))
        print('\nformato de umRot:', umRot.shape)
        if primeira:
            npRots = np.array([umRot])
            print('\nformato de npRots:', npRots.shape)
            primeira = False
        else:
            npRots = np.append(npRots, np.array([umRot]), 0)
            print('\nformato de npRots:', npRots.shape)
    print('\nnpRots\n', npRots)
    print('\nformato de npRots:', npRots.shape)
    numSeqsTreino = int(0.8 * numSeqs)
    print('Serão usadas %d sequências para treino ' % numSeqsTreino)
    numSeqsTeste = numSeqs - numSeqsTreino
    print('e %d sequências para teste.' % numSeqsTeste)
    seqsTreino = npSeqs[0:numSeqsTreino]
    print('forma do conjunto de sequências de treino:', seqsTreino.shape)
    rotsTreino = npRots[0:numSeqsTreino]
    print('forma do conjunto de rótulos de treino:', rotsTreino.shape)
    seqsTeste = npSeqs[numSeqsTreino:]
    print('forma do conjunto de sequências de teste:', seqsTeste.shape)
    rotsTeste = npRots[numSeqsTreino:]
    print('forma do conjunto de rótulos de teste:', rotsTeste.shape)

    # Criação da rede neural
    model = Sequential()
    batch_size = 1
    for camada in range(len(camadas)):
        if camada != len(camadas) - 1:
            model.add(LSTM(camadas[camada],
                           batch_input_shape=(batch_size, seqsTreino.shape[1],
                                              seqsTreino.shape[2]),
                           stateful=False, return_sequences=True))
            ultimo = True
        else:
            model.add(LSTM(camadas[camada],
                           batch_input_shape=(batch_size, seqsTreino.shape[1],
                                              seqsTreino.shape[2]),
                           stateful=False))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    print(model.summary())
    model.fit(seqsTreino, rotsTreino, epochs=numEpocas, batch_size=batch_size,
              verbose=1, shuffle=True)
    rotsPreditos = model.predict(seqsTeste, batch_size=batch_size)
    np.savetxt(nomeArqPredicoes, rotsPreditos)

    erro = model.evaluate(seqsTeste, rotsTeste, batch_size=batch_size)
    print(f'Erro de teste: {erro}')


if __name__ == '__main__':
    import teste_bebidas.cu