"""
Uso no anaconda:
    python3 cria_sequencias_Tsiouris.py -t diretorio_dos_arquivos_fft -n n_de_vetores
    O diretório dos arquivos é o caminho completo para o diretório que
    contém os arquivos de FFT. Esses arquivos devem ter "Interictal" ou
    "PreIctal" no nome.
    n__de_vetores é o número de vetores por sequência, o Pires usou 30
    então acho legal usarmos esse número também.
    Cuidado: as sequências criadas vão estar na pasta que está esse programa
    (cria-Sequencias_Tsiouris) então se tiver alguma sequência nela tire antes
    de executar para que não sejam sobrescritas.

"""

import getopt
import os
import sys

import numpy as np
from tqdm import tqdm

optlist, args = getopt.gnu_getopt(sys.argv[1:], "t:n:")
for (opcao, argumento) in optlist:
    if opcao == "-t":
        nomeDirDados = argumento

treino_interictal = []
treino_preictal = []

for file in tqdm(os.listdir(nomeDirDados)):
    if "Interictal" in file:
        vetor = np.loadtxt(os.path.join(nomeDirDados, file))
        if np.any(np.isnan(vetor)):
            continue
        # print(f'Vetor de interictal: {vetor}')
        treino_interictal.append(vetor)
    elif "PreIctal" in file:
        vetor = np.loadtxt(os.path.join(nomeDirDados, file))
        if np.any(np.isnan(vetor)):
            continue
        # print(f'Vetor de preictal: {vetor}')
        treino_preictal.append(vetor)

treino_interictal = np.array(treino_interictal)
treino_preictal = np.array(treino_preictal)

np.random.shuffle(treino_interictal)
np.random.shuffle(treino_preictal)

for i in range(len(treino_interictal) // 30):
    np.savetxt(
        f"seqInterictal{i}.txt",
        treino_interictal[treino_interictal.shape[0] - 30 :],
    )
    treino_interictal = treino_interictal[0 : treino_interictal.shape[0] - 30]

for i in range(len(treino_preictal) // 30):
    np.savetxt(
        f"seqPreictal{i}.txt", treino_preictal[treino_preictal.shape[0] - 30 :]
    )
    treino_preictal = treino_preictal[0 : treino_preictal.shape[0] - 30]
