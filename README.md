# Japanese Company Lexicon (JCL)

The high coverage lexicon for Japanese company recognition.

## Download links

We provide two kinds of format. The **CSV** format contains one name per line, and the [MeCab format](https://gist.github.com/Kimtaro/ab137870ad4a385b2d79) contains one record per line:


- JCL_slim (7067216, [CSV](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_slim.csv.zip), [MeCab](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_slim.dic.zip)): no furigana, no extra enNames, no ditital names, the name length is longer than 2 and shorter than 30.
- JCL_medium (7555163, [CSV](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_medium.csv.zip), [MeCab](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_medium.dic.zip)): no ditital names, the name length is longer than 2 and shorter than 30. 
- JCL_full (8491326, [CSV](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_full.csv.zip), [MeCab](https://s3-ap-northeast-1.amazonaws.com/chakki.jcl.jp/public/jcl_full.dic.zip)): without any limitation

Our goal is to build the enterprise knowledge graph, so we only consider the companies that conducts economic activity for commercial purposes. These companies are denoted as Stock Compay (株式会社), Limited Company (有限会社), and Limitted Liability Company (合同会社). 


The full version contains all kinds of names, including digits, one character  aliases, etc. These abnormal names will cause annotation error for NER task. We recommend use the JCL_medium version or JCL_slim version. 

These realease versions are easier to use than the version we used in the papaer. Considering the trade-off between dictionary size and searching performance, we delete zenkaku(全角) names and only perserve the hankaku(半角) names. For example, we delete `'株式会社ＫＡＤＯＫＡＷＡ'` but perseve `'株式会社KADOKAWA'`. If you deal with text with JCL, we recommend first normalize the text to hankaku format.

```python
import unicodedata

text = unicodedata.normalize('NFKC', text) # convert zenkaku to hankaku
```


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




## JCL Generation Process

Instead of downloading the data, you can even build the JCL lexicon from scratch by following the below instructions. 

### Data Preparation

```
# conda create -n jcl python=3.6
# source activate jcl
pip install -r requirements.txt
```

If you want to downlaod the data by Selenium, you have to download the ChromeDriver. First check your Chrome version, and then download the corresponding version of ChromeDriver from [here](https://chromedriver.chromium.org/downloads). 

Uncompressing ZIP file to get `chromedriver`, then move it to target directory:
```
cd $HOME/Downloads
unzip chromedriver_mac64.zip 
mv chromedriver /usr/local/bin
```

Downloading hojin data:
```bash
sh scripts/download.sh
```


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
│       ├── output            # processed JCL lexicon
│       └── zip               # downloaded hojin data
```

### JCL Generation

Generating alias
```bash
sh scripts/generate_alias.sh
```

Untill now, the JCL lexicon is prepared. 

If you want to get the MeCab format:
```
python tools/save_mecab_format.py
```

### Evaluation

Below result is based on the latest version of JCL, which might be different with the performance of the paper reported. 


#### Datasets, dicionaries, and annotated datasets preparation

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

# 2 Prepare dicionaries 
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

The extrinsic evaluation is using using the NER taks to measure different lexicon performance.  We annotate training set with different lexicons, train the model (CRF and Bi-LSTM-CRF), and test on the test set. The `Glod` means we train the model with true labels. The best result is highlighted. 

```
python main.py
```

Following table is the extrinsic evaluation result. The best result is highlighted. 


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



## Citation

Release after March...
