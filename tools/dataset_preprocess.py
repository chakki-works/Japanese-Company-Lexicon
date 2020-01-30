"""
Before run this script, first comverting data to .tsv by using tools/dataset_converter.py

This script is for 

- For sentences(x): delete sentences if sentences do not contains any label of ['B-corporation_other', 'B-company_group', 'B-company']
- For labels(y): convert label to 'O' if the label is not in ['B-corporation_other', 'B-company_group', 'B-company']
- Save data to JSONL format and bio format

The JSONL format looks like:
  {
    "sample": xxxxx
    "tags": [{
      "label": xxxx(corporation),
      "span": [xxx, xxx],
      "text: xxx
    },{
     "label": 'corporation,
      "start": xxx,
      "end": xxx,
      "text: xxx 
    }]
  }

"""
import os
import json
from tqdm import tqdm
from unicodedata import normalize

from settings import ROOT_DIR

def load_data_and_labels(filename, encoding='utf-8'):
    """Loads data and label from a file.
    https://github.com/Hironsan/anago/blob/master/anago/utils.py
    Args:
        filename (str): path to the file.
        encoding (str): file encoding format.
        The file format is tab-separated values.
        A blank line is required at the end of a sentence.
        For example:
        ```
        EU	B-ORG
        rejects	O
        German	B-MISC
        call	O
        to	O
        boycott	O
        British	B-MISC
        lamb	O
        .	O
        Peter	B-PER
        Blackburn	I-PER
        ...
        ```
    Returns:
        tuple(numpy array, numpy array): data and labels.
    Example:
        >>> filename = 'conll2003/en/ner/train.txt'
        >>> data, labels = load_data_and_labels(filename)
    """
    sents, labels = [], []
    words, tags = [], []
    with open(filename, encoding=encoding) as f:
        for line in f:
            line = line.rstrip()
            if line:
                word, tag = line.split('\t')
                words.append(word)
                tags.append(tag)
            else:
                sents.append(words)
                labels.append(tags)
                words, tags = [], []

    return sents, labels

def get_corporation_index(y_train, only_company=True):
  """Get index of corporation
  
  Args:
      y_train ([type]): [description]
      only_company (bool, optional): if false，return 3 types
                                     if true，only return company type
  """
  corporation_index = []
  company_index = []

  tag_names = ['B-corporation_other', 'B-company_group', 'B-company']
  tag_counts = [0, 0, 0]
  for i, y in enumerate(y_train):
      if tag_names[0] in y:
          tag_counts[0] += 1
          corporation_index.append(i)
      elif tag_names[1] in y:
          tag_counts[1] += 1
          corporation_index.append(i)
      elif tag_names[2] in y:
          tag_counts[2] += 1
          corporation_index.append(i)
          company_index.append(i)
  print(tag_names)
  print(tag_counts)
  if only_company:
    return company_index
  else: 
    return corporation_index

def filter_corporation_tag(y, only_company=True):
  """Filter unnecessary labels. 
  
  Args:
      y (List of list of tag): 
      company_tag (False, optional): If false, return 3 kinds of types.
                                     If true, only return company type. 
                                     Defaults to False.

  Returns:
      [list of list of tag]: filted y
  """
  if isinstance(y, tuple):
      y = list(y)
  if only_company:
    company_tag_list = ['B-company', 'I-company']
  else:
    company_tag_list = ['B-corporation_other', 'I-corporation_other',
                    'B-company_group', 'I-company_group',
                    'B-company', 'I-company'] 

  for i, sample in enumerate(y):
      y[i] = ['O' if tag not in company_tag_list else tag for tag in sample]
  return y

