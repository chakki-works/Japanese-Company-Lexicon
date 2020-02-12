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

<!-- Make sure the `main.py` has following setting:

```python
# main.py setting
entity_level = True 
# ...
### result 3 ###
# bccwj: evaluate on low frequency compnay names 
main(bccwj_paths, bccwj_glod, entity_level=entity_level, low_frequency=bccwj_counter)
# mainichi: evaluate on low frequency compnay names
main(mainichi_paths, mainichi_glod, entity_level=entity_level, low_frequency=mainichi_counter)

### result 4 ###
# bccwj: evaluate on low frequency compnay names, use dictionary as feature for CRF
crf_tagged_pipeline(bccwj_paths, bccwj_glod, entity_level=entity_level, low_frequency=bccwj_counter)
# mainichi: evaluate on low frequency compnay names, use dictionary as feature for CRF
crf_tagged_pipeline(mainichi_paths, mainichi_glod, entity_level=entity_level, low_frequency=mainichi_counter) 
```

Run the below command:

```
python main.py
``` -->

We frist divide the result into 3 categories:


| Category | Desciption                                       | Evaluation                                    |
| -------- | ------------------------------------------------ | --------------------------------------------- |
| 0        | the entity not exist in the training set         | Zero-shot, performance on unseen entity       |
| 1        | the entity only exists once in the training set  | One-shot, performance on low frequency entity |
| 2        | the entity exists many times in the training set | Training on normal data                       |




| Single Lexicon             | BCCWJ<br />F1(CRF) |            |        | Mainichi<br />F1(CRF) |            |        |
| -------------------------- | ------------------ | ---------- | ------ | --------------------- | ---------- | ------ |
|                            | 0                  | 1          | 2      | 0                     | 1          | 2      |
| Gold                       | 0.6667             | 0.8511     | 0.9024 | 0.4396                | 0.5437     | 0.5828 |
| JCL-slim                   | 0.6854             | 0.8454     | 0.8655 | 0.4570                | 0.5372     | 0.5829 |
| JCL-meidum                 | 0.6686             | **0.8687** | 0.8810 | 0.4452                | 0.5473     | 0.5808 |
| JCL-full                   | **0.6978**         | 0.8119     | 0.8383 | **0.4603**            | 0.5525     | 0.5783 |
| Juman                      | 0.6706             | 0.8352     | 0.8571 | 0.4436                | **0.5558** | 0.5778 |
| IPAdic                     | 0.6927             | 0.8367     | 0.8621 | 0.4462                | 0.5531     | 0.5709 |
| NEologd                    | 0.6626             | 0.8400     | 0.8671 | 0.4514                | 0.5509     | 0.5750 |
| **Multiple Lexicon**       |                    |            |        |                       |            |        |
| IPAdic-NEologd             | 0.6957             | **0.8600** | 0.8315 | 0.4593                | **0.5503** | 0.5719 |
| IPAdic-NEologd-JCL(medium) | **0.7209**         | 0.8454     | 0.8675 | **0.4649**            | 0.5463     | 0.5749 |


From the result above, we can see JCLdic boost the zero-shot and one-shot performance a lot, especially on the BCCWJ dataset.




We could further divide these 3 categories to 6 categories:


| Category | Desciption                                                   | Evaluation                                    |
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




For Mainichi dataset, after adding dictionary features, JCL-slim boosts the f1 from 0.3848 to 0.4244 for 0-2, and JCL-full boosts the f1 from 0.4921 to 0.5204. 


## Citation

Release after March...
