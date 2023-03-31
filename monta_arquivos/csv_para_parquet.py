import os
import pandas as pd

from tqdm import tqdm

dir_path = os.path.join('..', 'sinais', 'chb03')
for file in tqdm(os.listdir(dir_path)):
    if file.endswith('parquet'):
        continue
    out_file = os.path.join(dir_path, file[:-3] + 'parquet.gzip')
    in_file = os.path.join(dir_path, file)
    try:
        pd.read_csv(in_file, sep=',').to_parquet(out_file, index=False, compression='gzip')
    except pd.errors.EmptyDataError:
        print(file)
    os.remove(in_file)
