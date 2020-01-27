import gc 
import os
import glob
from pathlib import Path

from utils import ROOT_DIR
from utils import extend_maps, prepocess_data_for_lstmcrf, build_map, load_data_and_labels
from evaluate import crf_train_eval, bilstm_train_and_eval

def split_data(sents, glod_labels, tag_labels, dev=False, train_ratio=0.7, dev_ratio=0.85):
    if not dev:
        split_index = int(len(sents) * train_ratio)
        train_word_lists, train_tag_lists = sents[:split_index], tag_labels[:split_index]
        test_word_lists, test_tag_lists = sents[split_index:], glod_labels[split_index:]
        return train_word_lists, train_tag_lists, test_word_lists, test_tag_lists
    else:
        train_index = int(len(sents) * train_ratio)
        dev_index = int(len(sents) * dev_ratio)
        train_word_lists, train_tag_lists = sents[:train_index], tag_labels[:train_index]
        dev_word_lists, dev_tag_lists = sents[train_index:dev_index], glod_labels[train_index:dev_index]
        test_word_lists, test_tag_lists = sents[dev_index:], glod_labels[dev_index:]
        return train_word_lists, train_tag_lists, dev_word_lists, dev_tag_lists, test_word_lists, test_tag_lists

def crf_pipeline(data_paths, glod_data_path):
    # read glod data
    sents, glod_labels = load_data_and_labels(glod_data_path)

    for data_path in data_paths:
        # read tagged data
        tag_sents, tag_labels = load_data_and_labels(data_path)
        train_word_lists, train_tag_lists, test_word_lists, test_tag_lists = split_data(tag_sents, glod_labels, tag_labels, dev=False)
        
        data_path = Path(data_path)
        print("Training and evaluating CRF model for data:", data_path.stem)
        print('trian data: {}, test data: {}'.format(len(train_tag_lists), len(test_tag_lists)))
        crf_pred = crf_train_eval(
            (train_word_lists, train_tag_lists),
            (test_word_lists, test_tag_lists)
        )
        print()
        print()
        del crf_pred 
        gc.collect()
    
def bi_lstm_crf_pipeline(data_path, glod_data_path):
    # read glod data
    sents, glod_labels = load_data_and_labels(glod_data_path)

    # read tagged data
    tag_sents, tag_labels = load_data_and_labels(data_path)
    train_word_lists, train_tag_lists, dev_word_lists, dev_tag_lists, test_word_lists, test_tag_lists = split_data(tag_sents, glod_labels, tag_labels, dev=True, train_ratio=0.7, dev_ratio=0.85)        
    word2id = build_map(train_word_lists)
    tag2id = build_map(train_tag_lists)

    # Add <start> and <end> if using CRF layer with Bi-LSTM (decoding)
    crf_word2id, crf_tag2id = extend_maps(word2id, tag2id, for_crf=True)

    # other data process 
    train_word_lists, train_tag_lists = prepocess_data_for_lstmcrf(
        train_word_lists, train_tag_lists
    )
    dev_word_lists, dev_tag_lists = prepocess_data_for_lstmcrf(
        dev_word_lists, dev_tag_lists
    )
    test_word_lists, test_tag_lists = prepocess_data_for_lstmcrf(
        test_word_lists, test_tag_lists, test=True
    )

    print("Training and evaluating Bi-LSTM-CRF model for data:", data_path.stem)
    print('trian data: {}, dev data: {}, test data: {}'.format(len(train_tag_lists), len(dev_tag_lists), len(test_tag_lists)))

    lstmcrf_pred = bilstm_train_and_eval(
        (train_word_lists, train_tag_lists),
        (dev_word_lists, dev_tag_lists),
        (test_word_lists, test_tag_lists),
        crf_word2id, crf_tag2id
    )
    del lstmcrf_pred 
    gc.collect()

def main(data_paths, glod_data_path):
    """CRF and Bi-LSTM-CRF pipelines"""

    # CRF pipeline
    crf_pipeline(data_paths, glod_data_path)

    # Bi-LSTM-CRF Pipeline
    for data_path in data_paths:
        data_path = Path(data_path)
        bi_lstm_crf_pipeline(data_path, glod_data_path)
        
   
if __name__ == "__main__":
    data_dir = os.path.join(ROOT_DIR, 'data/corpora/output/*.bio')
    data_paths = glob.glob(data_dir) 
    data_paths = sorted(data_paths, key=lambda x: len(x))

    # bccwj  
    bccwj_paths = [x for x in data_paths if 'bccwj' in x]
    bccwj_glod = os.path.join(ROOT_DIR, 'data/corpora/output/bccwj.bio') 
    main(bccwj_paths, bccwj_glod)

    # mainichi
    mainichi_paths = [x for x in data_paths if 'mainichi' in x] 
    mainichi_glod = os.path.join(ROOT_DIR, 'data/corpora/output/mainichi.bio')     
    main(mainichi_paths, mainichi_glod)
    