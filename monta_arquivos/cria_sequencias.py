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
import logging
import sys
from pathlib import Path
from random import shuffle

import pandas as pd
from tqdm import tqdm


def recebe_argumentos():
    optlist, args = getopt.gnu_getopt(sys.argv[1:], 't:s:e:')
    for (opcao, argumento) in optlist:
        if opcao == '-t':
            nome_dir_dados = argumento
        if opcao == '-s':
            tamanho_seq = int(argumento)
        if opcao == '-e':
            if argumento == 's':
                embaralha = True
            else:
                embaralha = False
    try:
        return nome_dir_dados, tamanho_seq, embaralha
    except ValueError:
        exit()


def encontra_arquivos(diretorio):
    treino_interictal = {}
    treino_preictal = {}
    teste_interictal = {}
    teste_preictal = {}

    for arquivo in diretorio.iterdir():
        nome_arquivo = arquivo.stem.lower()
        crise = int(nome_arquivo.split('_')[-1])

        if 'treino' in nome_arquivo and 'inter' in nome_arquivo:
            if crise in treino_interictal:
                treino_interictal[crise].append(arquivo)
            else:
                treino_interictal[crise] = [arquivo]
        elif 'treino' in nome_arquivo and 'pre' in nome_arquivo:
            if crise in treino_preictal:
                treino_preictal[crise].append(arquivo)
            else:
                treino_preictal[crise] = [arquivo]
        elif 'teste' in nome_arquivo and 'inter' in nome_arquivo:
            if crise in teste_interictal:
                teste_interictal[crise].append(arquivo)
            else:
                teste_interictal[crise] = [arquivo]
        elif 'teste' in nome_arquivo and 'pre' in nome_arquivo:
            if crise in teste_preictal:
                teste_preictal[crise].append(arquivo)
            else:
                teste_preictal[crise] = [arquivo]

    return {
        'treino_interictal': treino_interictal,
        'treino_preictal': treino_preictal,
        'teste_interictal': teste_interictal,
        'teste_preictal': teste_preictal,
    }


def cria_sequencias_crise(
    arquivos,
    tamanho_seq,
    pasta_resultado,
    crise,
    treino=False,
    interictal=False,
    embaralha=False,
):
    # Ordena lista de sequências, garante que
    # sequencias serão formadas com vetores
    # adjacentes
    if embaralha:
        shuffle(arquivos)
    else:
        arquivos.sort(key=lambda caminho: caminho.stem)

    for ind_sequencia in tqdm(
        range(len(arquivos) // tamanho_seq),
        desc=f'Sequência',
        leave=False,
    ):

        # Calcula o nome do arquivos de saída
        if treino and interictal:
            arq_resultado = (
                f'treino_interictal_crise_{crise}_seq_{ind_sequencia}.parquet'
            )
        elif treino and not interictal:
            arq_resultado = (
                f'treino_preictal_crise_{crise}_seq_{ind_sequencia}.parquet'
            )
        elif not treino and interictal:
            arq_resultado = (
                f'teste_interictal_crise_{crise}_seq_{ind_sequencia}.parquet'
            )
        elif not treino and not interictal:
            arq_resultado = (
                f'teste_preictal_crise_{crise}_seq_{ind_sequencia}.parquet'
            )

        sequencia = []

        # Lê os arquivos de vetores:
        for arquivo in arquivos[:tamanho_seq]:
            sequencia.append(pd.read_parquet(arquivo).to_numpy().T[0])

        # Salva a sequencia
        try:
            sequencia = pd.DataFrame(
                sequencia, columns=[str(i) for i in range(len(sequencia[0]))]
            )
            sequencia.to_parquet(pasta_resultado / arq_resultado)

        except ValueError as e:
            # Sequência com vetores de tamanhos diferentes
            # neste caso, por algum motivo algum vetor foi
            # criado de forma errada, assim apenas ignoramos
            # a sequência
            continue

        # Remove `tamanho_seq` primeiros elementos da lista de vetores
        arquivos = arquivos[tamanho_seq:]


def cria_sequencias_tipo(
    dict_crises,
    tamanho_seq,
    pasta_resultado,
    treino=False,
    interictal=False,
    embaralha=False,
):
    for crise, arquivos in tqdm(
        dict_crises.items(), desc=f'Crise', leave=False
    ):
        cria_sequencias_crise(
            arquivos,
            tamanho_seq,
            pasta_resultado,
            crise,
            treino,
            interictal,
            embaralha,
        )


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - [%(levelname)s] %(message)s',
        level=logging.INFO,
        datefmt='%d/%m/%Y %H:%M:%S',
    )
    nome_dir_dados, tamanho_seq, embaralha = recebe_argumentos()
    nome_dir_dados = Path(nome_dir_dados)
    dicts_vetores = encontra_arquivos(nome_dir_dados)

    # Encontra caminho onde as sequências devem ser armazenadas
    tipo_vetor = nome_dir_dados.stem
    paciente = nome_dir_dados.parents[0].stem
    pasta_resultado = Path(
        'sequencias', paciente, str(tamanho_seq), tipo_vetor
    )
    pasta_resultado.mkdir(exist_ok=True)

    logging.info('Sequências de treino interictal')
    cria_sequencias_tipo(
        dicts_vetores['treino_interictal'],
        tamanho_seq,
        pasta_resultado,
        treino=True,
        interictal=True,
        embaralha=embaralha,
    )
    logging.info('Sequências de treino preictal')
    cria_sequencias_tipo(
        dicts_vetores['treino_preictal'],
        tamanho_seq,
        pasta_resultado,
        treino=True,
        interictal=False,
        embaralha=embaralha,
    )
    logging.info('Sequências de teste interictal')
    cria_sequencias_tipo(
        dicts_vetores['teste_interictal'],
        tamanho_seq,
        pasta_resultado,
        treino=False,
        interictal=True,
        embaralha=embaralha,
    )
    logging.info('Sequências de teste preictal')
    cria_sequencias_tipo(
        dicts_vetores['teste_preictal'],
        tamanho_seq,
        pasta_resultado,
        treino=False,
        interictal=False,
        embaralha=embaralha,
    )
