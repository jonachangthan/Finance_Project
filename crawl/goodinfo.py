
import requests
from bs4 import BeautifulSoup
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.150 Safari/537.36"
}
TIMEOUT = 50
prevCallTime = time.time()

def getHistoryEquityPreYear(stock_id: str,debug = False) -> dict[str, int]:
    if not debug:
        global prevCallTime
        while time.time() - prevCallTime < TIMEOUT:
            time.sleep(0.1)
        prevCallTime = time.time()

    try:
        refer = {
            "Referer": F"https://goodinfo.tw/tw/StockAssetsStatus.asp?STOCK_ID={stock_id}"
        }
        response = requests.post(F"https://goodinfo.tw/tw/StockAssetsStatus.asp?STOCK_ID={stock_id}", headers={**headers, **refer})
        #print(response.text)
        soup = BeautifulSoup(response.text, "html.parser")
        soup = soup.find("table", {"id": "tblDetail"})
        rows = soup.find_all("tr")
        data = {}
        for row in rows:
            try:
                cols = row.find_all("td")
                year = cols[0].text if 'Q' not in cols[0].text else "20" + cols[0].text.split("Q")[0]
                equity = float(str(cols[1].text.replace(",","")))
            except Exception as e:
                continue
            data[year] = equity
        return data
    except Exception as e:
        print("被擋了QQ")
        return None
    
if __name__ == '__main__':
    print(getHistoryEquityPreYear("1732",debug=True))
