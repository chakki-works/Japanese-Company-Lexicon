import os
from pathlib import Path
from settings import ROOT_DIR

def filter_name(names, lower_length=2, upper_length=30):
  """filter names with length
  Args:
    names (list): name list
    filter_length (int, optional): 
      0: filter the digital alias names, like 0, 00, 1990
      1: filter digits and filter names whose lengh is larger than 1, e.g. "風"
      2: filter digits and filter names whose lenght is larger than 2, e.g. "今日"
      3: filter digits and filter names whose lenght is larger than 3, like "B&P", "由和堂"
      4: ..., like "前場商店", "じんごう" 
  """
  result = set()
  for name in names:
    if len(name) > lower_length and len(name) < upper_length:
      if not name.isdigit():
        result.add(name)
  return list(result)

def jcl_pipeline(path):
  print('JCL filtered files generation process...')
  # Read
  input_path = Path(os.path.join(ROOT_DIR, path))
  names = list()
  with open(input_path, 'r', encoding='utf-8') as f:
    for name in f:
      names.append(name.strip())
  
  # Filter the digits, and the company names with proper length
  lower_length = 2
  upper_length = 30
  print('Before filtering lower length: {}, name counts: {}'.format(lower_length, len(names)))
  names = filter_name(names, lower_length=lower_length, upper_length=upper_length)
  print('After filtering lower length: {}, name counts: {}'.format(lower_length, len(names)))

  # Generate final JCL lexicon
  output_path = os.path.join(ROOT_DIR, 'data/dictionaries', input_path.name)
  with open(output_path, 'w', encoding='utf-8') as f:
    for name in names:
      f.write('{}\n'.format(name))
    print("Generate filterd file to: {}".format(output_path))
    print()

if __name__ == "__main__":
    paths = ['data/hojin/output/jcl_full.csv', 'data/hojin/output/jcl_slim.csv']
    for path in paths:
      jcl_pipeline(path) # filtering names to decrease annotation error
