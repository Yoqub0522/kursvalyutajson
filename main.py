from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

app = FastAPI(title="USD Bank Rates API")

URL = "https://kurs.uz/uz"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def parse_int(text: str):
    if not text:
        return None
    numbers = re.sub(r"[^\d]", "", text)
    return int(numbers) if numbers else None

def scrape_usd_rates():
    res = requests.get(URL, headers=HEADERS, timeout=15)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.find("table")
    if not table:
        raise HTTPException(status_code=500, detail="Jadval topilmadi")

    rows = table.select("tbody tr")
    banks = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            bank = cols[0].get_text(strip=True)

            buy_text = cols[1].get_text(strip=True)
            sell_text = cols[2].get_text(strip=True)

            banks.append({
                "bank": bank,
                "buy": parse_int(buy_text),
                "sell": parse_int(sell_text)
            })

    return banks

@app.get("/api/usd")
def usd_rates():
    return {
        "currency": "USD",
        "updated_at": datetime.now().isoformat(),
        "banks": scrape_usd_rates()
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

#http://127.0.0.1:8000/api/usd
 #uvicorn main:app --reload
