import os
import json
import re
import unicodedata
from typing import List
from collections import OrderedDict, Counter, defaultdict

from tqdm import tqdm
from IPython import embed

from settings import ROOT_DIR


def find_legal_form(legal_forms, name):
  """Find name if it contains any of legal forms
  
  Args:
      legal_forms (list[str]): ['株式会社', '有限会社', '合同会社'] 
      name (str): 'TIS株式会社'
  Return:
    if find, ['株式会社']
    else, []
  """
  for legal_form in legal_forms:
    if legal_form in name:
      return legal_form
  return ''

def find_abnormal_form(legal_forms_dict, name):
  """Find unnormal JP legal form
  
  Args:
      legal_forms_dict (dict): {'株式会社': ['株式會社', '株式会仕', '株式会杜', '株式会礼', '株弍会社', '抹式会社', '株式金社', '株式公社', '株式会']}
      name (str): name
  """
  for normal_name, values in legal_forms_dict.items():
    abnormal_name = find_legal_form(values, name)
    if abnormal_name:
      return abnormal_name, normal_name
  return '', ''


class AliasGenerator:
  """Read company names from jsonl"""

  def __init__(self, data:List[dict]):
    self.data = data

  @classmethod
  def read_json(cls, path:str) -> List[dict]:
    """Read data from JSONL
    output example:
          {'enName': nan,
          'furigana': nan,
          'name': '株式会社ACT NOW'}
    """
    companies = []
    with open(path, 'r') as f:
      print('Reading data from JSONL...')
      for company in tqdm(f):
        company_json = json.loads(company)
        companies.append(company_json)
    return cls(companies)

  def remove_duplicate_companies(self): 
    """Remove duplicate companies, get enName and furigana"""
    print('Begin to remove duplicate companies...')
    count = [0, 0]
    unique_names = dict()
    for company in tqdm(self.data):
      name = company['name']  
      if name not in unique_names:
        unique_names[name] = company
      else:
        if str(unique_names[name]['enName']) == 'nan' and str(company['enName']) != 'nan':
          unique_names[name]['enName'] = company['enName'] 
          count[0] += 1
        if str(unique_names[name]['furigana']) == 'nan' and str(company['furigana']) != 'nan':
          unique_names[name]['furigana'] = company['furigana'] 
          count[1] += 1
    print('enName updated: {}, furigana updated: {}'.format(count[0], count[1]))
    print('Total names are: {}, unique names are: {}'.format(len(self.data), len(unique_names)))

    self.data = [v for v in unique_names.values()]

  def remove_legal_form(self):
    """Remove legal form for JP and EN
    output example:
        {'enName': nan,
          'furigana': nan,
          'name': '株式会社ジェイエイチインターナショナル',
          'jp_no_legal': 'ジェイエイチインターナショナル'}
    """ 
    jp_legal_forms = ['株式会社', '有限会社', '合同会社']
    jp_abnormal_forms = {'株式会社': ['株式會社', '株式会仕', '株式会杜', '株式会礼', '株弍会社', '抹式会社', '株式金社', '株式公社', '株式会'],
                        '有限会社': ['有限式会社', '有階会社', '有限會社', '有現会社', '有眼会社', '有限会杜', '有限衾社', '有限会'],
                        '合同会社': ['合名会社']}
    en_legal_forms = ['KABUSHIKI KAISHA', 'Trading Company', 'KABUSHIKIGAISHA', ' corporation', ' CORPORATION', ' Corporation', 'Godo Kaisha', 
                      ' Co., Ltd.', ' co.,ltd.', ' Co.,Ltd.', ' CO., LTD', ' Co. Ltd.', ' Co.,Ltd', ' CO.,LTD.', ' CO.,Ltd.', ' LIMITED', ' Co.,Ltd', 
                      ' CO.,LTD', ' COMPANY', ' co.,Ltd', ' Limited', ' Co.Ltd', 'Co,.Ltd.', ', INC.', ' CORP.', ' Corp.', ', Inc.', 'L.L.C.', ' k.k.', ' ltd.', 
                      'K. K.', ', LTD', 'INC.', 'llc.', 'lnc.', 'LTD.', ' LLc', 'Inc.', ',INC', 'K.K.', 'Firm', 'Ltd.', ',LCC', 'inc.', ' CO.', 'LLC.', 
                      'G.K.', ' inc', ' LTD', 'INC', 'LLC', 'Co.', 'llc', ' GK', ' LC', 'GK.', 'Inc', 'Ltd', 'KK']
    
    print('Begin to remove legal form ...')
    # 1 delete legal form for JP
    jp1 = [] # Companies that have normal, 2942266, example: ['株式会社', '有限会社', '合同会社'],  
    jp2 = [] # Companies that have abnormal, 0, example: ['株式會社', '株式会仕', '株式会杜', '株式会礼', '株弍会社', ...] 
    jp3 = [] # Companies except above two situations, 0 
    for company in tqdm(self.data):
      jp_legal_form = find_legal_form(jp_legal_forms, company['name'])
      if jp_legal_form:
        company['no_legal'] = company['name'].replace(jp_legal_form, '') 
        jp1.append(company)
      else:
        abnormal_name, normal_name = find_abnormal_form(jp_abnormal_forms, company['name'])
        if abnormal_name:
          company['no_legal'] = company['name'].replace(abnormal_name, '') 
          company['name'] = company['name'].replace(abnormal_name, normal_name) 
          jp2.append(company)
        else:
          company['no_legal'] = 'nan'
          jp3.append(company)

    # 2 delete legal form for EN
    en1 = [] # enName exist, and contains en_legal_forms, 1354
    en2 = [] # enName exist, not contains en_legal_forms, 13
    en3 = [] # enName not exist, 2940899
    for company in tqdm(self.data): 
      if str(company['enName']) != 'nan': 
        en_legal_form = find_legal_form(en_legal_forms, company['enName'])
        if en_legal_form: # legal form exists
          company['en_no_legal'] = company['enName'].replace(en_legal_form, '').strip()
          en1.append(company)
        else: # Legal form not exist, use the original enName
          company['en_no_legal'] = company['enName'] 
          en2.append(company)
      else:
        company['en_no_legal'] = 'nan'
        en3.append(company)


  def remove_special_character(self, data=None):
    """Remove special character
    test_names = ["DECOR.F.C株式会社", "株式会社K’s Act", "Metty-labo", "株式会社L’atelier Monei", 
                  "株式会社Q&F", 'TISシステムサービス株式会社', '合同会社やまこう']

    output example:
       {'enName': nan,
        'furigana': nan,
        'name': '株式会社ジェイエイチインターナショナル',
        'no_legal': 'ジェイエイチインターナショナル',
        'no_special': '株式会社ジェイエイチインターナショナル'}
    """
    print('Begin to remove special character ...')
    #  remove specical character
    for company in tqdm(self.data):
      company['no_special'] = re.sub(r"[\'|・|.|’|^|&|,|、|-]+", '', company['name'])
      company['no_legal_no_special'] = re.sub(r"[\'|・|.|’|^|&|,|、|-]+", '', company['no_legal'])

  def en_normalization(self):
    """Normalize the EN company names
    Eexample: toyoto -> Toyota -> TOYOTA
              BALZANO JAPAN -> Balzano Japan -> balzano japan
    """
    print('Begin to normalize English Name ...')
    for company in tqdm(self.data):
      if company['en_no_legal'] != 'nan':
        name = company['en_no_legal']
        name_list = [name.title(), name.lower(), name.upper()]
        company['en_norm'] = list(set(name_list))
      else:
        company['en_norm'] = list()

  def jp_normalization(self):
    """Normalize the JP company name

    Covert lower case furigana/katakana to uppter case furigana/katakana, e.g. ェ -> エ

    Reference: https://github.com/studio-ousia/mojimoji/blob/master/mojimoji.pyx

    output example:
      {'enName': nan,
        'furigana': nan,
        'name': '株式会社ジェイエイチインターナショナル',
        'no_legal': 'ジェイエイチインターナショナル',
        'no_special': '株式会社ジェイエイチインターナショナル',
        'en_no_legal': 'YEAST haha'
        'en_norm': ['YEAST HAHA', 'yeast haha', 'Yeast Haha'] or []
        'jp_norm': ['株式会社ジエイエイチインターナシヨナル',
          'ジェイエイチインターナショナル',
          '株式会社ジェイエイチインターナショナル',
          'ジエイエイチインターナシヨナル']}
    """
    print('Begin to normalize lower katakana ...')
    katakana_komoji = 'ァィゥェォッャュョ'
    katakana_omoji = 'アイウエオツヤユヨ'
    furigana_komoji = 'ぁぃぅぇぉっゃゅょ'
    furigana_omoji = 'あいうえおつやゆよ'
    katakana_translation = str.maketrans(katakana_komoji, katakana_omoji)
    furigana_translation = str.maketrans(furigana_komoji, furigana_omoji)
    for company in tqdm(self.data):
      company['jp_norm'] = set()
      company['jp_norm'].add(company['name'].translate(katakana_translation))
      company['jp_norm'].add(company['no_legal'].translate(katakana_translation))
      company['jp_norm'].add(company['no_special'].translate(katakana_translation))
      company['jp_norm'].add(company['no_legal_no_special'].translate(katakana_translation))

      company['jp_norm'].add(company['name'].translate(furigana_translation))
      company['jp_norm'].add(company['no_legal'].translate(furigana_translation))
      company['jp_norm'].add(company['no_special'].translate(furigana_translation))
      company['jp_norm'].add(company['no_legal_no_special'].translate(furigana_translation))
 
      company['jp_norm'] = list(company['jp_norm'])  

  
