import logging
import os
import tarfile

from tqdm import tqdm

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
        tempo = (
            int(
                input("Digite o número dentro dos colchetes ao lado do tipo desejado: ")
            )
            - 1
        )
        if tempo > len(possiveis) or tempo < 0:
            print("Número de paciente inválido")
        else:
            break
    except ValueError:
        print("Você deve digitar um número")

os.chdir(possiveis[tempo])
if possiveis[tempo] == "novo":
    janelas_dir = "novo"
else:
    janelas_dir = "antigo"
if tempo == 0:
    tempo = "antigo"
else:
    tempo = "novo"
seq_dir = "sequencias"
vet_dir = "vetores"

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
quantidades = [15, 30, 45, 60]


# --------------------------- CRIANDO VETORES ------------------------------------
os.chdir("../..")
logging.info("Extraindo diretório de janelas")
with tarfile.open(os.path.join("janelas", janelas_dir, paciente), "r:gz") as tar:
    tar.extractall(os.path.join("janelas", janelas_dir))
paciente = paciente[:-7]

#tipos = ["FFT", "Grafos"]
tipos = ["FFT", "Wavelets", "Grafos"]
logging.info("Iniciando criação de vetores")

for arquivo in os.listdir(f'janelas/{janelas_dir}/{paciente}/'):
    if os.path.getsize(os.path.join(f'janelas/{janelas_dir}/{paciente}/', arquivo)) == 0:
        os.remove(os.path.join(f'janelas/{janelas_dir}/{paciente}/', arquivo))

for tipo in tipos:
    if not os.path.exists(f"{vet_dir}/{paciente}/{tempo}/{tipo}"):
        os.makedirs(f"{vet_dir}/{paciente}/{tempo}/{tipo}")
    logging.info(f"Vetores de {tipo}")
    if len(os.listdir(f"{vet_dir}/{paciente}/{tempo}/{tipo}")) != -1:
        os.system(
            f"python monta_arquivos/montaVets{tipo}.py -e janelas/{janelas_dir}/{paciente}/"
        )
        for file in os.listdir():
            if file.endswith(".txt"):
                os.rename(file, os.path.join(os.getcwd(), vet_dir, paciente, tempo, tipo, file))

logging.info("Ajustando correlações e grafos")
if not os.path.exists(os.path.join("vetores", paciente, tempo, "Grafos")):
    os.makedirs(os.path.join("vetores", paciente, tempo, "Grafos"))
if not os.path.exists(os.path.join("vetores", paciente, tempo, "Grafos")):
    os.makedirs(os.path.join("vetores", paciente, tempo, "Correlacao"))
os.chdir(os.path.join("vetores", paciente, tempo, "Grafos"))
if not os.path.exists(os.path.join("..", "Correlacao")):
    os.mkdir(os.path.join("..", "Correlacao"))
for file in os.listdir():
    if file.startswith("corr"):
        os.rename(file, os.path.join("..", "Correlacao", file))

tipos.append("Correlacao")

#print(os.getcwd())
os.chdir("../../../../")
logging.info("Iniciando criação de sequencias")
for quantidade in quantidades:
    for tipo in tipos:
        if not os.path.exists(f"{seq_dir}/{paciente}/{tempo}/{quantidade}/{tipo}"):
            os.makedirs(f"{seq_dir}/{paciente}/{tempo}/{quantidade}/{tipo}")
        logging.info(f"Sequencias de {tipo} com {quantidade} vetores")
        print(f"python monta_arquivos/cria_sequencias.py -t {vet_dir}/{paciente}/{tempo}/{tipo}/ -s {quantidade}")
        os.system(
            f"python monta_arquivos/cria_sequencias.py -t {vet_dir}/{paciente}/{tempo}/{tipo}/ -s {quantidade}"
        )
        for file in os.listdir():
            if file.endswith(".txt"):
                os.rename(
                    file,
                    os.path.join(seq_dir, paciente, tempo, str(quantidade), tipo, file),
                )
os.system(f'rm -rf {os.path.join("janelas", janelas_dir, paciente)}')
