import os
import unicodedata

from settings import ROOT_DIR

def save_file(output_path, names):
  with open(output_path, 'w', encoding='utf-8') as f:
    for name in names:
      f.write('{}\n'.format(name))

def main():
  # ipadic
  path = os.path.join(ROOT_DIR, 'data/dictionaries/ipadic/Noun.org.csv')
  names = set()
  with open(path, 'r', encoding='euc_jp') as f:
    for line in f:
      names.add(line.strip().split(',')[0])

  output_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/ipadic.csv')
  save_file(output_path, names)
  print(f'IPAdic counts: {len(names)}')

  # juman
  """
  cd /Users/smap10/Project/company-name/data/dictionaries/mecab-jumandic-7.0-20130310
  cat *.csv | wc -l
  751185

  cat *.csv | grep 組織名 | wc -l       
  9608

  grep -iRl "組織名" ./*csv 
  ./Auto.csv
  ./ContentW.csv
  ./Noun.koyuu.csv
  ./Rengo.csv
  ./Wikipedia.csv
  """
  file_names = ['Auto.csv', 'ContentW.csv', 'Noun.koyuu.csv', 'Rengo.csv', 'Wikipedia.csv']
  dir_path = os.path.join(ROOT_DIR, 'data/dictionaries/juman')
  file_paths = []
  for file_name in file_names:
    file_paths.append(os.path.join(dir_path, file_name))

  names = set()
  for file_path in file_paths:
    with open(file_path, 'r', encoding='utf-8') as f:
      for line in f:
        if "組織名" in line:
          names.add(line.strip().split(',')[0])

  output_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/juman.csv')
  save_file(output_path, names)
  print(f'Juman counts: {len(names)}')

  # neolody
  """
  cd ~/Project/mecab-ipadic-neologd/build/mecab-ipadic-2.7.0-20070801-neologd-20191202
  cat mecab-user-dict-seed.20191202.csv | grep 組織 | wc -l
  330851

  '組織' only in mecab-user-dict-seed.20191202.csv
  """
  path = os.path.join(ROOT_DIR, 'data/dictionaries/neologd/mecab-user-dict-seed.20191202.csv')
  lines = []
  with open(path, 'r', encoding='utf-8') as f:    
    for line in f:
      if '組織' in line:
        lines.append(line.strip().split(','))

  for line in lines:
    line[0] = unicodedata.normalize('NFKC', line[0])
    if '(株)' in line[0]:    
      line[0] = line[0].replace('(株)', '').strip()
    elif '(有)' in line[0]:
      line[0] = line[0].replace('(有)', '').strip()

  names = set()
  for line in lines:
    names.add(line[0])

  output_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/neologd.csv')
  save_file(output_path, names)
  print(f'NEologd counts: {len(names)}')


  # ipadic-neologd
  path1 = os.path.join(ROOT_DIR, 'data/dictionaries/output/ipadic.csv')
  path2 = os.path.join(ROOT_DIR, 'data/dictionaries/output/neologd.csv')

  names = set()
  with open(path1, 'r', encoding='utf-8') as f:
    for line in f:
      names.add(line.strip())
  with open(path2, 'r', encoding='utf-8') as f:
    for line in f:
      names.add(line.strip())

  output_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/ipadic_neologd.csv')
  save_file(output_path, names)
  print(f'IPAdic-NEologd counts: {len(names)}')
  

  # ipadic-neologd-jcl
  path1 = os.path.join(ROOT_DIR, 'data/dictionaries/output/ipadic_neologd.csv')
  path2 = os.path.join(ROOT_DIR, 'data/dictionaries/output/jcl_medium.csv') 
  names = set()
  with open(path1, 'r', encoding='utf-8') as f:
    for line in f:
      names.add(line.strip())
  with open(path2, 'r', encoding='utf-8') as f:
    for line in f:
      names.add(line.strip())

  output_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/ipadic_neologd_jcl.csv')
  save_file(output_path, names)
  print(f'IPAdic-NEologd counts: {len(names)}') 

if __name__ == "__main__":
  main()