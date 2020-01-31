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

### Dictionary annotation as feature

Add dictionary annotation as CRF features. Uncomment below scirpt in the `main.py` and run `python main.py`.

```python
# # use dictionary as feature for CRF
# data_dir = os.path.join(ROOT_DIR, 'data/corpora/output/*.bio')
# data_paths = glob.glob(data_dir) 
# data_paths = sorted(data_paths, key=lambda x: len(x))

# # bccwj  
# bccwj_paths = [x for x in data_paths if 'bccwj' in x]
# bccwj_glod = os.path.join(ROOT_DIR, 'data/corpora/output/bccwj.bio') 
# crf_tagged_pipeline(bccwj_paths, bccwj_glod)

# # mainichi
# mainichi_paths = [x for x in data_paths if 'mainichi' in x] 
# mainichi_glod = os.path.join(ROOT_DIR, 'data/corpora/output/mainichi.bio')     
# crf_tagged_pipeline(mainichi_paths, mainichi_glod) 
```

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


### Remove the company names that only appeard once, increase the coverage


Dataset: 


| Dataset                                  | Mainichi | BCCWJ |
| ---------------------------------------- | -------- | ----- |
| Company Samples/Sentence                 | 3027     | 1364  |
| Company Entities                         | 4664     | 1704  |
| Unique Company Entities                  | 1580     | 897   |
| Company Names that Appeared Only Once    | 934      | 604   |
| Duplicated Company Names                 | 3730     | 1100  |
| Company Names that need to be recognized | 646      | 293   |


Remove the company names tha appeared only once. The result formant is `result1 (result3)`:

- `result1` : train the data on the labels that tagged by dictionary
- `result3` : train the data on the labels that tagged by dictionary, remove the company names that only appear once (increase the coverage)


| **Single Lexicon**         | Mainichi   |                     | BCCWJ     |                     |
| -------------------------- | ---------- | ------------------- | --------- | ------------------- |
|                            | Count      | Coverage            | Count     | Coverage            |
| Gold                       | 1580 (646) |                     | 897 (293) |                     |
| JCL-slim                   | 727 (313)  | 0.4601 (0.4845)     | 419 (164) | 0.4671 (0.5597)     |
| JCL-medium                 | 730 (315)  | 0.4620 (0.4876)     | 422 (165) | 0.4705 (0.5631)     |
| JCL-full                   | 805 (365)  | **0.5095** (0.5650) | 487 (201) | **0.5429** (0.6860) |
| IPAdic                     | 726 (414)  | 0.4595 (0.6409)     | 316 (148) | 0.3523 (0.5051)     |
| Juman                      | 197 (140)  | 0.1247 (0.2167)     | 133 (79)  | 0.1483 (0.2696)     |
| NEologd                    | 424 (212)  | 0.2684 (0.3282)     | 241 (101) | 0.2687 (0.3447)     |
| **Multiple Lexicon**       |            |                     |           |                     |
| IPAdic-NEologd             | 839 (446)  | 0.5310 (0.6904)     | 421 (180) | 0.4693 (0.6143)     |
| IPAdic-neologd-JCL(medium) | 1064 (497) | **0.6734** (0.7693) | 568 (220) | **0.6332** (0.7782) |


The NER task result.



- `result1` : train the data on the labels that tagged by dictionary
- `result2` : add the dictionary tag as feature for CRF, use the true label for training
- `result3` : train the data on the labels that tagged by dictionary, remove the company names that only appear once (increase the coverage)
- `result4` : remove the company names that only appear once, but add the dictionary tag as feature for CRF, use the true label for training (increase the coverage)




| Single Lexicon             | Mainichi F1 (CRF) | Mainichi F1 (CRF) | Mainichi F1 (CRF) | Mainichi F1 (CRF) | BCCWJ F1 (CRF) | BCCWJ F1 (CRF) | BCCWJ F1 (CRF) | BCCWJ F1 (CRF) |
| -------------------------- | ----------------- | ----------------- | ----------------- | ----------------- | -------------- | -------------- | -------------- | -------------- |
|                            | Result1           | Result2           | Result3           | Result4           | Result1        | Result2        | Result3        | Result4        |
| Gold                       | 0.9756            | 1                 | 0.9749            | 1                 | 0.9273         | 1              | 0.9260         | 1              |
| JCL-slim                   | 0.8533            | 0.9754            | 0.9310            | 0.9769            | 0.8506         | 0.9339         | 0.8575         | 0.9412         |
| JCL-meidum                 | 0.8517            | 0.9752            | 0.9325            | **0.9771**        | 0.8501         | 0.9303         | 0.8562         | 0.9412         |
| JCL-full                   | 0.5264            | **0.9764**        | **0.9470**        | 0.9770            | 0.5646         | **0.9364**     | **0.8833**     | **0.9458**     |
| Juman                      | 0.8865            | 0.9754            | 0.9282            | 0.9758            | 0.8320         | 0.9276         | 0.8444         | 0.9301         |
| IPAdic                     | **0.9048**        | 0.9758            | 0.9418            | 0.9757            | **0.8646**     | 0.9299         | 0.8555         | 0.9281         |
| NEologd                    | 0.8975            | 0.9750            | 0.9237            | 0.9744            | 0.8453         | 0.9282         | 0.8429         | 0.9296         |
| **Multiple Lexicon**       |                   |                   |                   |                   |                |                |                |                |
| IPAdic-NEologd             | **0.8911**        | **0.9767**        | 0.9449            | 0.9760            | **0.8624**     | **0.9366**     | 0.8589         | 0.9367         |
| IPAdic-NEologd-JCL(medium) | 0.8335            | 0.9759            | **0.9532**        | **0.9777**        | 0.8530         | 0.9334         | **0.8724**     | **0.9425**     |



After removing the company names, the coverage increases, and the f1 is also increased (`result1->result3`). Another finding is that after we add dictionary features (`result4`), the reuslt is pretty colose to the `result2`, which means that even if we delete the company names that only appear once, we can still get a good performance if we add the dictionary features.


## Citation

Release after March...
