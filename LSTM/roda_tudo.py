import os
import tarfile

redes = ["LSTM_recomendado.py", "LSTM_Tsiouris.py"]
pacientes = list(map(lambda i: f"CHB{i:02}", range(4, 12)))
tipos = ['Correlacao', 'Grafos', 'FFT', 'Wavelets']
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
                    print(f"python {rede} -e {pasta}")
                    if not os.path.exists(os.path.join("..", "Resultados", tempo, paciente, tipo)):
                        os.makedirs(os.path.join("..", "Resultados", tempo, paciente, tipo))
                    if not os.path.exists(os.path.join("..", "Gráficos", tempo, paciente, tipo)):
                        os.makedirs(os.path.join("..", "Gráficos", tempo, paciente, tipo))
                    try:
                        with tarfile.open(pasta + ".tar.gz", "r:gz") as tar:
                            def is_within_directory(directory, target):
                                
                                abs_directory = os.path.abspath(directory)
                                abs_target = os.path.abspath(target)
                            
                                prefix = os.path.commonprefix([abs_directory, abs_target])
                                
                                return prefix == abs_directory
                            
                            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                            
                                for member in tar.getmembers():
                                    member_path = os.path.join(path, member.name)
                                    if not is_within_directory(path, member_path):
                                        raise Exception("Attempted Path Traversal in Tar File")
                            
                                tar.extractall(path, members, numeric_owner) 
                                
                            
                            safe_extract(tar, "/".join(pasta.split("/")[:-"1"]))
                        os.system(f"python {rede} -e {pasta}")
                        os.system(f"rm -rf {pasta}")
                    except (tarfile.ReadError, FileNotFoundError):
                        os.system(f"python {rede} -e {pasta}")
                    
                    
