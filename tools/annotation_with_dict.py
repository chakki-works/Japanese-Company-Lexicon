"""
Calculate coverage with specific dictionary and specific dataset
"""
import os
import unicodedata
from typing import List
from pathlib import Path
from collections import defaultdict

from ahocorasick import Automaton
from dataset_preprocess import load_data_and_labels

from settings import ROOT_DIR

def read_dictionary(dict_path: str) -> dict:
  with open(dict_path, 'r', encoding='utf-8') as f:
    company_dict = {}
    for i, line in enumerate(f, start=1):
      try:
        name = line.strip()
        company_dict[name] = i
      except Exception as e:
        print(e)
        print(line)
  return company_dict

def build_trie(company_dict: dict) -> Automaton:
  trie = Automaton()
  for name, idx in company_dict.items():
    trie.add_word(name, (idx, name))
  trie.make_automaton()
  return trie

def read_bio(data_path: str) -> list:
  return load_data_and_labels(data_path)

def filter_chunks(chunks: list) -> list:
  chunks = sorted(chunks)
  # same start but for longest match
  dic = defaultdict(list)
  last_chunk = chunks[0]
  for chunk in chunks:
      start_idx = chunk[0]
      end_idx = chunk[1]
      if start_idx not in dic:
          # [131, 139, 'ジャパンエナジー'], [133, 134, 'パ']     
          if last_chunk[0] <= start_idx and last_chunk[1] >= end_idx:   
              continue
          else: # [48, 53, '愛知学泉大']
              dic[start_idx] = chunk
      else: # [131, 135, 'ジャパン'], [131, 139, 'ジャパンエナジー']
          if dic[start_idx][1] < chunk[1]:
              dic[start_idx] = chunk
              last_chunk = chunk

  # same end but for longest match
  chunks = dic.values()
  dic = defaultdict(list)
  for chunk in chunks:
      end_idx = chunk[1]
      if end_idx not in dic:
          dic[end_idx] = chunk
      else:
          if dic[end_idx][0] > chunk[0]:
              dic[end_idx] = chunk
  return list(dic.values())

def tag_with_dict(company_trie: Automaton, sents: list) -> float:
  sent_tags = []
  sent_text = []
  for sent in sents:
    text = ''.join(sent).strip()
    text = unicodedata.normalize('NFKC', text)
    chunks = []
    tags = ['O'] * len(text)
    # find all chunks
    for idx, (_, w) in company_trie.iter(text):
      end_idx = idx + 1
      start_idx = end_idx - len(w)
      chunks.append([start_idx, end_idx, w]) # [[48, 53, '愛知学泉大'], [122, 130, 'シャンソン化粧品'], [131, 135, 'ジャパン'], [131, 139, 'ジャパンエナジー'], [133, 134, 'パ'], [140, 144, '第一勧銀']]
    # find chunks
    if len(chunks) != 0:
      # filter chunks
      chunks = filter_chunks(chunks) # [[122, 130, 'シャンソン化粧品'], [131, 139, 'ジャパンエナジー'], [140, 144, '第一勧銀']]
      # generate labels
      for chunk in chunks:
          start_idx, end_idx = chunk[0], chunk[1]
          for tag_idx in range(start_idx, end_idx):
              if tag_idx == start_idx:
                  tags[tag_idx] = 'B-company'
              else:
                  tags[tag_idx] = 'I-company'
    sent_tags.append(tags)
    sent_text.append([x for x in text]) 
  return sent_tags, sent_text

def save_bio(path, sents, tags): 
  with open(path, 'w', encoding='utf-8') as f:
    for idx in range(len(sents)):
      sent = sents[idx]
      tag = tags[idx]
      for char, tag in zip(sent, tag):
          f.write('{}\t{}\n'.format(char, tag))
      f.write('\n')

def pipeline(dict_path: str):
  """Annotation pipeline
  
  1. read dict and build trie
  2. read two data set
  3. tag two data set with dict for longest match
  4. output bio format tagged file
  """
  # 1. read dict and build trie 
  dict_path = Path(dict_path)
  dict_name = dict_path.stem

  company_dict = read_dictionary(dict_path)
  company_trie = build_trie(company_dict) 

  # 2. read two datasets
  mainichi_path = os.path.join(ROOT_DIR, 'data/corpora/output/mainichi.bio')
  bccwj_path = os.path.join(ROOT_DIR, 'data/corpora/output/bccwj.bio') 
  
  for data_path in [mainichi_path, bccwj_path]:
    data_path = Path(data_path)
    data_name = data_path.stem
    sents, glod_labels = read_bio(data_path)

    # 3. tag two data set with dict for longest match
    tag_labels, sent_text = tag_with_dict(company_trie, sents)

    # 4. Save tagged dataset
    save_file_name = data_path.stem + '_' + dict_path.stem + '_tagged.bio'
    save_file_path = data_path.parent.joinpath(save_file_name)
    save_bio(save_file_path, sent_text, tag_labels) 

    print('Dict is: {} (has {} words)'.format(dict_name, len(company_trie)))
    print('Data is: {} (has {} sentences)'.format(data_name, len(sents)))
    print('Save file as: {}'.format(save_file_name))
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

  # ipaidc_neogody
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

  # ipaidc_neogody_jcl
  dict_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/ipadic_neologd_jcl.csv')
  pipeline(dict_path)


  


