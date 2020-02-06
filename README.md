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

The new experiment results are in the parentheses. We use the dictionary annotation as CRF feature, and the best results are highlighted. The result shows that the dictionary feature boost the performance, especilly the JCL. 


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


### Dictionary feature for low frequence company names on entity level

Make sure the `main.py` has following setting:

```python
# main.py setting
entity_level = True 
# ...
### result 3 ###
# bccwj: evaluate on low frequency compnay names 
main(bccwj_paths, bccwj_glod, entity_level=entity_level, low_frequency=bccwj_counter)
# mainichi: evaluate on low frequency compnay names
main(mainichi_paths, mainichi_glod, entity_level=entity_level, low_frequency=bccwj_counter)

### result 4 ###
# bccwj: evaluate on low frequency compnay names, use dictionary as feature for CRF
crf_tagged_pipeline(bccwj_paths, bccwj_glod, entity_level=entity_level, low_frequency=bccwj_counter)
# mainichi: evaluate on low frequency compnay names, use dictionary as feature for CRF
crf_tagged_pipeline(mainichi_paths, mainichi_glod, entity_level=entity_level, low_frequency=mainichi_counter) 
```

Run the below command:

```
python main.py
```


The entity level result:

- `result3` : train the data on the labels that tagged by dictionary, evalue it on three kinds of frequency of company name. The `Once` means the company appears once in the whole dataset, The `Twice` means the company appears twiice, and the `More` means the company appears more than two times.
- `result4` : add the dictionary tag as feature for CRF, use the true label for training




| Single Lexicon             | BCCWJ<br />Accuracy(CRF) |            |         |            |         |            |
| -------------------------- | ------------------------ | ---------- | ------- | ---------- | ------- | ---------- |
|                            | Result3                  | Result4    | Result3 | Result4    | Result3 | Result4    |
|                            | Once                     | Once       | Twice   | Twice      | More    | More       |
| Gold                       | 0.3230                   |            | 0.4239  |            | 0.4977  |            |
| JCL-slim                   | 0.1801                   | 0.4037     | 0.2065  | 0.4348     | 0.2172  | 0.5339     |
| JCL-meidum                 | 0.2050                   | 0.3851     | 0.1957  | 0.4239     | 0.2262  | 0.5294     |
| JCL-full                   | 0.2050                   | **0.4534** | 0.3261  | **0.5217** | 0.3529  | **0.5475** |
| Juman                      | 0.0062                   | 0.3416     | 0.0326  | 0.4565     | 0.0769  | 0.5204     |
| IPAdic                     | 0.0373                   | 0.3975     | 0.1304  | 0.4674     | 0.1538  | 0.5475     |
| NEologd                    | 0.0124                   | 0.3478     | 0.0543  | 0.4457     | 0.0950  | 0.5249     |
| **Multiple Lexicon**       |                          |            |         |            |         |            |
| IPAdic-NEologd             | 0.0745                   | 0.4286     | 0.1413  | 0.4891     | 0.1674  | **0.5747** |
| IPAdic-NEologd-JCL(medium) | 0.2919                   | **0.4534** | 0.2826  | **0.4891** | 0.4072  | 0.5204     |


For BCCWJ dataset, after adding dictionary features, JCL-full boosts the accuracy from 0.3230 to 0.4534 for `Once` company, boosts the accuracy from 0.4239 to 0.5217 for `Twice` company, and boosts the accuracy from 0.4977 to 0.5475 for `Once` company. Especially for the `Once` and `Twice` companies, JCL-full shows good performance compaaring with the multiple lexicon.




| Single Lexicon             | Mainichi<br />Accuracy (CRF) |            |         |            |         |            |
| -------------------------- | ---------------------------- | ---------- | ------- | ---------- | ------- | ---------- |
|                            | Result3                      | Result4    | Result3 | Result4    | Result3 | Result4    |
|                            | Once                         | Once       | Twice   | Twice      | More    | More       |
| Gold                       | 0.3495                       |            | 0.5370  |            | 0.8514  |            |
| JCL-slim                   | 0.1972                       | 0.3633     | 0.2037  | 0.5741     | 0.2749  | 0.8641     |
| JCL-meidum                 | 0.2111                       | 0.3529     | 0.2407  | 0.5494     | 0.2834  | 0.8631     |
| JCL-full                   | 0.1869                       | 0.3910     | 0.2284  | **0.6049** | 0.3153  | **0.8705** |
| Juman                      | 0.0104                       | 0.3633     | 0.0123  | 0.5247     | 0.2176  | 0.8694     |
| IPAdic                     | 0.1073                       | **0.3945** | 0.1790  | 0.5864     | 0.4034  | 0.8641     |
| NEologd                    | 0.0484                       | 0.3910     | 0.0556  | 0.5617     | 0.1507  | 0.8556     |
| **Multiple Lexicon**       |                              |            |         |            |         |            |
| IPAdic-NEologd             | 0.1765                       | **0.4048** | 0.2469  | **0.6049** | 0.4660  | **0.8662** |
| IPAdic-NEologd-JCL(medium) | 0.3668                       | 0.3944     | 0.4321  | 0.5741     | 0.5807  | 0.8652     |


For Mainichi dataset, the result is basicly same with BCCWJ dataset. Dictionary features boost the performance a lot, especially for the `Once` and `Twice` companies. 


## Citation

Release after March...
