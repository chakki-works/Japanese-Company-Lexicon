import os
import glob

from tqdm import tqdm
from bs4 import BeautifulSoup

from settings import ROOT_DIR
from annotator import Annotator


def get_text(text):
    soup = BeautifulSoup(text, 'lxml')
    text = soup.find('text')
    func = lambda s: s.encode('utf-8').decode('utf-8')
    text = ''.join(map(func, text.contents))

    return text

def load_text(file_names, encoding):
    for file_name in file_names:
        with open(file_name, encoding=encoding) as f:
            text = get_text(text=f.read())
            yield text

def save_file(docs, annotator, output_path):
    total = 0
    error = 0
    with open(output_path, 'w') as f:
        for doc in tqdm(docs):
            total += 1
            try:
                text, tags = annotator.to_bio(doc)
            except:
                error += 1
                print(doc)
                continue
            for char, tag in zip(text, tags):
                f.write('{}\t{}\n'.format(char, tag))
            f.write('\n')
    print('{} / {}'.format(error, total))

def bccwj_pipeline(input_path, output_path):
    a = Annotator()
    file_names = glob.glob(os.path.join(input_path, '**/*.xml'), recursive=True)
    docs = load_text(file_names, encoding='utf-8')
    save_file(docs, a, output_path)

def mainichi_pipeline(input_path, output_path):
    a = Annotator()
    file_names = glob.glob(os.path.join(input_path, '*.sgml'))
    docs = load_text(file_names, encoding='shift_jis')
    save_file(docs, a, output_path)


if __name__ == '__main__':
    mainichi_input = os.path.join(ROOT_DIR, 'data/corpora/mainichi')
    mainichi_output = os.path.join(ROOT_DIR, 'data/corpora/output/mainichi_dataset.tsv')
    mainichi_pipeline(mainichi_input, mainichi_output)

    bccwj_input = os.path.join(ROOT_DIR, 'data/corpora/bccwj')     
    bccwj_output = os.path.join(ROOT_DIR, 'data/corpora/output/bccwj_dataset.tsv') 
    bccwj_pipeline(bccwj_input, bccwj_output)
