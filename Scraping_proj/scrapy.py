#!/usr/bin/env python
# coding: utf-8

# ## Import modul and library

# In[1]:


from bs4 import BeautifulSoup
import requests
import pandas as pd


# ## Request page source from URL

# In[2]:


url = "https://www.imdb.com/search/title/?groups=top_250&sort=user_rating"

url_2 = "https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start=51&ref_=adv_nxt"

url_3 = "https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start=101&ref_=adv_nxt"

url_4 = "https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start=151&ref_=adv_nxt"

url_5 = "https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start=201&ref_=adv_nxt"

urls=[url, url_2, url_3, url_4, url_5]


# In[3]:


movies_data=[]

headers = {"Accept-Language": "en-US,en;q=0.5"}

# Boucler sur les urls définies plus haut
for url in urls:
    # récupérer le html de la page
    data = requests.get(url, headers=headers)
    
    # ajouter les données de la page html à BeautifulSoup
    soup =  BeautifulSoup(data.text, 'html.parser')
    
    # Boucler sur chaque div contenant les infos nécessaires (classe de la div = 'lister-item-content')
    for div in soup.find_all('div', { 'class' : 'lister-item-content' }):
        # Récupérer le titre et retirer les balises html
        title = div.find('a')
        title_text = title.text
        # Récupérer l'année et retirer les balises html
        year = div.find("span", class_="lister-item-year").text
        # Récupérer la durée et retirer les balises html
        runtime = div.find('span', {'class':'runtime'}).text
        # Récupérer le genre et retirer les balises html
        genre = div.find('span', {'class':'genre'}).text.strip()

        # ajouter les 4 éléments de chaque films dans une liste
        data_list = [title_text, year, runtime, genre]
        # ajouter tous les éléments des 50 films dans une liste
        movies_data.append(data_list)


# In[4]:


#création des colonnes
data2 = pd.DataFrame(movies_data, columns = ['Title', 'Year_of_release', 'Duration_in_minutes', 'Genre'])


# In[6]:


#remplacer
data2.Title = data2.Title.apply(lambda x:x.replace(" ", "_"))


# In[7]:


data2.Title = data2.Title.apply(lambda x:x.replace("The_", ""))


# ## Tomato score and audience score

# In[10]:


uri = 'https://www.rottentomatoes.com/m/'


# In[11]:


urilist = []
for i in data2["Title"]:
    response = (f'{uri}{str(i)}')
    urilist.append(response)


# In[19]:


score_data = []

for title in data2['Title']:
    changed_title = title.replace(" ", "_").replace("The_", "")
    url = f'{uri}{changed_title}'
    data = requests.get(url, headers=headers)
#Une condition pour éviter que la boucle s'arrête sur une erreur 404    
    if data.status_code == 404:
        score_list = ['not found', 'not_found']
        score_data.append(score_list)
#         print(score_data)
        continue
    else:
        soup_ = BeautifulSoup(data.text, 'html.parser') #s'il n'y a pas d'erreur il applique la fonction soup

        audience_score = soup_.find("score-board")["audiencescore"] #find sur les notes audiences balise "score-board"
        tomato_score = soup_.find("score-board")["tomatometerscore"] #find sur les notes tomatos balise "score-board"

        score_list = [tomato_score, audience_score] #list les scores

        score_data.append(score_list)
        
print(score_data)


# In[20]:


#création du df et nommer les colonnes
score_rotten = pd.DataFrame(score_data, columns=['Score_Tomatos', 'Score_Audience'])
score_rotten


# In[21]:


# merge les deux df
df_scraping = data2.merge(score_rotten, how='inner', left_index=True, right_index=True)


# In[ ]:




