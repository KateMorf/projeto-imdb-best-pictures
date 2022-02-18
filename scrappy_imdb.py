from urllib import response
from bs4 import BeautifulSoup
import requests
import re

#Download dos top 250 filmes 
url = 'http://www.imdb.com/chart/top'
response = requests.get(url)
soup = BeautifulSoup(response.text, features="html.parser")

movies = soup.select('td.titleColumn')
links = [a.attrs.get('href') for a in soup.select('td.titleColumn a')]
crew = [a.attrs.get('title') for a in soup.select('td.titleColumn a')]
ratings = [b.attrs.get('data-value') for b in soup.select('td.posterColumn span[name=ir]')]
votes = [b.attrs.get('data-value') for b in soup.select('td.ratingColumn strong')]

#cria uma lista vazia para salvar informação do filme
list = []

#Itera sobre os filmes extraídos
for index in range(0, len(movies)):
    
    #separa o filme em: 'place' (colocação), title (título) e year (ano)
    movie_string = movies[index].get_text()
    movie = (' '.join(movie_string.split()).replace('.', ''))
    movie_tile = movie[len(str(index))+1:-7]
    year = re.search('\((.*?)\)', movie_string).group(1)
    place = movie[:len(str(index))-len(movie)]

    data = {"movie_tile": movie_tile,
            "year": year,
            "place": place,
            "star_cast": crew[index],
            "rating": ratings[index],
            "vote": votes[index],
            "link": links[index]
            }
    list.append(data)

# print os detalhes do filme com as notas
for movie in list:
    print(movie['place'], '-', movie['movie_tile'], '('+movie['year']+') -',\
         'Starring:', movie['star_cast'], movie['rating'])