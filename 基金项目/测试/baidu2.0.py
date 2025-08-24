import requests
from bs4 import BeautifulSoup
url = 'https://www.baidu.com/s'
params = {'wd': 'Python'}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(url, params=params, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
results = soup.find_all('h3', class_='t')
num=0
for result in results:
    title = result.get_text()
    link = result.a['href']
    num+=1
    print(f'{num}、标题: {title}\n链接: {link}\n')