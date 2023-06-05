import logging
import os
from itertools import permutations
from pathlib import Path

import pandas as pd
from tqdm import tqdm


def junta_sequencias(caminho_seqs):
    if (
        len(caminho_seqs) < 2
    ):  # garante que há no mínimo dois tipos de sequências
        return

    tipos = list(map(lambda caminho: caminho.stem, caminho_seqs))
    arquivos = list(map(lambda caminho: os.listdir(caminho), caminho_seqs))
    for lista in arquivos:
        lista.sort()

    base = arquivos[0]
    comuns = []
    for arquivo in base:

        # Checa se o todos os vetores têm essa sequência
        continuar = False
        for lista in arquivos[1:]:
            if arquivo not in lista:
                continuar = True
                break
        if continuar:
            continue
        else:
            comuns.append(arquivo)

    caminho_resultado = Path(list(caminho_seqs[0].parents)[0]) / '-'.join(
        tipos
    )
    caminho_resultado.mkdir(exist_ok=True)

    for nome in tqdm(comuns, desc='Arquivo', leave=False):
        sequencia = []
        for caminho in caminho_seqs:
            seq = pd.read_parquet(caminho / nome)
            sequencia.append(seq.T)
        sequencia = pd.concat(sequencia)
        sequencia.to_parquet(caminho_resultado / nome)


logging.basicConfig(
    format='%(asctime)s - [%(levelname)s] %(message)s',
    level=logging.INFO,
    datefmt='%d/%m/%Y %H:%M:%S',
)

seq_dir = Path('sequencias')
vet_dir = Path('vetores')
janelas_dir = Path('janelas')

possiveis = os.listdir(janelas_dir)
possiveis.sort()

print('Escolha um dos pacientes para criar as sequências:')
for numero, paciente in enumerate(possiveis):
    print(f'[{numero + 1}] - {paciente}')

while True:
    try:
        paciente = (
            int(
                input(
                    'Digite o número dentro dos colchetes ao lado do paciente desejado: '
                )
            )
            - 1
        )
        if paciente > len(possiveis) or paciente < 0:
            print('Número de paciente inválido')
        else:
            break
    except ValueError:
        print('Você deve digitar um número')

while True:
    mistura = input('Você deseja misturar os vetores nas sequências? (s/n) ')
    if mistura not in 'sn':
        print('Você deve digitar "s" ou "n"')
    else:
        break

paciente = str(possiveis[paciente])
quantidades = [15, 30, 45, 60]

# --------------------------- CRIANDO VETORES ------------------------------------
tipos = ['Wavelets', 'Corr']

# Checa se os vetores estão prontos
vetores_prontos = True
for tipo in tipos:
    try:
        quantidade = len(os.listdir(vet_dir / paciente / tipo))
        if quantidade == 0:
            vetores_prontos = False
            break
    except FileNotFoundError:
        vetores_prontos = False
        break

if not vetores_prontos:
    logging.info('Iniciando criação de vetores')
    for tipo in tipos:
        Path(vet_dir / paciente / tipo).mkdir(parents=True, exist_ok=True)
        logging.info(f'Vetores de {tipo}')
        os.system(
            f'python monta_arquivos/montaVets{tipo}.py -e {janelas_dir}/{paciente}'
        )
        for file in Path().glob('*.parquet'):
            os.rename(file, Path.cwd() / vet_dir / paciente / tipo / file)
else:
    logging.info('Vetores já estão prontos.')

# --------------------------- CRIANDO SEQUÊNCIAS ------------------------------------
logging.info('Iniciando criação de sequencias')
for quantidade in quantidades:
    for tipo in tipos:
        Path(seq_dir / paciente / str(quantidade) / tipo).mkdir(
            parents=True, exist_ok=True
        )
        logging.info(f'Sequencias de {tipo} com {quantidade} vetores')
        if mistura == 'n':
            os.system(
                f'python monta_arquivos/cria_sequencias.py -t {vet_dir}/{paciente}/{tipo}/ -s {quantidade} -e n'
            )
        else:
            os.system(
                f'python monta_arquivos/cria_sequencias.py -t {vet_dir}/{paciente}/{tipo}/ -s {quantidade} -e s'
            )

# --------------------------- JUNTANDO SEQUÊNCIAS ------------------------------------
para_juntar = [tipos]
for quantidade in quantidades:
    for junto in para_juntar:
        caminhos = [
            Path(seq_dir / paciente / str(quantidade) / tipo) for tipo in junto
        ]
        logging.info(
            f'Sequencias de {"-".join(junto)} com {quantidade} vetores'
        )
        junta_sequencias(caminhos)
