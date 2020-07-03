# Japanese Company Lexicon (JCLdic)

The repo of "High Coverage Lexicon for Japanese Company Name Recognition" [Paper](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/xu2020jcldic.pdf). 

## Download links

We provide two kinds of format. The `CSV` format contains one name per line, and the [MeCab format](https://gist.github.com/Kimtaro/ab137870ad4a385b2d79) contains one record per line.  Users can directly open `MeCab CSV` format to check the record. The `MeCab Dic` format is compiled by MeCab, which can be used as the user dictionary of MeCab. [MeCab Dic usage](https://github.com/chakki-works/Japanese-Company-Lexicon/wiki/JCLdic-Usage)


- JCL_slim (7067216, [CSV](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_slim.csv.zip), [MeCab CSV](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_slim_mecab.csv.zip), [MeCab Dic](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_slim_mecab.dic.zip)): No furigana, no extra enNames, no digital names, the name length is longer than 2 and shorter than 30.
- JCL_medium (7555163, [CSV](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_medium.csv.zip), [MeCab CSV](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_medium_mecab.csv.zip), [MeCab Dic](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_medium_mecab.dic.zip)): No digital names, the name length is longer than 2 and shorter than 30. 
- JCL_full (8491326, [CSV](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_full.csv.zip), [MeCab CSV](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_full_mecab.csv.zip), [MeCab Dic 1 (5,000,000)](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_full_mecab_1.dic.zip), [MeCab Dic 2 (3,491,326)](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_full_mecab_2.dic.zip)): Contain all kinds of names. I split the MeCab Dic into two files because MeCab cannot compile the single file due to the large file size. 

Our goal is to build the enterprise knowledge graph, so we only consider the companies that conducts economic activity for commercial purposes. These companies are denoted as Stock Company (株式会社), Limited Company (有限会社), and Limited Liability Company (合同会社). 


The full version contains all kinds of names, including digits, one character  aliases, etc. These abnormal names will cause annotation error for NER task. We recommend use the JCL_medium version or JCL_slim version. 

These release versions are easier to use than the version we used in the paper. Considering the trade-off between dictionary size and searching performance, we delete zenkaku(全角) names and only preserve the hankaku(半角) names. For example, we delete `'株式会社ＫＡＤＯＫＡＷＡ'` but preserve `'株式会社KADOKAWA'`. As for the normalization process, please read the Python section in [usage page](https://github.com/chakki-works/Japanese-Company-Lexicon/wiki/JCLdic-Usage).


| **Single Lexicon**         | Total Names | Unique Company Names |
| -------------------------- | ----------- | -------------------- |
| JCL-slim                   | 7067216     | 7067216              |
| JCL-medium                 | 7555163     | 7555163              |
| JCL-full                   | 8491326     | 8491326              |
| IPAdic                     | 392126      | 16596                |
| Juman                      | 751185      | 9598                 |
| NEologd                    | 3171530     | 244213               |
| **Multiple Lexicon**       |             |                      |
| IPAdic-NEologd             | 4615340     | 257246               |
| IPAdic-NEologd-JCL(medium) | 12093988    | 7722861              |

## Usage

See [wiki](https://github.com/chakki-works/Japanese-Company-Lexicon/wiki/JCLdic-Usage) page for detail usage.


## JCLdic Generation Process

Instead of downloading the data, you can even build the JCLdic from scratch by following the below instructions. 

### Data Preparation

```
# conda create -n jcl python=3.6
# source activate jcl
pip install -r requirements.txt
```

If you want to download the data by Selenium, you have to download the ChromeDriver. First check your Chrome version, and then download the corresponding version of ChromeDriver from [here](https://chromedriver.chromium.org/downloads). 


Uncompressing ZIP file to get `chromedriver`, then move it to target directory:
```
cd $HOME/Downloads
unzip chromedriver_mac64.zip 
mv chromedriver /usr/local/bin
```

We create JCLdic according to the original data from [National Tax Agency Corporate Number Publication Site](https://www.houjin-bangou.nta.go.jp/) (国税庁法人番号公表サイト). Please download the ZIP files data from the below site:

- [CSV形式・Unicode](https://www.houjin-bangou.nta.go.jp/download/zenken/#csv-unicode)


Put the ZIP files to `data/hojin/zip` directory, and run below script to preprocess the data:
```bash
bash scripts/download.sh
```

Below directories will be generated automatically, but you need to create `data/hojin/zip` directory manually to store the ZIP files in the first place. 

```bash
.
├── data
│   ├── corpora 
│   │   ├── bccwj             # raw dataset
│   │   ├── mainichi          # raw dataset
│   │   └── output            # processed bccwj and mainichi dataset as IBO2 format
│   ├── dictionaries
│   │   ├── ipadic            # raw lexicon
│   │   ├── neologd           # raw lexicon
│   │   ├── juman             # raw lexicon
│   │   └── output            # processed lexicons
│   └── hojin
│       ├── csv               # downloaded hojin data
│       ├── output            # processed JCLdic
│       └── zip               # downloaded hojin data
```

### JCLdic Generation

Generating alias
```bash
bash scripts/generate_alias.sh
```

Until now, the JCLdic is prepared. 

If you want to get the MeCab format:
```
python tools/save_mecab_format.py
```

### Evaluation

Below result is based on the latest version of JCLdic, which might be different with the performance of the paper reported. 


#### Datasets, dictionaries, and annotated datasets preparation

Because these datasets (Mainichi, BCCWJ) are not free, you should get the datasets by yourself. After you get the datasets, put them to `data/corpora/{bccwj,mainichi}` and run the below command:

 
```bash
# 1 Datasets preparation
python tools/dataset_converter.py # Read data from .xml, .sgml to .tsv
python tools/dataset_preprocess.py # Generate .bio data
```

If you want to compare other dictionaries, you could download it from below links and put them to `data/dictionaries/{ipadic,jumman,neologd}`:

```bash
# ipadic
# https://github.com/taku910/mecab/tree/master/mecab-ipadic

# juman
# https://github.com/taku910/mecab/tree/master/mecab-jumandic

# neologd
# https://github.com/neologd/mecab-ipadic-neologd/blob/master/seed/mecab-user-dict-seed.20200109.csv.xz

# 2 Prepare dictionaries 
python tools/dictionary_preprocess.py
```

```bash
# 3 Annotate datasets with different dictionaries 
python tools/annotation_with_dict.py
```

#### Intrinsic Evaluation: Coverage 

Calculate coverage:
```
python tools/coverage.py
```

The intrinsic evaluation is calculate how many company names in different lexicons. The best results are highlighted.



| **Single Lexicon**         | Mainichi |            | BCCWJ |            |
| -------------------------- | -------- | ---------- | ----- | ---------- |
|                            | Count    | Coverage   | Count | Coverage   |
| JCL-slim                   | 727      | 0.4601     | 419   | 0.4671     |
| JCL-medium                 | 730      | 0.4620     | 422   | 0.4705     |
| JCL-full                   | 805      | **0.5095** | 487   | **0.5429** |
| IPAdic                     | 726      | 0.4595     | 316   | 0.3523     |
| Juman                      | 197      | 0.1247     | 133   | 0.1483     |
| NEologd                    | 424      | 0.2684     | 241   | 0.2687     |
| **Multiple Lexicon**       |          |            |       |            |
| IPAdic-NEologd             | 839      | 0.5310     | 421   | 0.4693     |
| IPAdic-neologd-JCL(medium) | 1064     | **0.6734** | 568   | **0.6332** |


#### Extrinsic Evaluation: NER task

Make sure the `main.py` has following setting:

```python
# main.py setting
entity_level = False 
# ...
### result 1 ###
# bccwj  
main(bccwj_paths, bccwj_glod, entity_level=entity_level)
# mainichi
main(mainichi_paths, mainichi_glod, entity_level=entity_level)
```

Run the below command:

```
python main.py
```

The extrinsic evaluation is using using the NER taks to measure different lexicon performance.  We annotate training set with different lexicons, train the model (CRF and Bi-LSTM-CRF), and test on the test set. The `Glod` means we train the model with true labels. The best result is highlighted. 



Following table is the extrinsic evaluation result. The best results are highlighted. 


| Single Lexicon             | Mainichi F1 |             | BCCWJ F1   |             |
| -------------------------- | ----------- | ----------- | ---------- | ----------- |
|                            | CRF         | Bi-LSTM-CRF | CRF        | Bi-LSTM-CRF |
| Gold                       | 0.9756      | 0.9683      | 0.9273     | 0.8911      |
| JCL-slim                   | 0.8533      | 0.8708      | 0.8506     | 0.8484      |
| JCL-meidum                 | 0.8517      | 0.8709      | 0.8501     | **0.8526**  |
| JCL-full                   | 0.5264      | 0.5792      | 0.5646     | 0.7028      |
| Juman                      | 0.8865      | 0.8905      | 0.8320     | 0.8169      |
| IPAdic                     | **0.9048**  | **0.9141**  | **0.8646** | 0.8334      |
| NEologd                    | 0.8975      | 0.9066      | 0.8453     | 0.8288      |
| **Multiple Lexicon**       |             |             |            |             |
| IPAdic-NEologd             | **0.8911**  | **0.9074**  | **0.8624** | 0.8360      |
| IPAdic-NEologd-JCL(medium) | 0.8335      | 0.8752      | 0.8530     | **0.8524**  |

## Extra Experiment

### Dictionary annotation as feature on token level

The new experiment results are in the parentheses. We use the dictionary annotation as CRF feature, and the best results are highlighted. The result shows that the dictionary feature boost the performance, especially the JCL. 


| Single Lexicon             | Mainichi F1         | BCCWJ F1            |
| -------------------------- | ------------------- | ------------------- |
|                            | CRF                 | CRF                 |
| Gold                       | 0.9756 (1)          | 0.9273 (1)          |
| JCL-slim                   | 0.8533 (0.9754)     | 0.8506 (0.9339)     |
| JCL-meidum                 | 0.8517 (0.9752)     | 0.8501 (0.9303)     |
| JCL-full                   | 0.5264 (**0.9764**) | 0.5646 (**0.9364**) |
| Juman                      | 0.8865 (0.9754)     | 0.8320 (0.9276)     |
| IPAdic                     | 0.9048 (0.9758)     | 0.8646 (0.9299)     |
| NEologd                    | 0.8975 (0.9750)     | 0.8453 (0.9282)     |
| **Multiple Lexicon**       |                     |                     |
| IPAdic-NEologd             | 0.8911 (**0.9767**) | 0.8624 (**0.9366**) |
| IPAdic-NEologd-JCL(medium) | 0.8335 (0.9759)     | 0.8530 (0.9334)     |

### Dictionary annotation as feature on entity level

Make sure the `main.py` has following setting:

```python
# main.py setting
entity_level = True 
# ...
### result 1 ###
# bccwj  
main(bccwj_paths, bccwj_glod, entity_level=entity_level)
# mainichi
main(mainichi_paths, mainichi_glod, entity_level=entity_level)

### result 2 ###
# bccwj: use dictionary as feature for CRF
crf_tagged_pipeline(bccwj_paths, bccwj_glod, entity_level=entity_level)
# mainichi: use dictionary as feature for CRF       
crf_tagged_pipeline(mainichi_paths, mainichi_glod, entity_level=entity_level) 
```

Run the below command:

```
python main.py
```


The entity level result:

- `result1` : train the data on the labels that tagged by dictionary
- `result2` : add the dictionary tag as feature for CRF, use the true label for training



| Single Lexicon             | Mainichi F1 (CRF) | Mainichi F1 (CRF) | BCCWJ F1 (CRF) | BCCWJ F1 (CRF) |
| -------------------------- | ----------------- | ----------------- | -------------- | -------------- |
|                            | Result1           | Result2           | Result1        | Result2        |
| Gold                       | 0.7826            |                   | 0.5537         |                |
| JCL-slim                   | 0.1326            | 0.7969            | 0.1632         | 0.5892         |
| JCL-meidum                 | 0.1363            | 0.7927            | **0.1672**     | 0.5813         |
| JCL-full                   | 0.0268            | **0.8039**        | 0.0446         | **0.6205**     |
| Juman                      | 0.0742            | 0.7923            | 0.0329         | 0.5661         |
| IPAdic                     | **0.3099**        | 0.7924            | 0.1605         | 0.5961         |
| NEologd                    | 0.1107            | 0.7897            | 0.0814         | 0.5718         |
| **Multiple Lexicon**       |                   |                   |                |                |
| IPAdic-NEologd             | **0.2456**        | 0.7986            | 0.1412         | 0.6187         |
| IPAdic-NEologd-JCL(medium) | 0.1967            | **0.8009**        | **0.2166**     | 0.6132         |


From `result1` and `result2`, we can see these dictionary are not suitable for annotating training label, but the dictionary feature do improve the performance in `result2`. 


### Dictionary feature for low frequency company names on entity level

<!-- Make sure the `main.py` has following setting:

```python
# main.py setting
entity_level = True 
# ...
### result 3 ###
# bccwj: evaluate on low frequency company names 
main(bccwj_paths, bccwj_glod, entity_level=entity_level, low_frequency=bccwj_counter)
# mainichi: evaluate on low frequency company names
main(mainichi_paths, mainichi_glod, entity_level=entity_level, low_frequency=mainichi_counter)

### result 4 ###
# bccwj: evaluate on low frequency company names, use dictionary as feature for CRF
crf_tagged_pipeline(bccwj_paths, bccwj_glod, entity_level=entity_level, low_frequency=bccwj_counter)
# mainichi: evaluate on low frequency company names, use dictionary as feature for CRF
crf_tagged_pipeline(mainichi_paths, mainichi_glod, entity_level=entity_level, low_frequency=mainichi_counter) 
```

Run the below command:

```
python main.py
``` -->

We first divide the result into 3 categories:


| Category | Description                                       | Evaluation                                    |
| -------- | ------------------------------------------------ | --------------------------------------------- |
| Zero       | the entity not exist in the training set         | Zero-shot, performance on unseen entity       |
| One        | the entity only exists once in the training set  | One-shot, performance on low frequency entity |
| More       | the entity exists many times in the training set | Training on normal data                       |

The dataset statistics: 



| Dataset                                                      | BCCWJ                                | Mainichi                            |
| ------------------------------------------------------------ | ------------------------------------ | ----------------------------------- |
| Company Samples/Sentence                                     | 1364                                 | 3027                                |
| Company Entities                                             | 1704                                 | 4664                                |
| Unique Company Entities                                      | 897                                  | 1580                                |
| Number of Unique Company <br />Entities Exist in Training Set | Zero: 226<br/>One: 472<br/>More: 199 | Zero: 1440<br/>One: 49<br/>More: 91 |

The experiment results:



| Single Lexicon             | BCCWJ<br />F1(CRF) |            |            | Mainichi<br />F1(CRF) |            |            |
| -------------------------- | ------------------ | ---------- | ---------- | --------------------- | ---------- | ---------- |
|                            | Zero               | One        | More       | Zero                  | One        | More       |
| Gold                       | 0.4080             | 0.8211     | 0.9091     | 0.4970                | 0.8284     | 0.9353     |
| JCL-slim                   | 0.4748             | 0.8333     | 0.9091     | 0.5345                | 0.8075     | **0.9509** |
| JCL-meidum                 | 0.4530             | **0.8660** | 0.9091     | 0.5151                | 0.8061     | 0.9503     |
| JCL-full                   | **0.5411**         | 0.8333     | 0.8933     | **0.5630**            | 0.8467     | 0.9476     |
| Juman                      | 0.4506             | 0.7957     | 0.9032     | 0.5113                | **0.8655** | 0.9431     |
| IPAdic                     | 0.4926             | 0.8421     | **0.9161** | 0.5369                | 0.8633     | 0.9419     |
| NEologd                    | 0.4382             | 0.8454     | 0.9161     | 0.5343                | 0.8456     | 0.9359     |
| **Multiple Lexicon**       |                    |            |            |                       |            |            |
| IPAdic-NEologd             | 0.5276             | **0.8600** | 0.9091     | **0.5556**            | **0.8623** | 0.9432     |
| IPAdic-NEologd-JCL(medium) | **0.5198**         | 0.8421     | 0.8947     | 0.5484                | 0.8487     | **0.9476** |





From the result above, we can see JCLdic boost the zero-shot and one-shot performance a lot, especially on the BCCWJ dataset.


<!-- ### (Extra) Dictionary feature for low frequency company names on entity level

We could further divide these 3 categories to 6 categories:


| Category | Description                                                   | Evaluation                                    |
| -------- | ------------------------------------------------------------ | --------------------------------------------- |
| 0-1      | Not shown in training set, but only shown once in test set   | Zero-shot, performance on unseen entity       |
| 0-2      | Not shown in training set, but shown more than 2 times in test set | Zero-shot, performance on unseen entity       |
| 1-1      | Shown once in training set, and also shown once in test set  | One-shot, performance on low frequency entity |
| 1-2      | Shown once in training set, and shown more than 2 times in test set | One-shot, performance on low frequency entity |
| 2-1      | Shown more than 2 times in training set, but only shown once in test set | Training on normal data                       |
| 2-2      | Shown more than 2 times in training set, and also shown more than 2 times in test set | Training on normal data                       |






| Single Lexicon             | BCCWJ<br />F1(CRF) |            |            |            |            |        |
| -------------------------- | ------------------ | ---------- | ---------- | ---------- | ---------- | ------ |
|                            | 0-1                | 0-2        | 1-1        | 1-2        | 2-1        | 2-2    |
| Gold                       | 0.6512             | 0.6880     | 0.9091     | 0.8197     | 0.8387     | 0.9173 |
| JCL-slim                   | 0.6931             | 0.6753     | 0.9032     | 0.8182     | 0.8387     | 0.8714 |
| JCL-meidum                 | 0.6872             | 0.6438     | **0.9091** | **0.8485** | **0.8387** | 0.8905 |
| JCL-full                   | **0.7097**         | 0.6842     | 0.8571     | 0.7879     | 0.8276     | 0.8406 |
| Juman                      | 0.6413             | 0.7059     | 0.9032     | 0.8000     | 0.8387     | 0.8611 |
| IPAdic                     | 0.6802             | **0.7081** | 0.9032     | 0.8060     | 0.8387     | 0.8671 |
| NEologd                    | 0.6630             | 0.6621     | **0.9091** | 0.8060     | 0.8387     | 0.8732 |
| **Multiple Lexicon**       |                    |            |            |            |            |        |
| IPAdic-NEologd             | 0.6957             | **0.6957** | **0.9143** | **0.8308** | 0.8387     | 0.8299 |
| IPAdic-NEologd-JCL(medium) | **0.7440**         | 0.6914     | 0.8824     | 0.8254     | 0.8387     | 0.8741 |






For BCCWJ dataset, after adding dictionary features, JCL-full boosts the f1 from 0.6512 to 0.7097 for 0-1.




| Single Lexicon             | Mainichi<br />F1(CRF) |            |            |            |            |            |
| -------------------------- | --------------------- | ---------- | ---------- | ---------- | ---------- | ---------- |
|                            | 0-1                   | 0-2        | 1-1        | 1-2        | 2-1        | 2-2        |
| Gold                       | 0.4837                | 0.3848     | 0.4921     | 0.5862     | 0.5354     | 0.5881     |
| JCL-slim                   | 0.4831                | **0.4244** | 0.4974     | 0.5702     | 0.5344     | **0.5885** |
| JCL-meidum                 | 0.4784                | 0.4043     | 0.5109     | 0.5780     | **0.5385** | 0.5857     |
| JCL-full                   | 0.4959                | 0.4169     | **0.5204** | 0.5785     | 0.5217     | 0.5845     |
| Juman                      | 0.4978                | 0.3777     | 0.4813     | **0.6111** | 0.5211     | 0.5842     |
| IPAdic                     | 0.4920                | 0.3890     | 0.4923     | 0.5992     | 0.5275     | 0.5760     |
| NEologd                    | **0.5052**            | 0.3832     | 0.5000     | 0.5917     | 0.5267     | 0.5805     |
| **Multiple Lexicon**       |                       |            |            |            |            |            |
| IPAdic-NEologd             | 0.5069                | 0.4000     | 0.5078     | **0.5827** | 0.5191     | 0.5778     |
| IPAdic-NEologd-JCL(medium) | **0.5072**            | **0.4115** | **0.5078** | 0.5774     | **0.5308** | 0.5799     |




For Mainichi dataset, after adding dictionary features, JCL-slim boosts the f1 from 0.3848 to 0.4244 for 0-2, and JCL-full boosts the f1 from 0.4921 to 0.5204.  -->


## Citation

Please use the following bibtex, when you refer JCLdic from your papers.

```
@INPROCEEDINGS{liang2020jcldic,
    author    = {Xu Liang, Taniguchi Yasufumi and Nakayama Hiroki},
    title     = {High Coverage Lexicon for Japanese Company Name Recognition},
    booktitle = {Proceedings of the Twenty-six Annual Meeting of the Association for Natural Language Processing},
    year      = {2020},
    pages     = {NLP2020-B2-3},
    publisher = {The Association for Natural Language Processing},
}
```

