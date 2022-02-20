from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import csv 
from sqlalchemy import create_engine


def return_dataframe_best_pictures(urls):
    list_dfs = []
    
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features="html.parser")

        movies = soup.select('div.lister-item-content')
        title = [a.get_text() for a in soup.select('h3.lister-item-header a')]
        runtime = [a.get_text().split(' ')[0] for a in soup.select('p.text-muted span.runtime')]
        genre = [a.get_text() for a in soup.select('p.text-muted span.genre')]
        year = [a.get_text() for a in soup.select('h3 span.lister-item-year')]

        description = [a.get_text() for a in soup.select('p.text-muted')]
        names = [a.get_text() for a in soup.select('p') if 'Stars:' in a.get_text()]
        names = [n.replace('\n', '').replace('|',',').replace('Director:', '').replace('Directors:', '').\
            replace('Stars:', '').replace("    ", "") for n in names]
        
        cols = ['Movie Title', 'Year', 'Runtime', 'Genre 1', 'Genre 2', 'Genre 3', 'Description',\
             'Director', 'Actor 1', 'Actor 2', 'Actor 3', 'Actor 4']
        df = pd.DataFrame(columns=cols, index=range(0, len(movies)))
        
        for index in range(0, len(movies)):
            df.iloc[index]['Movie Title'] = title[index] 
            df.iloc[index]['Year'] = year[index][-5:].replace(')', '')
            df.iloc[index]['Runtime'] = runtime[index]
            df.iloc[index]['Description'] = description[index * 2 + 1].replace('\n', '')
            
            df.iloc[index]['Director'] = names[index].split(',')[0]
            df.iloc[index]['Actor 1'] = names[index].split(',')[-4]
            df.iloc[index]['Actor 2'] = names[index].split(',')[-3]
            df.iloc[index]['Actor 3'] = names[index].split(',')[-2]
            df.iloc[index]['Actor 4'] = names[index].split(',')[-1]

            l_genres = genre[index].replace('\n', '').replace(" ","").split(',')
            len_gen = len(l_genres)

            df.iloc[index]['Genre 1'] = l_genres[0] 
            df.iloc[index]['Genre 2'] = l_genres[1] if len_gen > 1 else np.NaN
            df.iloc[index]['Genre 3'] = l_genres[2] if len_gen > 2 else np.NaN

        list_dfs.append(df)

    return pd.concat(list_dfs, ignore_index=True)


def save_dataset_csv(df, filename):
    df.to_csv(filename, sep=',', index=False, quoting=csv.QUOTE_ALL)


def save_dataset_db(df, conn_string, table_name):
    # conn_string = 'postgresql://user:password@host/database'

    db = create_engine(conn_string)
    conn = db.connect()

    df.to_sql(table_name, con=conn, if_exists='replace', index=False)
    conn.close()


if __name__ == '__main__':
    url_win = ['https://www.imdb.com/search/title/?groups=best_picture_winner&sort=year,desc&count=100&view=advanced']
    url_nom = ['https://www.imdb.com/search/title/?groups=oscar_best_picture_nominees&sort=year,desc&count=200&view=advanced',
                'https://www.imdb.com/search/title/?groups=oscar_best_picture_nominees&sort=year,desc&count=200&start=201&ref_=adv_nxt',
                'https://www.imdb.com/search/title/?groups=oscar_best_picture_nominees&sort=year,desc&count=200&start=401&ref_=adv_nxt']
    

    df_win = return_dataframe_best_pictures(url_win)
    df_nom = return_dataframe_best_pictures(url_nom)

    save_dataset_csv(df_win, 'oscar_best_pictures_winners.csv')
    save_dataset_csv(df_nom, 'oscar_best_pictures_nominees.csv')

    print(df_win.shape)
    print(df_nom.shape)

    conn_string = 'postgresql://postgres:root@localhost/imdb'
    # conn_string = 'postgresql://user:password@host/database'

    save_dataset_db(df_win, conn_string,'tb_oscar_best_pictures_winners')
    save_dataset_db(df_nom, conn_string,'tb_oscar_best_pictures_nominees')

