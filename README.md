# Japanese Company Lexicon (JCL)

The high coverage lexicon for Japanese company recognition.

Release soon !!!


```
# conda create -n jcl python=3.6
# source activate jcl
pip3 install -r requirements.txt
```

If you want to downlaod the data by Selenium, you have to download the ChromeDriver. First check your Chrome version, and then download the corresponding version of ChromeDriver from [here](https://chromedriver.chromium.org/downloads). 

Uncompressing ZIP file to get `chromedriver`, then move it to target directory:
```
cd $HOME/Downloads
unzip chromedriver_mac64.zip 
mv chromedriver /usr/local/bin
```

Preparing data:
```
sh download.sh
```