def remove_duplicate_alias(data: dict, furigana=True, en_name=True): 
  """Remove all duplicate alias
    input example:
      self.data = {'name': '株式会社NOIE', 
                  'enName': 'NOIE corporation', 
                  'furigana': 'ノイエ', 
                  'no_legal': 'NOIE', 
                  'en_no_legal': 'NOIE', 
                  'no_special': '株式会社NOIE', 
                  'no_legal_no_special': 'NOIE', 
                  'en_norm': ['Noie', 'NOIE', 'noie'], 
                  'jp_norm': ['NOIE', '株式会社NOIE']}
  """
  alias_dict = dict()
  for company in tqdm(data):
    alias = set()
    alias.add(company['name'])
    alias.add(company['no_legal'])
    alias.add(company['no_special'])
    alias.add(company['no_legal_no_special'])
    alias = alias.union(set(company['jp_norm']))
    if not furigana and str(company['furigana']) != 'nan':
      alias.add(company['furigana'])
    if not en_name and str(company['enName']) != 'nan':
      alias.add(company['enName'])
      alias = alias.union(set(company['en_norm']))
    alias_dict[company['name']] = list(alias)
  return alias_dict


def status(alias: dict):
  """Get alias data information"""
  unique_name_count = len(alias)
  unique_alias_count = sum(len(v) for v in alias.values())
  average_alias_count = unique_alias_count / unique_name_count
  print('=====Status=====')
  print('Total unique company is: {}'.format(unique_name_count))
  print('Unique alias count is: {}'.format(unique_alias_count)) 
  print('Average alias company is: {0:.2f}'.format(average_alias_count))
  print('An example is:')
  i = 0
  for item in alias.items():
    print(item)
    i += 1
    if i > 0:
      break

