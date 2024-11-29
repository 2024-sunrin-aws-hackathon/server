import requests
from bs4 import BeautifulSoup    

def get_news_from_ytn(keyword):
    url = "https://www.ytn.co.kr/search/index.php?q="+keyword
    
    news_list = []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    news_url_list = [link.get('href') for link in soup.find("div", class_="searchMain").select("div.search_news_list a")]

    for i in range(5):
        news_url = news_url_list[i]
        response = requests.get(news_url)
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h2",class_="news_title").text
        content = soup.find("div",class_="content").text.strip().replace("\n","").replace("\t","").replace("\r","")

        if not content or len(content) > 2000:
            pass
        else:
            news_list.append({
                "url": news_url,
                "title": title,
                "content": content
            })
    
    return news_list

def get_all_news(keyword):
    news_list = []
    news_list.append({
        "ytn": get_news_from_ytn(keyword)
    })
    return news_list