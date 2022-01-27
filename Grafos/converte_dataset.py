import os
import re

import mne
import numpy as np
import pandas as pd
from tqdm import tqdm

caminho_entrada = os.path.join("physionet.org", "files", "chbmit", "1.0.0")
caminho_saida = os.path.join("data")


for j in tqdm([1], desc="Paciente"):
    caminho_paciente = os.path.join(caminho_entrada, f"chb{j:02}")

    if not os.path.exists(f"{caminho_saida}/Paciente {j:02}"):
        os.makedirs(f"{caminho_saida}/Paciente {j:02}")
        caminho_paciente_saida = os.path.join(caminho_saida, f"Paciente {j:02}")

    for arquivo in tqdm(
        list(filter(lambda x: x.endswith(".edf"), os.listdir(caminho_paciente))),
        desc="Arquivos",
        leave=False,
    ):
        find = f"chb{j:02}" + r"\_"
        saida = re.sub(find, "", string=arquivo)
        saida = re.sub(".edf", ".csv", string=saida)
        entrada = os.path.join(caminho_paciente, arquivo)

        raw = mne.io.read_raw_edf(
            entrada,
            exclude=["P7-T7", "T7-FT9", "FT9-FT10", "FT10-T8", "VNS"],
            verbose="CRITICAL",
        )
        df = pd.DataFrame(data=raw.get_data().T, columns=raw.ch_names)
        df.drop("T8-P8-1", axis=1, inplace=True)
        df.rename(columns={"# FP1-F7": "FP1-F7", "T8-P8-0": "T8-P8"}, inplace=True)
        df.to_csv(os.path.join(caminho_paciente_saida, saida), index=False)

        del raw