def get_tag_list(x_sample, y_sample):
    tag_list = []
    one_tag = {'label': None, 'span': [0, 0], 'text': None}
    new_tag_flag = False
    for i, tag in enumerate(y_sample):
        if tag == 'B-corporation_other':
            one_tag['span'][0], one_tag['span'][1] = i, i
            one_tag['label'] = 'corporation_other'
            new_tag_flag = True
        elif tag == 'I-corporation_other':
            one_tag['span'][1] = i

        if tag == 'B-company_group':
            one_tag['span'][0], one_tag['span'][1] = i, i
            one_tag['label'] = 'company_group'
            new_tag_flag = True
        elif tag == 'I-company_group':
            one_tag['span'][1] = i

        if tag == 'B-company':
            one_tag['span'][0], one_tag['span'][1] = i, i
            one_tag['label'] = 'company'
            new_tag_flag = True
        elif tag == 'I-company':
            one_tag['span'][1] = i

        if (tag == 'O' or i == len(y_sample)-1) and new_tag_flag == True:
            tag_list.append(one_tag)
            new_tag_flag = False
            one_tag['text'] = x_sample[one_tag['span'][0]:one_tag['span'][1]+1]
            one_tag = {'label': None, 'span': [0, 0], 'text': None}
    return tag_list

def save_jsonl(x_corporation, y_corporation, output_file: str) -> None:
  """
  save format:
     {
    "sample": xxxxx
    "tags": [{
      "label": xxxx(corporation),
      "span": [xxx, xxx],
      "text: xxx
    },{
     "label": 'corporation,
      "start": xxx,
      "end": xxx,
      "text: xxx 
    }]
  }}
  """
  print("Begin to Save Companies as JSONL")
  with open(output_file, 'w', encoding='utf-8') as f:
    for x_sample, y_sample in zip(x_corporation, y_corporation):
      tag_list = get_tag_list(x_sample, y_sample)
      if len(tag_list) == 0:
        print(x_sample)
        print(y_sample)
      entry = {'sample': x_sample, 'tags': tag_list}
      json.dump(entry, f, ensure_ascii=False)
      f.write('\n')

def save_names(x_corporation, y_corporation, output_file) -> None:
  with open(output_file, 'w', encoding='utf-8') as f:
    all_tags = list()
    for x_sample, y_sample in zip(x_corporation, y_corporation):
      tag_list = get_tag_list(x_sample, y_sample)
      for tag in tag_list:
        tag_text = ''.join(tag['text']) 
        if len(tag_text) != 0: # in case that tag is a empty string
          all_tags.append(tag_text) 
        else:
          print(x_sample)
          print(y_sample)
    print('total tags are: {}'.format(len(all_tags)))
    unique_tags = list(set(all_tags))
    print('Unique tags are: {}'.format(len(unique_tags)))
    for tag in list(unique_tags):
      f.write('{}\n'.format(tag))

def filter_bad_words_forward(x_sample, y_sample):
    bad_word = True
    while bad_word:
        # delete empty string in 
        if len(x_sample[0]) == 0: 
            x_sample = x_sample[1:]
            y_sample = y_sample[1:]
        # delete zenkaku space in the beginning
        elif x_sample[0] == '\u3000': 
            x_sample = x_sample[1:]
            y_sample = y_sample[1:]
        # delete empty space
        elif x_sample[0] == ' ':
            x_sample = x_sample[1:]
            y_sample = y_sample[1:]
        else:
            bad_word = False
    return x_sample, y_sample

def filter_bad_words(x_sample, y_sample):
  """Remove bad words in the beginning and end"""
  # Remove bad words in the beginning
  x_sample, y_sample = filter_bad_words_forward(x_sample, y_sample)
  # Remove bad words in the end
  x_sample, y_sample = x_sample[::-1], y_sample[::-1]
  x_sample, y_sample = filter_bad_words_forward(x_sample, y_sample)
  return x_sample[::-1], y_sample[::-1]


def zenkaku_normalize(x_sample, y_sample):
  """Normalize data to hankaku format in case of length change

  x_sample: ['第', '四', '日', 'は', '五', '日', '、', '千', '葉', 'ポ', 'ー', 'ト', 'ア', 'リ', ...]
  y_sample: ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', ...]
  """
  x_sample_norm = []
  y_sample_norm = []

  for i, x in enumerate(x_sample):
    x_norm = normalize('NFKC', x)
    if len(x) == len(x_norm):
      x_sample_norm.extend(x_norm)
      y_sample_norm.append(y_sample[i])
      
    else:
      x_sample_norm.extend([x for x in x_norm])
      y_sample_norm.extend([y_sample[i] for _ in range(len(x_norm))])
  
  return x_sample_norm, y_sample_norm


