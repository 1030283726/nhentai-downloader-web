# 使用最新 Python 映像
FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

# 複製依賴檔案並安裝
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用所有檔案
COPY . .

# 設定環境變數（與程式中一致）
ENV NHENTAI_PASSWORD=admin
ENV DOWNLOAD_PATH=/nhentai

# 對外開放 Flask 預設埠
EXPOSE 61234

# 啟動應用
CMD [ "python", "nhentai.py" ]
