# Google_Search_Crawler

## 使用 Selenium 與 BeautifulSoup4 擷取 Google Search 的結果

![alt text](https://imgur.com/bGErFLn.png)
![alt text](https://imgur.com/iOpibo5.png)

## 教學

### 套件安裝

需要的套件已經包在 requirements.txt 的文字檔中，將此檔案放入專案路徑中，然後在終端機輸入以下指令即可

> 安裝套件之前請先確認你的環境有安裝 [Python 3.7.6](https://www.python.org/downloads/release/python-376/)
> msedge.selenium_tools 可依據個人需求決定是否安裝，如果你偏好使用 edge 的瀏覽器，則需要安裝此套件

```
pip install -r requirements.txt
```

### 執行範例

-   請先建立一個 crawler.ini 的設定檔

```
[Settings]
Crawler_Task=搜尋的關鍵字,搜尋種類,搜尋頁數 (如: 焦點新聞,news,5|Uru,video,10 . . .)
Output_Path=存放爬蟲擷取搜尋結果的路徑
Open_Browser=擷取搜尋結果時是否開啟瀏覽器頁面 (YES or NO)
Browser_Type=爬蟲使用的瀏覽器種類 (chrome or edge)
```

-   範例如下

```
[Settings]
Crawler_Task=刀劍神域,video,10|精靈幻想記,video,5|新冠肺炎,news,7|Omicron Taiwan,news,5
Output_Path=D:\Files\Project\Google_Search_Crawler\output
Open_Browser=NO
Driver_Path=D:\Files\Project\Google_Search_Crawler\driver\chromedriver.exe
Browser_Type=chrome
```

-   撈取一個 (以上) 不同類型的 Google Search 之結果
-   引數化指定 ini 設定檔的所在目錄
-   [crawler_google_search_args.py](https://github.com/hoshisakan/Google_Search_Crawler/blob/main/crawler_google_search_args.py) 這個檔案也已經放在 GitHub 專案目錄上，需要可自行取用
### 將 python 打包成一個 .exe 的可執行檔

> 打包的 python 檔是 [crawler_google_search.py](https://github.com/hoshisakan/Google_Search_Crawler/blob/main/crawler_google_search.py)

-   打包時請注意你的 python 環境是乾淨的，避免製作執行檔時將不必要的套件一同匯入，建議使用 [virtualenv](https://pypi.org/project/virtualenv/) 與 [virtualenvwrapper-win](https://pypi.org/project/virtualenvwrapper-win/) 將爬蟲的開發環境區別開來

```
pyinstaller.exe --specpath ./execute/ --distpath ./execute/dist --workpath ./execute/build --add-data "D:\Files\Project\Google_Search_Crawler\crawler.ini;." -D crawler_google_search.py
```

![alt text](https://imgur.com/EmSbRm5.png)

### 執行檔打包完成後，在 dist 的目錄中會看見 crawler.ini 與 crawler_google_search.exe

![alt text](https://imgur.com/MzFIyKz.png)

-   實際測試執行檔

### 執行畫面

![alt text](https://imgur.com/bGErFLn.png)
![alt text](https://imgur.com/FQdS4TX.png)
![alt text](https://imgur.com/72kJOCP.png)
![alt text](https://imgur.com/AEfNzb0.png)
![alt text](https://imgur.com/iOpibo5.png)

### 輸出資料夾

![alt text](https://imgur.com/CaKscoZ.png)

# 執行環境

-   Python 3.7.6
