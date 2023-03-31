import logging
import os
import shutil
from pathlib import Path

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

paciente = str(possiveis[paciente])
quantidades = [15, 30, 45, 60]

# --------------------------- CRIANDO VETORES ------------------------------------
tipos = ['Corr', 'Wavelets']
logging.info('Iniciando criação de janelas')

for tipo in tipos:
    if not os.path.exists(f'{vet_dir}/{paciente}/{tipo}'):
        os.makedirs(f'{vet_dir}/{paciente}/{tipo}')
    logging.info(f'Vetores de {tipo}')
    os.system(
        f'python monta_arquivos/montaVets{tipo}.py -e {janelas_dir}/{paciente}/'
    )
    for file in os.listdir():
        if file.endswith('.parquet'):
            os.rename(file, Path.cwd() / vet_dir / paciente / tipo / file)

logging.info('Iniciando criação de sequencias')
for quantidade in quantidades:
    for tipo in tipos:
        if not os.path.exists(f'{seq_dir}/{paciente}/{quantidade}/{tipo}'):
            os.makedirs(f'{seq_dir}/{paciente}/{quantidade}/{tipo}')
        logging.info(f'Sequencias de {tipo} com {quantidade} janelas')
        os.system(
            f'python monta_arquivos/cria_sequencias.py -t {vet_dir}/{paciente}/{tipo}/ -s {quantidade}'
        )
        for file in os.listdir():
            if file.endswith('.parquet'):
                os.rename(
                    file,
                    os.path.join(
                        seq_dir, paciente, str(quantidade), tipo, file
                    ),
                )
