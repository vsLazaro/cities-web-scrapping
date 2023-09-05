from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import json
import os

class Movie:
    def __init__(self, title=None, year=None, poster_url=None, poster_img=None, rating=None, movie_url=None, genres=None, popularity=None, directors=None):
        self.title = title
        self.year = year
        self.poster_url = poster_url
        self.poster_img = poster_img
        self.rating = rating
        self.movie_url = movie_url
        self.genres = genres
        self.popularity = popularity
        self.directors = directors

# Inicializar o driver do navegador (por exemplo, Chrome)
driver = webdriver.Chrome()

try:
    # URL da página com a lista dos 250 filmes mais bem avaliados no IMDb
    url = 'https://www.imdb.com/chart/top/?ref_=nv_mv_250'

    # Carregar a página usando o Selenium
    driver.get(url)

    # Criar um objeto BeautifulSoup a partir do conteúdo da página carregada pelo Selenium
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Encontrar todas as entradas de filmes na página
    movie_entries = soup.select('ul.ipc-metadata-list li.ipc-metadata-list-summary-item')

    # Lista para armazenar objetos Movie
    movies = []

    # Loop através das entradas de filmes
    for movie_entry in movie_entries:
        # Extrair elementos relevantes para o filme
        title_element = movie_entry.select_one('div.ipc-title a.ipc-title-link-wrapper h3.ipc-title__text')
        year_element = movie_entry.select_one('div.sc-b85248f1-5 span.sc-b85248f1-6')
        poster_url_element = movie_entry.select_one('div.ipc-poster div.ipc-media img.ipc-image')
        rating_svg = movie_entry.select_one('span.ipc-rating-star svg.ipc-icon')
        movie_url_element = movie_entry.select_one('div.ipc-poster a.ipc-lockup-overlay')

        # Extrair dados do filme, considerando a possibilidade de elementos ausentes
        title = title_element.text if title_element else None
        year = year_element.text if year_element else None
        poster_url = poster_url_element.get('src') if poster_url_element else None
        rating = rating_svg.next_sibling if rating_svg else None
        movie_url = "https://www.imdb.com" + movie_url_element.get('href') if movie_url_element else None

        # Criar um objeto Movie com os dados extraídos e adicionar à lista
        movie = Movie(title=title, year=year, poster_url=poster_url, rating=rating, movie_url=movie_url)
        movies.append(movie)

    # Lista para armazenar objetos Movie com detalhes
    movies_with_details = []

    # Loop através das páginas de cada filme para obter mais dados
    for movie in movies:
        if movie.movie_url:
            try:
                # Acessar a página de cada filme
                driver.get(movie.movie_url)

                # Criar um objeto BeautifulSoup a partir do conteúdo da página carregada
                details_soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Extrair elementos adicionais para o filme
                genres_element = details_soup.select('a.ipc-chip span.ipc-chip__text')
                popularity_element = details_soup.select_one('div.sc-5f7fb5b4-0 div.sc-5f7fb5b4-1')
                directors_anchor = details_soup.select(
                    'div.sc-acac9414-3 li.ipc-metadata-list__item:first-child a.ipc-metadata-list-item__list-content-item'
                    )

                # Extrair dados adicionais do filme, considerando a possibilidade de elementos ausentes
                genres = [element.text for element in genres_element] if genres_element else None
                popularity = popularity_element.text if popularity_element else None
                directors = [element.text for element in directors_anchor] if directors_anchor else None
                
                # Criar um novo objeto Movie com os dados atualizados
                updated_movie = Movie(
                title=movie.title,
                year=movie.year,
                poster_url=movie.poster_url,
                rating=movie.rating,
                movie_url=movie.movie_url,
                genres=genres,
                popularity = popularity,
                directors = directors
                )
            
                # Adicionar os dados adicionais ao novo objeto Movie e adicionar à lista
                movies_with_details.append(updated_movie)
                    
            except Exception as e:
                print(f"Erro ao acessar a página de detalhes: {e}")

finally:
    # Fechar o driver do navegador, independentemente de sucesso ou erro
    driver.quit()

# Pasta para salvar as imagens
image_folder = 'movie_posters'
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Baixar e salvar as imagens
for index, movie in enumerate(movies_with_details, start=1):
    if movie.poster_url:
        try:
            response = requests.get(movie.poster_url)
            if response.status_code == 200:
                image_filename = f"{index}.jpg"
                image_path = os.path.join(image_folder, image_filename)

                with open(image_path, 'wb') as image_file:
                    image_file.write(response.content)
                
                movie.poster_img = image_path  # Atualizar o caminho da imagem no objeto Movie
                
                print(f"Imagem {image_filename} baixada com sucesso!")
            else:
                print(f"Falha ao baixar a imagem para {movie.title}. Status code: {response.status_code}")
        
        except Exception as e:
            print(f"Erro ao baixar a imagem para {movie.title}: {e}")

# Nome do arquivo JSON
json_file = 'top_250_movies.json'

# Serializar a lista de objetos Movie em um arquivo JSON
with open(json_file, 'w', encoding='utf-8') as f:
    movie_dicts = [
        {
            'title': movie.title,
            'year': movie.year,
            'poster_url': movie.poster_url,
            'poster_img': movie.poster_img,
            'rating': movie.rating,
            'movie_url': movie.movie_url,
            'genres': movie.genres,
            'popularity': movie.popularity,
            'directors': movie.directors
        }
        for movie in movies_with_details
    ]
    json.dump(movie_dicts, f, indent=4, ensure_ascii=False)

print("Dados serializados em JSON com sucesso!")