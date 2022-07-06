import logging
import os

ARQUIVO = __file__
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%d/%m/%Y %H:%M:%S",
)

os.chdir("janelas")
possiveis = os.listdir()
possiveis.sort()
# -------------------- RECEBENDO AS ENTRADAS ------------------------------------
print("Escolha um dos tipos de janelas criadas para criar as sequências:")
for numero, paciente in enumerate(possiveis):
    print(f"[{numero + 1}] - {paciente}")

while True:
    try:
        paciente = (
            int(
                input("Digite o número dentro dos colchetes ao lado do tipo desejado: ")
            )
            - 1
        )
        if paciente > len(possiveis) or paciente < 0:
            print("Número de paciente inválido")
        else:
            break
    except ValueError:
        print("Você deve digitar um número")

os.chdir(possiveis[paciente])
if possiveis[paciente] == "novo":
    seq_dir = "sequencias_novo"
    vet_dir = "vetores_novo"
    janelas_dir = "novo"
else:
    seq_dir = "sequencias"
    vet_dir = "vetores"
    janelas_dir = "antigo"

possiveis = os.listdir()
possiveis.sort()

print("Escolha um dos pacientes para criar as sequências:")
for numero, paciente in enumerate(possiveis):
    print(f"[{numero + 1}] - {paciente}")

while True:
    try:
        paciente = (
            int(
                input(
                    "Digite o número dentro dos colchetes ao lado do paciente desejado: "
                )
            )
            - 1
        )
        if paciente > len(possiveis) or paciente < 0:
            print("Número de paciente inválido")
        else:
            break
    except ValueError:
        print("Você deve digitar um número")

paciente = possiveis[paciente]

while True:
    try:
        quantidade = int(
            input(
                "Digite a quantidade de vetores por sequência de vetores para a LSTM: "
            )
        )
        if quantidade >= 2:
            break
    except ValueError:
        print("Você deve digitar um número")

# --------------------------- CRIANDO VETORES ------------------------------------
os.chdir("../..")
tipos = ["FFT", "Estatisticos", "Grafos", "Wavelets"]
logging.info("Iniciando criação de vetores")
print(os.getcwd())
for tipo in tipos:
    if not os.path.exists(f"{vet_dir}/{paciente}/{tipo}"):
        os.makedirs(f"{vet_dir}/{paciente}/{tipo}")
    logging.info(f"Vetores de {tipo}")
    if len(os.listdir(f"{vet_dir}/{paciente}/{tipo}")) == 0:
        os.system(
            f"python monta_vetores/montaVets{tipo}.py -e janelas/{janelas_dir}/{paciente}/"
        )
        for file in os.listdir():
            if file.endswith(".txt"):
                os.rename(file, os.path.join(vet_dir, paciente, tipo, file))

logging.info("Ajustando correlações e grafos")
os.chdir(os.path.join("vetores", paciente, "Grafos"))
if not os.path.exists(os.path.join("..", "Correlacao")):
    os.mkdir(os.path.join("..", "Correlacao"))
for file in os.listdir():
    if file.startswith("corr"):
        os.rename(file, os.path.join("..", "Correlacao", file))

tipos.append("Correlacao")

os.chdir("../../..")
logging.info("Iniciando criação de sequencias")
for tipo in tipos:
    if not os.path.exists(f"{seq_dir}/{paciente}/{quantidade}/{tipo}"):
        os.makedirs(f"{seq_dir}/{paciente}/{quantidade}/{tipo}")
    logging.info(f"Sequencias de {tipo} com {quantidade} vetores")
    os.system(
        f"python monta_vetores/cria_sequencias.py -t {vet_dir}/{paciente}/{tipo}/ -s {quantidade}"
    )
    for file in os.listdir():
        if file.endswith(".txt"):
            os.rename(
                file, os.path.join(seq_dir, paciente, str(quantidade), tipo, file)
            )
