import requests
import beautifulsoup4

def get_news():
    
def get_news_from_mbc(keyword):
    url = "https://www.ytn.co.kr/search/index.php?q="+keyword

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    



