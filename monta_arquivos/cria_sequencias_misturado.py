"""
Uso no anaconda:
    python3 cria_sequencias_Tsiouris.py -t diretorio_dos_arquivos_fft -n n_de_vetores
    O diretório dos arquivos é o caminho completo para o diretório que
    contém os arquivos de FFT. Esses arquivos devem ter "Interictal" ou
    "PreIctal" no nome.
    n_de_vetores é o número de vetores por sequência, o Pires usou tamanho_seq
    então acho legal usarmos esse número também.
    Cuidado: as sequências criadas vão estar na pasta que está esse programa
    (cria-Sequencias_Tsiouris) então se tiver alguma sequência nela tire antes
    de executar para que não sejam sobrescritas.
"""

import getopt
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm, trange

optlist, args = getopt.gnu_getopt(sys.argv[1:], 't:s:')
for (opcao, argumento) in optlist:
    if opcao == '-t':
        nomeDirDados = argumento
    if opcao == '-s':
        tamanho_seq = int(argumento)

treino_interictal = []
treino_preictal = []
teste_interictal = []
teste_preictal = []

for file in tqdm(os.listdir(nomeDirDados), desc='Lendo vetores', leave=False):
    if 'Treino' in file:
        if 'Interictal' in file:
            vetor = (
                pd.read_parquet(os.path.join(nomeDirDados, file))
                .to_numpy()
                .T[0]
            )
            if np.any(np.isnan(vetor)):
                continue
            # print(f'Vetor de interictal: {vetor}')
            treino_interictal.append(vetor)
        elif 'PreIctal' in file:
            vetor = (
                pd.read_parquet(os.path.join(nomeDirDados, file))
                .to_numpy()
                .T[0]
            )
            if np.any(np.isnan(vetor)):
                continue
            treino_preictal.append(vetor)
    elif 'Teste' in file:
        if 'Interictal' in file:
            vetor = (
                pd.read_parquet(os.path.join(nomeDirDados, file))
                .to_numpy()
                .T[0]
            )
            if np.any(np.isnan(vetor)):
                continue
            # print(f'Vetor de interictal: {vetor}')
            teste_interictal.append(vetor)
        elif 'PreIctal' in file:
            vetor = (
                pd.read_parquet(os.path.join(nomeDirDados, file))
                .to_numpy()
                .T[0]
            )
            if np.any(np.isnan(vetor)):
                continue
            teste_preictal.append(vetor)

treino_interictal = np.array(treino_interictal)
treino_preictal = np.array(treino_preictal)
teste_interictal = np.array(teste_interictal)
teste_preictal = np.array(teste_preictal)

np.random.shuffle(treino_interictal)
np.random.shuffle(treino_preictal)
np.random.shuffle(teste_interictal)
np.random.shuffle(teste_preictal)

nomeDirDados = Path(nomeDirDados)
tipo_vetor = nomeDirDados.stem
paciente = nomeDirDados.parents[0].stem
pasta_resultado = Path('sequencias', paciente, str(tamanho_seq), tipo_vetor)

for i in trange(
    len(treino_interictal) // tamanho_seq, desc='Treino inter', leave=False
):
    pd.DataFrame(
        treino_interictal[treino_interictal.shape[0] - tamanho_seq :]
    ).to_parquet(pasta_resultado / f'seqTreinoInterictal{i}.txt')
    treino_interictal = treino_interictal[
        0 : treino_interictal.shape[0] - tamanho_seq
    ]

for i in trange(
    len(treino_preictal) // tamanho_seq, desc='Treino pré', leave=False
):
    pd.DataFrame(
        treino_preictal[treino_preictal.shape[0] - tamanho_seq :]
    ).to_parquet(pasta_resultado / f'seqTreinoPreictal{i}.txt')
    treino_preictal = treino_preictal[
        0 : treino_preictal.shape[0] - tamanho_seq
    ]

for i in trange(
    len(teste_interictal) // tamanho_seq, desc='Teste inter', leave=False
):
    pd.DataFrame(
        teste_interictal[teste_interictal.shape[0] - tamanho_seq :]
    ).to_parquet(pasta_resultado / f'seqTesteInterictal{i}.txt')
    teste_interictal = teste_interictal[
        0 : treino_interictal.shape[0] - tamanho_seq
    ]

for i in trange(
    len(teste_preictal) // tamanho_seq, desc='Teste pré', leave=False
):
    pd.DataFrame(
        teste_preictal[teste_preictal.shape[0] - tamanho_seq :]
    ).to_parquet(pasta_resultado / f'seqTestePreictal{i}.txt')
    teste_preictal = teste_preictal[0 : teste_preictal.shape[0] - tamanho_seq]