def save_bio(x_corporation, y_corporation, output_file) -> None:
  total = 0
  error = 0
  with open(output_file, 'w', encoding='utf-8') as f:
    for x_sample, y_sample in zip(x_corporation, y_corporation):
      total += 1
      try:
        x_sample, y_sample = filter_bad_words(x_sample, y_sample)
        x_sample, y_sample = zenkaku_normalize(x_sample, y_sample)
        for char, tag in zip(x_sample, y_sample):
          f.write('{}\t{}\n'.format(char, tag))
      except:
        error += 1
        print(x_sample)
        continue
        
      f.write('\n')
  print('{} / {}'.format(error, total))
  print('Save bio format')

def main(data_path, output_path1, output_path2, output_path3, output_path4, output_path5):
  x_train, y_train = load_data_and_labels(data_path)

  # three corporation types
  # print('Begin 3 corporation types')
  # company_index = get_corporation_index(y_train, only_company=False)
  # x_corporation = [x_train[i] for i in company_index]
  # y_corporation = [y_train[i] for i in company_index]
  # y_corporation = filter_corporation_tag(y_corporation, only_company=False) 
  # save_jsonl(x_corporation, y_corporation, output_path1)
  # save_names(x_corporation, y_corporation, output_path3)
  # print()

  # only company type
  print('Begin only one company type')
  company_index = get_corporation_index(y_train, only_company=True)
  x_corporation = [x_train[i] for i in company_index]
  y_corporation = [y_train[i] for i in company_index]
  y_corporation = filter_corporation_tag(y_corporation, only_company=True) 
  save_jsonl(x_corporation, y_corporation, output_path2)
  save_names(x_corporation, y_corporation, output_path4)
  save_bio(x_corporation, y_corporation, output_path5)
  print()

if __name__ == "__main__":

  mainichi_path = os.path.join(ROOT_DIR, 'data/corpora/output/mainichi_dataset.tsv')
  mainichi_path1 = os.path.join(ROOT_DIR, 'data/corpora/output/mainichi_3corporation.jsonl')
  mainichi_path2 = os.path.join(ROOT_DIR, 'data/corpora/output/mainichi_1company.jsonl')
  mainichi_path3 = os.path.join(ROOT_DIR, 'data/corpora/output/mainichi_3corporation_names.jsonl')
  mainichi_path4 = os.path.join(ROOT_DIR, 'data/corpora/output/mainichi_names.csv')
  mainichi_path5 = os.path.join(ROOT_DIR, 'data/corpora/output/mainichi.bio')

  bccwj_path = os.path.join(ROOT_DIR, 'data/corpora/output/bccwj_dataset.tsv')
  bccwj_path1 = os.path.join(ROOT_DIR, 'data/corpora/output/bccwj_3corporation.jsonl')
  bccwj_path2 = os.path.join(ROOT_DIR, 'data/corpora/output/bccwj_1company.jsonl')
  bccwj_path3 = os.path.join(ROOT_DIR, 'data/corpora/output/bccwj_3corporation_names.csv')
  bccwj_path4 = os.path.join(ROOT_DIR, 'data/corpora/output/bccwj_names.csv')
  bccwj_path5 = os.path.join(ROOT_DIR, 'data/corpora/output/bccwj.bio')

  print('=== Preprocess mainnichi ===')
  main(mainichi_path, mainichi_path1, mainichi_path2, mainichi_path3, mainichi_path4, mainichi_path5)
  print('=== Preprocess bccwj ===')
  main(bccwj_path, bccwj_path1, bccwj_path2, bccwj_path3, bccwj_path4, bccwj_path5)
  print('Job Done!')