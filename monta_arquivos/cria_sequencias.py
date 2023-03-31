"""
Uso no anaconda:
    python3 cria_sequencias_Tsiouris.py -t diretorio_dos_arquivos_fft -n n_de_vetores
    O diretório dos arquivos é o caminho completo para o diretório que
    contém os arquivos de FFT. Esses arquivos devem ter "Interictal" ou
    "PreIctal" no nome.
    n_de_vetores é o número de janelas por sequência, o Pires usou tamanho_seq
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
from tqdm import tqdm


optlist, args = getopt.gnu_getopt(sys.argv[1:], "t:s:")
for (opcao, argumento) in optlist:
    if opcao == "-t":
        nomeDirDados = argumento
    if opcao == "-s":
        tamanho_seq = int(argumento)

treino_interictal = []
treino_preictal = []
teste_interictal = []
teste_preictal = []

shape = pd.read_parquet(Path(nomeDirDados, os.listdir(nomeDirDados)[0])).to_numpy().T[0].shape
for file in tqdm(os.listdir(nomeDirDados)):
    vetor = pd.read_parquet(Path(nomeDirDados, file)).to_numpy().T[0]
    if vetor.shape != shape:
        continue
    if np.any(np.isnan(vetor)):
        continue
    if "Treino" in file:
        if "Interictal" in file:
            treino_interictal.append(vetor)
        elif "PreIctal" in file:
            treino_preictal.append(vetor)
    elif "Teste" in file:
        if "Interictal" in file:
            teste_interictal.append(vetor)
        elif "PreIctal" in file:
            teste_preictal.append(vetor)


treino_interictal = np.array(treino_interictal)
treino_preictal = np.array(treino_preictal)
teste_interictal = np.array(teste_interictal)
teste_preictal = np.array(teste_preictal)

np.random.shuffle(treino_interictal)
np.random.shuffle(treino_preictal)
np.random.shuffle(teste_interictal)
np.random.shuffle(teste_preictal)

for i in range(len(treino_interictal) // tamanho_seq):
    para_salvar = pd.DataFrame(treino_interictal[treino_interictal.shape[0] - tamanho_seq :])
    para_salvar.rename(columns={i: str(i) for i in para_salvar.columns}, inplace=True)
    para_salvar.to_parquet(f"seqTreinoInterictal{i}.parquet")
    treino_interictal = treino_interictal[0 : treino_interictal.shape[0] - tamanho_seq]

for i in range(len(treino_preictal) // tamanho_seq):
    para_salvar = pd.DataFrame(treino_preictal[treino_preictal.shape[0] - tamanho_seq :])
    para_salvar.rename(columns={i: str(i) for i in para_salvar.columns}, inplace=True)
    para_salvar.to_parquet(f"seqTreinoPreictal{i}.parquet")
    treino_preictal = treino_preictal[0 : treino_preictal.shape[0] - tamanho_seq]

for i in range(len(teste_interictal) // tamanho_seq):
    para_salvar = pd.DataFrame(teste_interictal[teste_interictal.shape[0] - tamanho_seq :])
    para_salvar.rename(columns={i: str(i) for i in para_salvar.columns}, inplace=True)
    para_salvar.to_parquet(f"seqTesteInterictal{i}.parquet")
    teste_interictal = teste_interictal[0 : treino_interictal.shape[0] - tamanho_seq]

for i in range(len(teste_preictal) // tamanho_seq):
    para_salvar = pd.DataFrame(teste_preictal[teste_preictal.shape[0] - tamanho_seq :])
    para_salvar.rename(columns={i: str(i) for i in para_salvar.columns}, inplace=True)
    para_salvar.to_parquet(f"seqTestePreictal{i}.parquet")
    teste_preictal = teste_preictal[0 : teste_preictal.shape[0] - tamanho_seq]
