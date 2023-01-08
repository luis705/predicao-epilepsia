import os
import sys
import tarfile

import numpy as np
from tqdm import tqdm

def uso():
    print('Uso do programa:')
    print(f'\tpython {sys.argv[0]}  <tipo1> <tipo2> ... <tipon>\n')
    print(f'\tExemplo: {sys.argv[0]} Correlacao Grafos')

try:
    _, *nomes = sys.argv
    assert(len(nomes) >= 1)
except AssertionError: 
    uso()
    exit()
    
pacientes = os.listdir()
pacientes.remove('junta_sequencias.py')
tempos = ['antigo', 'novo']
quantidades = [str(i) for i in range(15, 61, 15)]


raiz = os.getcwd()
for paciente in tqdm(pacientes, desc='Pacientes'):
    for tempo in tqdm(tempos, leave=False, desc='Tempo'):
        for quantidade in quantidades:
            sequencias = {}
            os.chdir(os.path.join(paciente, tempo, quantidade))
            for nome in tqdm(nomes, leave=False, desc='Lendo nomes dos arquivos sequências'):
                # Primeiro extrai os arquivos .tar.gz
                
                sequencias[nome] = []
                with tarfile.open(nome + ".tar.gz", "r:gz") as tar:
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
                        
                    
                    safe_extract(tar)
                
                # Em seguida pega os nomes dos arquivos de sequência
                os.chdir(nome)
                arquivos = os.listdir()
                arquivos.sort()
                for arquivo in arquivos:
                    sequencias[nome].append(arquivo)
                os.chdir('..')
            
            base = sequencias[nomes[0]]
            # Apenas salva sequências que há de todos os tipos
            # Ex.: caso haja interictal 123 de Correlação
            # Mas não de Grafos a sequência interictal 123 é removida
            for arquivo in tqdm(base, leave=False, desc='Validando nomes dos arquivos de sequências'):
                for nome in nomes[1:]:
                    if arquivo not in sequencias[nome]:
                        base.remove(arquivo)
            
            # Cria sequências finais ao adicionar uma sequência na outra
            resultado = []
            for arquivo in tqdm(base, leave=False, desc='Juntando sequências dos tipos ' + ' '.join(nomes)):
                primeiro = True
                for nome in nomes:
                    if primeiro:
                        adicionar = np.loadtxt(os.path.join(nome, arquivo))
                        primeiro = False
                    else:
                        adicionar = np.append(adicionar, np.loadtxt(os.path.join(nome, arquivo)), axis=1)
                resultado.append(adicionar)
            
            
            # Salva sequências finais no destino correto
            destino = '-'.join(nomes)
            if not os.path.exists(destino):
                os.mkdir(destino)
            for r, arquivo in tqdm(zip(resultado, base), leave=False, desc='Salvando sequências criadas'):
                np.savetxt(os.path.join(destino, arquivo), r)
            
            with tarfile.open(destino + '.tar.gz', "w:gz") as tar:
                tar.add(destino, arcname=os.path.basename(destino))
            for file in tqdm(os.listdir(), leave=False, desc='Removendo arquivos desnecessários'):
                if not file.endswith('.tar.gz'):
                    os.system(f'rm -rf {file}')
            os.chdir(raiz)
