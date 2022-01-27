import os
import re
import concurrent.futures

import mne
import numpy as np
import pandas as pd
from tqdm import tqdm

def converte_um_arq(entrada, caminho_paciente_saida, saida):
    raw = mne.io.read_raw_edf(
            entrada,
            exclude=["P7-T7", "T7-FT9", "FT9-FT10", "FT10-T8", "VNS"],
            verbose="CRITICAL",
        )
    df = pd.DataFrame(data=raw.get_data().T, columns=raw.ch_names)
    df.drop("T8-P8-1", axis=1, inplace=True)
    df.rename(columns={"# FP1-F7": "FP1-F7", "T8-P8-0": "T8-P8"}, inplace=True)
    df.to_csv(os.path.join(caminho_paciente_saida, saida), index=False)


caminho_entrada = os.path.join("physionet.org", "files", "chbmit", "1.0.0")
caminho_saida = os.path.join("data")

pacientes = [1]
for j in tqdm(pacientes, desc="Paciente"):
    caminho_paciente = os.path.join(caminho_entrada, f"chb{j:02}")
    caminho_paciente_saida = os.path.join(caminho_saida, f"Paciente {j:02}")
    if not os.path.exists(caminho_paciente_saida):
        os.makedirs(f"{caminho_saida}/Paciente {j:02}")
    
    

    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Ajustando variáveis necessárias
        arquivos = list(filter(lambda x: x.endswith(".edf"), os.listdir(caminho_paciente)))
        entradas = [os.path.join(caminho_paciente, arquivo) for arquivo in arquivos]
        saidas = [re.sub(f'chb{j:02}' + r'\_', '', string=arquivo) for arquivo in arquivos]
        saidas = [re.sub('.edf', '.csv', string=saida) for saida in saidas]

        [executor.submit(converte_um_arq, entradas[i], caminho_paciente_saida, saidas[i]) for i in range(len(arquivos))]
