import os
import sys

import pandas as pd
from tqdm import tqdm

if len(sys.argv) < 2:
    assert False, (
        'Você deve passar ao menos uma opção,'
        ' utilize a opção -h para obter ajuda'
    )
elif sys.argv[1] == '-h':
    arquivo = __file__.split('/')[-1]
    print(
        f"{arquivo}: ajustes finos aos CSV's dos EEG's gerados pelo EDFBrowser"
    )
    print('Uso:')
    print(f'    python {arquivo} <opção> <argumento>')
    print('    Opções:')
    print('        -h: mostra essa mensagem')
    print('        -d: executa programa')
    print(
        '            argumento obrigatório: diretório contendo arquivos gerados pelo EDFBrowser'
    )
    sys.exit(0)
elif sys.argv[1] == '-d':
    diretorio = sys.argv[2]
else:
    assert (
        False
    ), f'Opção {sys.argv[1]} inválida, utilize a opção -h para obter ajuda'

os.chdir(diretorio)
for file in tqdm(os.listdir()):
    if 'data' in file:
        df = pd.read_csv(file)
        try:
            del df['Time']
        except KeyError:
            ...
        for coluna in range(19, 24):
            try:
                del df[str(coluna)]  # remove canais desnecessários
            except KeyError:
                continue
        df.to_csv(file, index=False)
    else:
        os.remove(file)
