import pandas as pd
import numpy as np
from typing import Dict
import os
import pickle
import hashlib


class DataLoader:
    stocks_path: str
    stocksIDName_path: str

    __stocksNameID: Dict[str, str]
    __stocks_df: Dict[str, pd.DataFrame] = {}

    def __init__(
        self,
        stocks_path="../data/stocks/",  # 股票資料路徑
        stocksIDName_path="../data/taiwan_stock_info.csv",  # 股票代號與名稱路徑
    ):
        self.stocks_path = stocks_path
        self.stocksIDName_path = stocksIDName_path

    def load_stocks(self, cache: bool = False):
        stocksNameID_df = pd.read_csv(self.stocksIDName_path)
        stocksNameID_df = stocksNameID_df.set_index("stock_name")
        stocksNameID_df = stocksNameID_df.sort_index()
        stocksNameID_df = stocksNameID_df.dropna()
        stocksNameID_df = stocksNameID_df.astype(str)
        self.__stocksNameID = stocksNameID_df.to_dict()["stock_id"]
        print("股票代號與名稱載入完成!")

        if cache:
            if os.path.exists("../data/stocks.pkl"):
                with open("../data/stocks.pkl", "rb") as f:
                    self.__stocks_df = pickle.load(f)
                print("股票資料載入完成!")
                print("股票總數:", len(self.__stocks_df))
                return

        for filename in os.listdir(self.stocks_path):
            if filename.endswith(".csv"):
                stock_id = filename.split(".")[0]
                try:
                    stock_df = pd.read_csv(self.stocks_path + filename)
                except Exception as e:
                    continue
                stock_df = stock_df.set_index("date")
                stock_df.index = pd.to_datetime(stock_df.index)
                stock_df = stock_df.sort_index()
                stock_df = stock_df.dropna()
                stock_df = stock_df.astype(float)
                self.__stocks_df[stock_id] = stock_df
        with open("../data/stocks.pkl", "wb") as f:
            pickle.dump(self.__stocks_df, f)

        print("股票資料載入完成!")
        print("股票總數:", len(self.__stocks_df))

    def get_stocks_df(
        self,
        stock_id: str = "",
        stock_name: str = "",
        year: int = 0,
    ) -> pd.DataFrame:
        if stock_id == "" and stock_name == "":
            raise Exception("請輸入股票代號或名稱!")
        elif stock_id == "" and stock_name != "":
            stock_id = self.get_stocksID_ByName(stock_name)
        elif stock_id != "" and stock_name != "":
            raise Exception("請輸入股票代號或名稱!")

        if stock_id not in self.__stocks_df:
            raise Exception("股票代號不存在!")

        if year != 0:
            return self.__stocks_df[stock_id][
                self.__stocks_df[stock_id].index.year == year
            ]
        return self.__stocks_df[stock_id]

    def get_stocksID_ByName(self, stock_name: str) -> str:
        if stock_name not in self.__stocksNameID:
            raise Exception(f"股票名稱不存在! {stock_name}")
        return self.__stocksNameID[stock_name]

    def get_stock_Years_byID(self, stock_id: str) -> list:
        if stock_id not in self.__stocks_df:
            raise Exception("股票代號不存在!")
        return self.__stocks_df[stock_id].index.year.unique().tolist()

    def getAllStocksPreYear(
        self, cols: list[str], cols_deal: list[callable], cache: bool = True
    ) -> pd.DataFrame:
        try:
            if cache:
                _id = hashlib.md5(str(cols).encode("utf-8")).hexdigest()
                if os.path.exists(f"../data/stocks_pre_year-{_id}.pkl"):
                    with open(f"../data/stocks_pre_year-{_id}.pkl", "rb") as f:
                        return pickle.load(f)
                else:
                    raise Exception("沒有快取檔案")
            else:
                raise
        except Exception as e:
            out = pd.DataFrame()
            for stock_id in self.__stocks_df:
                for year in self.get_stock_Years_byID(stock_id):
                    temp_row = {
                        "stock_id": stock_id,
                        "year": str(year),
                    }

                    tmp = self.get_stocks_df(stock_id=stock_id, year=year)
                    print(stock_id, year, tmp.shape)
                    try:
                        for col, col_deal in zip(cols, cols_deal):
                            if col not in tmp.columns:
                                raise Exception(f"股票代號: {stock_id} 沒有 {col} 欄位")
                            if col_deal is not None:
                                temp_row[col] = col_deal(tmp)
                            else:
                                temp_row[col] = tmp[col].iloc[-1]  # 最後一筆
                    except Exception as e:
                        print(e)
                        continue
                    out = pd.concat([out, pd.DataFrame([temp_row])], ignore_index=True)
            if cache:
                with open(f"../data/stocks_pre_year-{_id}.pkl", "wb") as f:
                    pickle.dump(out, f)
        return out


if __name__ == "__main__":
    dl = DataLoader()
    dl.load_stocks(cache=True)
    print(
        dl.getAllStocksPreYear(
            cols=["equity", "ROE", "ROA"], cols_deal=[None, None, None]
        )
    )
