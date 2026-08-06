import os
import requests
from dotenv import load_dotenv

load_dotenv()


class NewsService:

    def get_news(self):
        print("INSIDE GET_NEWS")
        api_key = os.getenv("NEWS_API_KEY")

        if not api_key:
            return {
                "error": "NEWS_API_KEY not found in .env file"
            }

        url= (
           "https://newsapi.org/v2/everything?"
           "q=Nifty OR Sensex OR NSE OR BSE&"
           "language=en&"
           "sortBy=publishedAt&"
           "pageSize=5&"
          f"apiKey={api_key}"
          )

        try:
            response = requests.get(url, timeout=10)


            print("STATUS CODE:", response.status_code)
            print("RESPONSE:", response.text)

            if response.status_code != 200:
                return {
                    "error": "Unable to fetch news",
                    "status_code": response.status_code,
                    "details": response.json()
                }

            data = response.json()
            print(data)

            news_list = []
            print("Articles:", len(data.get("articles", [])))
            for article in data.get("articles", []):

                news_list.append({
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "source": article.get("source", {}).get("name"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt")
                })

            return news_list

        except requests.exceptions.RequestException as e:
            return {
                "error": "Network error while fetching news",
                "details": str(e)
            }

        except Exception as e:
            return {
                "error": "Unexpected error",
                "details": str(e)
            }