import os
from pathlib import Path

primeiro_paciente = 2
ultimo_paciente = 2
tsiouris = False
recomendado = True
tipos = ['Corr', 'Wavelets', 'Wavelets-Corr']
sequencias = [15, 30, 45, 60]

pacientes = list(
    map(lambda i: f'CHB{i:02}', range(primeiro_paciente, ultimo_paciente + 1))
)

if not (tsiouris or recomendado):
    exit()

for paciente in pacientes:
    for sequencia in sequencias:
        for tipo in tipos:
            pasta = os.path.join(
                '..', 'sequencias', paciente, str(sequencia), tipo
            )
            Path('..', 'Resultados', paciente, tipo).mkdir(
                exist_ok=True, parents=True
            )
            Path('..', 'Gráficos', paciente, tipo).mkdir(
                exist_ok=True, parents=True
            )
            if tsiouris:
                print(f'python lstm_novo.py -e {pasta} -t')
                os.system(f'python lstm_novo.py -e {pasta} -t')
            if recomendado:
                print(f'python lstm_novo.py -e {pasta}')
                os.system(f'python lstm_novo.py -e {pasta}')
