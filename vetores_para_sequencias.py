import logging
import os

logging.basicConfig(
    format='%(asctime)s - [%(levelname)s] %(message)s',
    level=logging.INFO,
    datefmt='%d/%m/%Y %H:%M:%S',
)

quantidades = [15, 30, 45, 60]
tipos = ['FFT', 'Wavelets', 'Grafos', 'Correlacao']
seq_dir = 'sequencias'
vet_dir = 'janelas'
pacientes = list(map(lambda i: f'CHB{i:02}', range(1, 12)))
tempos = ['antigo', 'novo']

for paciente in pacientes:
    for tempo in tempos:
        for quantidade in quantidades:
            for tipo in tipos:
                if not os.path.exists(
                    f'{seq_dir}/{paciente}/{tempo}/{quantidade}/{tipo}'
                ):
                    os.makedirs(
                        f'{seq_dir}/{paciente}/{tempo}/{quantidade}/{tipo}'
                    )
                logging.info(
                    f'Sequencias de {tipo} com {quantidade} janelas do paciente {paciente}'
                )
                os.system(
                    f'python monta_arquivos/cria_sequencias.py -t {vet_dir}/{paciente}/{tempo}/{tipo}/ -s {quantidade}'
                )
                for file in os.listdir():
                    if file.endswith('.txt'):
                        os.rename(
                            file,
                            os.path.join(
                                seq_dir,
                                paciente,
                                tempo,
                                str(quantidade),
                                tipo,
                                file,
                            ),
                        )