def save_jsonl(alias: dict, output_file: str) -> None:
  """Save to JSONL 
  save format:
    {'name': ['alias1', 'alias2', ....]}
    {'name': ['alias1', 'alias2', ....]}
  """
  print("=== Save to JSONL... ===")
  with open(output_file, 'w') as f:
    for key, value in tqdm(alias.items()):
      entry = {key: value}
      json.dump(entry, f, ensure_ascii=False)
      f.write('\n')

def save_names(alias: dict, output_file: str) -> None:
  """Save to CSV
  One line for one name
  """
  print("=== Save to CSV...===")
  with open(output_file, 'w', encoding='utf-8') as f:
    for name, alias_list in tqdm(alias.items()):
      for alias in alias_list:  
        f.write('{}\n'.format(alias))


if __name__ == '__main__':

  company_path = os.path.join(ROOT_DIR, 'data/hojin/output/company.jsonl') # /Users/smap10/Project/japanese-company-lexicon/data/hojin/output/company.jsonl
  output_dir = os.path.join(ROOT_DIR, 'data/hojin/output/') 

  alias = AliasGenerator.read_json(company_path) 
  alias.remove_duplicate_companies() # Remove duplicate companies, get enName and furigana
  alias.remove_legal_form() # Remove legal form for JP and EN
  alias.remove_special_character() # Remove special character
  alias.en_normalization() # Normalize the EN company name
  alias.jp_normalization() # Normalize the JP company name

  # alias without furigana and enname
  alias_normal = remove_duplicate_alias(alias.data, furigana=True, en_name=True) 
  status(alias_normal)
  output_file = os.path.join(output_dir, 'jcl_slim.jsonl') # simplified version don't contains furigana and English alias to decrease the annotation error
  save_jsonl(alias_normal, output_file) 
  output_file = os.path.join(output_dir, 'jcl_slim.csv')
  save_names(alias_normal, output_file)

  # alias with furigana and enname
  alias_furigana_enname = remove_duplicate_alias(alias.data, furigana=False, en_name=False) 
  status(alias_furigana_enname)
  output_file = os.path.join(output_dir, 'jcl_full.jsonl') # full version contains furigana and English alias
  save_jsonl(alias_furigana_enname, output_file) 
  output_file = os.path.join(output_dir, 'jcl_full.csv')
  save_names(alias_furigana_enname, output_file)
