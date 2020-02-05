import pickle
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def low_frequency_accuracy(sent_test_tags, sent_pred_tags, counter):
    """
    sent_test_tags: # [[{'start_idx': 7, 'end_idx': 12, 'text': '東芝キヤリア'}, {'start_idx': 14, 'end_idx': 19, 'text': 'ダイキン工業'}], 
                    [{'start_idx': 0, 'end_idx': 1, 'text': '東芝'}, {'start_idx': 27, 'end_idx': 32, 'text': 'ダイキン工業'}]]
                    
    sent_pred_tags: [[{'start_idx': 14, 'end_idx': 19, 'text': 'ダイキン工業'}], 
                    [{'start_idx': 0, 'end_idx': 1, 'text': '東芝'}, {'start_idx': 27, 'end_idx': 32, 'text': 'ダイキン工業'}]]
    counter = {'1': ['東芝キヤリア', ''東芝''], '2': ['ダイキン工業']}

    total is calculated by sent_test_tags and counter, total = {'once': 100, 'twice': 70, 'more': 50}
    correct is calculated by sent_pred_tags, correct = {'once': 1, 'twice': 2, 'more': 0}, which means '東芝' (once) is corrected, 
                                                                                                    'ダイキン工業' (twice) is corrected.
                                                                                                    '東芝キヤリア' (once) is not predicted.

    accuracy = {'once': 1/100, 'twice': 2/70, 'more': 0/50} 
    """
  correct = {'once': 0, 'twice': 0, 'more': 0}
  total = {'once': 0, 'twice': 0, 'more': 0}
  accuracy = {'once': 0, 'twice': 0, 'more': 0}

  # get total
  for test_tags in sent_test_tags:
    for test_tag in test_tags:
        if test_tag['text'] in counter['1']:
            total['once'] += 1
        elif test_tag['text'] in counter['2']:
            total['twice'] += 1
        else:
            total['more'] += 1

  # get correct pred
  for test_tags, pred_tags in zip(sent_test_tags, sent_pred_tags):
    for pred_tag in pred_tags:
        for test_tag in test_tags:
            if pred_tag['start_idx'] == test_tag['start_idx'] and pred_tag['end_idx'] == test_tag['end_idx'] and pred_tag['text'] == test_tag['text']:
                if pred_tag['text'] in counter['1']:
                    correct['once'] += 1
                elif pred_tag['text'] in counter['2']:
                    correct['twice'] += 1
                else:
                    correct['more'] += 1

  accuracy = [correct[key] / total[key] for key in total.keys()]
  result = "once accuracy: {:.4f}, twice accuracy: {:.4f}, more times: {:.4f}".format(accuracy[0], accuracy[1], accuracy[2])
  return result


def get_tag_list(x_sample, y_sample):
    tag_list = []
    tag_text = []
    one_tag = {'start_idx': 0, 'end_idx': 0, 'text': None}
    new_tag_flag = False
    for i, tag in enumerate(y_sample):
        if tag == 'B-company':
            one_tag['start_idx'], one_tag['end_idx'] = i, i
            new_tag_flag = True
        elif tag == 'I-company' and new_tag_flag:
            one_tag['end_idx'] = i
        if (tag == 'O' or i == len(y_sample)-1) and new_tag_flag is True:
            tag_list.append(one_tag)
            new_tag_flag = False
            one_tag['text'] = ''.join(x_sample[one_tag['start_idx'] : one_tag['end_idx']+1])
            one_tag = {'start_idx': 0, 'end_idx': 0, 'text': None}
    for tag in tag_list:
        tag_text.append(tag['text'])
    return tag_list


def get_sent_tags(sent_words, sent_tags):
    result = []
    for (words, tags) in zip(sent_words, sent_tags):
        tag_list = get_tag_list(words, tags)
        result.append(tag_list)
    return result


def merge_maps(dict1, dict2):
    """merge two word2id or two tag2id"""
    for key in dict2.keys():
        if key not in dict1:
            dict1[key] = len(dict1)
    return dict1


def save_model(model, file_name):
    """save model"""
    with open(file_name, "wb") as f:
        pickle.dump(model, f)


def load_model(file_name):
    """load model"""
    with open(file_name, "rb") as f:
        model = pickle.load(f)
    return model

# LSTM model need to add PAD and UNK to word2id and tag2id
# If using the CRF layer for Bi-LSTM, it also need to add <start> and <end> (decoding)
def extend_maps(word2id, tag2id, for_crf=True):
    word2id['<unk>'] = len(word2id)
    word2id['<pad>'] = len(word2id)
    tag2id['<unk>'] = len(tag2id)
    tag2id['<pad>'] = len(tag2id)
    # If using the CRF layer for Bi-LSTM, it also need to add <start> and <end> (decoding)
    if for_crf:
        word2id['<start>'] = len(word2id)
        word2id['<end>'] = len(word2id)
        tag2id['<start>'] = len(tag2id)
        tag2id['<end>'] = len(tag2id)

    return word2id, tag2id


def prepocess_data_for_lstmcrf(word_lists, tag_lists, test=False):
    assert len(word_lists) == len(tag_lists)
    for i in range(len(word_lists)):
        word_lists[i].append("<end>")
        if not test:  # if test data, no need to add end token
            tag_lists[i].append("<end>")

    return word_lists, tag_lists


def flatten_lists(lists):
    flatten_list = []
    for l in lists:
        if type(l) == list:
            flatten_list += l
        else:
            flatten_list.append(l)
    return flatten_list


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


def build_map(lists):
    maps = {}
    for list_ in lists:
        for e in list_:
            if e not in maps:
                maps[e] = len(maps)

    return maps
