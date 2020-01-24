import os
import json
from pathlib import Path

from settings import ROOT_DIR

lower_length = 2
upper_length = 30

def read_dict(dict_path):
  lines = []
  with open(dict_path, 'r', encoding='utf-8') as f:
    for line in f:
      lines.append(json.loads(line))
  return lines


def save_mecab(output_path, lines, full=True):
  """Save to mecab dictionary
  params:
    output_path: output path
    lines: [{"株式会社ライフインテリア": ["ライフインテリア", "株式会社ライフインテリア"]},
            {"株式会社cotode": ["株式会社cotode", "cotode"]}, ...]
    full: True means output the full version of JCL, no need to filter
  """
  with open(output_path, 'w', encoding='utf-8') as f:
    for line in lines:
      key = list(line.keys())[0]
      values = line[key]
      for alias in values:
        if ',' not in alias:          
          if full:
            record = f'{alias},1292,1292,4000,名詞,固有名詞,組織,*,*,*,{key},*,*\n'
            f.write(record)
          else:
            if len(alias) > lower_length and len(alias) < upper_length and not alias.isdigit():
              record = f'{alias},1292,1292,4000,名詞,固有名詞,組織,*,*,*,{key},*,*\n'
              f.write(record)
                
 


def pipeline(dict_path):
  """Save dict to mecab format
  
  dict_path: the JSONL data is not filterd, so we have to filter it
  
  mecab format:https://gist.github.com/Kimtaro/ab137870ad4a385b2d79
        # 表層形,左文脈ID,右文脈ID,コスト,品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
        "(有)DEN,1292,1292,6437,名詞,固有名詞,組織,*,*,*,有限会社DEN,ユウゲンガイシャデン,ユーゲンガイシャデン"
  """
  path = Path(dict_path)
  lines = read_dict(dict_path)
  if 'full' in path.name:
    print('Saving jcl_full ...')
    output_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/jcl_full.dic') 
    save_mecab(output_path, lines, full=True)

    print('Saving jcl_medium ...')
    output_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/jcl_medium.dic') 
    save_mecab(output_path, lines, full=False)
  else:
    print('Saving jcl_slim ...')
    output_path = os.path.join(ROOT_DIR, 'data/dictionaries/output/jcl_slim.dic') 
    save_mecab(output_path, lines, full=False)

if __name__ == "__main__":
  # jcl_slim
  dict_path = os.path.join(ROOT_DIR, 'data/hojin/output/jcl_slim.jsonl')
  pipeline(dict_path)

  # jul_full
  dict_path = os.path.join(ROOT_DIR, 'data/hojin/output/jcl_full.jsonl')
  pipeline(dict_path)

  
  