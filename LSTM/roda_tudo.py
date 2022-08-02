import os
import tarfile

redes = ["LSTM_recomendado.py", "LSTM_Tsiouris.py"]
pacientes = list(map(lambda i: f"CHB{i:02}", range(1, 12)))
tipos = ["Correlacao", "Grafos"]
sequencias = [15, 30, 45, 60]
tempos = ["antigo", "novo"]

for paciente in pacientes:
    for tempo in tempos:
        for sequencia in sequencias:
            for tipo in tipos:
                for rede in redes:
                    pasta = os.path.join(
                        "..", "sequencias", paciente, tempo, str(sequencia), tipo
                    )
                    with tarfile.open(pasta + ".tar.gz", "r:gz") as tar:
                        tar.extractall("/".join(pasta.split("/")[:-1]))
                    print(rede, pasta)
                    os.system(f"python {rede} -e {pasta}")
                    os.system(f"rm -rf {pasta}")
