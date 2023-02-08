import requests
from twilio.rest import Client

from _private_keys import STOCK_API_KEY, NEWS_API_KEY, AUTH_TOKEN, MY_NUMBER, ACCOUNT_SID

# -------------------------------- GLOBAL VARIABLES -------------------------------- #
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"


# -------------------------------- STOCKS API -------------------------------- #

def get_company_stock_data():
    STOCK_API_URL = "https://www.alphavantage.co/query"
    stock_api_params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": STOCK,
        "apikey": STOCK_API_KEY,
    }

    response = requests.get(STOCK_API_URL, params=stock_api_params)
    response.raise_for_status()
    stock_data = response.json()

    last_two_days_data = [value["4. close"] for (key, value) in stock_data["Time Series (Daily)"].items()][:2]

    price_change_percentage = (1 - (float(last_two_days_data[0]) / float(last_two_days_data[1]))) * 100

    if abs(price_change_percentage) >= 5:
        get_company_news(price_change_percentage)


# -------------------------------- NEWS API -------------------------------- #
def get_company_news(price_change_percentage):
    NEWS_API_URL = "https://newsapi.org/v2/everything"
    news_api_params = {
        "q": COMPANY_NAME,
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY,
    }

    response = requests.get(NEWS_API_URL, params=news_api_params)
    response.raise_for_status()
    news_data = response.json()
    top_three_articles = news_data["articles"][:3]

    shorter_news = [{"headline": item["title"], "brief": item["description"]} for item in top_three_articles]

    send_notification(shorter_news, price_change_percentage)


# -------------------------------- WhatsApp NOTIFICATIONS  -------------------------------- #
def send_notification(articles, price_change_percentage):
    if price_change_percentage > 0:
        symbol = "🔺"
    else:
        symbol = "🔻"

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    for article in articles:
        message = client.messages.create(
            from_="whatsapp:+14155238886",
            body=f"{COMPANY_NAME}:{symbol} {round(abs(price_change_percentage))}%\n"
                 f"Headline: {article['headline']} ({STOCK})\n"
                 f"Brief: {article['brief']}",
            to=f"whatsapp:+{MY_NUMBER}"
        )
        print(message.sid)


get_company_stock_data()
