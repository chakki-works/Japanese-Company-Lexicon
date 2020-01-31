"""
Calculate coverage with specific dictionary and specific dataset
"""
import os
from typing import List
from pathlib import Path
import unicodedata

from ahocorasick import Automaton

from settings import ROOT_DIR

def read_dictionary(dict_path: str) -> dict:
  with open(dict_path, 'r', encoding='utf-8') as f:
    company_dict = {}
    for i, line in enumerate(f, start=1):
      try:
        name = line.strip()
        name = unicodedata.normalize('NFKC', name)
        company_dict[name] = i
      except Exception as e:
        print(e)
        print(line)
  return company_dict

def build_trie(company_dict: dict) -> Automaton:
  trie = Automaton()
  for name, idx in company_dict.items():
    trie.add_word(name, (idx, name))
  return trie

def read_entity(data_path: str) -> list:
  with open(data_path, 'r', encoding='utf-8') as f:
    entities = []
    for line in f:
      name = line.strip()
      name = unicodedata.normalize('NFKC', name)
      entities.append(name) 
  return entities 

def caltulate_coverage(company_trie: Automaton, entities: list) -> float:
  total_number = len(entities)
  counts = 0
  for entity in entities:
    if entity in company_trie:
      counts += 1
  return counts, counts / total_number

def pipeline(dict_path: str):
  """run coverage calculation pipeline"""
  dict_path = Path(dict_path)
  dict_name = dict_path.stem

  company_dict = read_dictionary(dict_path)
  company_trie = build_trie(company_dict) 

  mainichi_path = os.path.join(ROOT_DIR, 'data/corpora/output/mainichi_names.csv')
  bccwj_path = os.path.join(ROOT_DIR, 'data/corpora/output/bccwj_names.csv')

  # uncomment below paths to run the duplicate coverage calculation
  # mainichi_path = os.path.join(ROOT_DIR, 'data/corpora/output/mainichi_names_duplicates.csv')
  # bccwj_path = os.path.join(ROOT_DIR, 'data/corpora/output/bccwj_names_duplicates.csv')

  for data_path in [mainichi_path, bccwj_path]:
    data_path = Path(data_path)
    data_name = data_path.stem

    entities = read_entity(data_path)
    counts, coverage = caltulate_coverage(company_trie, entities)
    print('Dict is: {} (has {} words)'.format(dict_name, len(company_trie)))
    print('Data is: {} (has {} entities)'.format(data_name, len(entities)))
    print('Counts is: {}'.format(counts))
    print('Coverage is: {}'.format(coverage))
    print()


if __name__ == "__main__":
  # ipic
  dict_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/ipadic.csv')
  pipeline(dict_path)

  # juman
  dict_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/juman.csv')
  pipeline(dict_path)

  # neologd
  dict_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/neologd.csv')
  pipeline(dict_path) 

  # ipaidc-neogody
  dict_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/ipadic_neologd.csv')
  pipeline(dict_path) 

  # jcl_slim
  dict_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/jcl_slim.csv')
  pipeline(dict_path)

  # jcl_medium
  dict_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/jcl_medium.csv')
  pipeline(dict_path)

  # jcl_full
  dict_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/jcl_full.csv')
  pipeline(dict_path)

  # ipadic-neologd-jcl(medium)
  dict_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/ipadic_neologd_jcl.csv')
  pipeline(dict_path)

  