import os
import json
import unicodedata
from typing import List
from collections import OrderedDict, Counter, defaultdict

import pandas as pd
from tqdm import tqdm

from settings import ROOT_DIR

dtypes = {'sequenceNumber': int, 'corporateNumber': int, 'process': int, 'correct': int, 'updateDate': str, 
          'changeDate': str, 'name': str, 'nameImageId': int, 'kind': int, 'prefectureName': str, 
          'cityName': str, 'streetNumber': str, 'addressImageId': int, 'prefectureCode': int, 'cityCode': int, 
          'postCode': int, 'addressOutside': str, 'addressOutsideImageId': int, 'closeDate': str, 'closeCause': int, 
          'successor': int, 'changeCause': str, 'assignmentDate': str, 'latest': int, 'enName': str, 
          'enPrefectureName': str, 'enCityName': str, 'enAddressOutside': str, 'furigana': str, 'hihyoji': int}
    
# example: 227,1430001000632,01,0,2015-10-30,2015-10-05,"株式会社エム．ジイ．エス",,301,"北海道","札幌市白石区","本通４丁目南２番１号",,01,104,0030026,,,,,,,2015-10-05,1,,,,,,0
kind_map = {101: "国の機関",
            201: "地方公共団体",
            301: "株式会社",
            302: "有限会社",
            303: "合名会社",
            304: "合資会社",
            305: "合同会社",
            399: "その他の設立登記法人",
            401: "外国会社等",
            499: "その他"}


class Company:
  def __init__(self, dir_name: str) -> None:
    """
    dir_name = '/.../data/hojin/csv/'
    """
    self.dir_name = dir_name
    self.file_paths = self.get_paths()
    self.data = [] # Only save Company tyle: 株式会社，有限会社，合同会社
    self.total_data = 0 # All corporations 
    self.names = defaultdict(int) # Save unique company name
    self.column_names = ['sequenceNumber', 'corporateNumber', 'process', 'correct', 'updateDate', 
                'changeDate', 'name', 'nameImageId', 'kind', 'prefectureName', 'cityName', 
                'streetNumber', 'addressImageId', 'prefectureCode', 'cityCode', 'postCode', 
                'addressOutside', 'addressOutsideImageId', 'closeDate', 'closeCause', 
                'successor', 'changeCause', 'assignmentDate', 'latest', 'enName', 
                'enPrefectureName', 'enCityName', 'enAddressOutside', 'furigana', 'hihyoji']
    
  
  def get_paths(self) -> List[str]:
    # Get all paths
    file_paths = []
    file_names = [f for f in os.listdir(self.dir_name) if f.endswith('.csv')]
    for file_name in file_names:
        file_paths.append(os.path.join(self.dir_name, file_name))
    return file_paths

  def parse_csv(self, file_paths: List[str]) -> None:
    """Parse all csv file to get company related field
    """
    print("=== Read CSV files... ===")
    for path in tqdm(file_paths):
      df = pd.read_csv(path, names=self.column_names)
      self.total_data += df.shape[0]
      df = df[df['kind'].isin([301, 302, 305])] # Only reserve 301, 302, 305（株式会社，有限会社，合同会社）
      # df['kind'] = df['kind'].map(kind_map) # Change kind to kanji representation

      # Only reserve necessary columns 
      df = df[['name', 'enName', 'furigana']]
      
      # Add zenkaku name, remove for concise
      # df['name_zenkaku'] = df['name']

      # Convert zenkaku latin to hankaku latin
      df['name'] = df['name'].apply(lambda x: unicodedata.normalize('NFKC', x)) 
      # Add unique name
      for name in df['name'].values:
        self.names[name] += 1
      # Add name, enName, furigana to self.data
      hojin_list = df.to_dict('records')
      self.data += hojin_list
    print("=== DONE! ===\n")

  def save_jsonl(self, output_file: str) -> None:
    # keys = ['name', 'enName', 'furigana']
    print("=== Save companies to JSONL... ===")
    with open(output_file, 'w') as f:
      for corporate in tqdm(self.data):
        entry = {'name': corporate['name'], 'enName': corporate['enName'], 
                 'furigana': corporate['furigana']}
        json.dump(entry, f, ensure_ascii=False)
        f.write('\n')
    print("=== DONE! ===\n")
  
  def save_names(self, output_file) -> None:
    print("=== Save companies names and frequency to CSV... ===")
    with open(output_file, 'w', encoding='utf-8') as f:
      self.names = {k: v for k, v in sorted(self.names.items(), key=lambda item: item[1], reverse=True)}
      for name, value in tqdm(self.names.items()):
        f.write('{},{}\n'.format(name, value))
    print("=== DONE! ===\n")

if __name__ == "__main__":
  print("Covnert CSV to JSONL...")
  CSV_DIR = os.path.join(ROOT_DIR, 'data/hojin/csv/') 
  OUTPUT_DIR = os.path.join(ROOT_DIR, 'data/hojin/output/') 

  company = Company(CSV_DIR)
  file_paths = company.get_paths()
  company.parse_csv(file_paths)
  print('Total corporates are: {}'.format(company.total_data))
  print('Total companies are: {}'.format(len(company.data)))
  print('Unique companies are: {}\n'.format(len(company.names)))

  output_file = os.path.join(OUTPUT_DIR, 'company.jsonl')
  company.save_jsonl(output_file)

  output_file = os.path.join(OUTPUT_DIR, 'company_frequency.csv')
  company.save_names(output_file)
  
  print("Covnert CSV to JSONL Done!")
  