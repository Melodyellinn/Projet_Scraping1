## Installations (à décommenter si ce n'est pas déjà installé)
# pip install bs4 requests
# pip install pandas
# pip install numpy
# pip install requests

#Import librairies
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np


## 1ère partie du TP: Récupérer la première partie de l'information (titre, genre, date, durée) du site IMDb

url = "https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start="
language = {"Accept-Language": "en-US,en;q=0.5"}
pages = np.arange(1, 251, 50)

movies_data=[]

# Boucler sur les urls définies plus haut
for page in pages:
    data = requests.get(url + str(page) + '&ref_=adv_nxt', headers=language) #récupérer le html de la page
    soup =  BeautifulSoup(data.text, 'html.parser') #ajouter les données de la page html à BeautifulSoup
    
    # Boucler sur chaque div contenant les infos nécessaires (classe de la div = 'lister-item-content')
    for div in soup.find_all('div', { 'class' : 'lister-item-content' }):
        # Récupérer le titre et retirer les balises html
        title = div.find('a')
        title_text = title.text
        year = div.find("span", class_="lister-item-year").text #Récupérer l'année et retirer les balises html
        runtime = div.find('span', {'class':'runtime'}).text #Récupérer la durée et retirer les balises html
        genre = div.find('span', {'class':'genre'}).text.strip() #Récupérer le genre et retirer les balises html
        # ajouter les 4 éléments de chaque films dans une liste
        data_list = [title_text, year, runtime, genre]
        # ajouter tous les éléments des 50 films dans une liste
        movies_data.append(data_list)


data2 = pd.DataFrame(movies_data, columns = ['title', 'year_of_release', 'duration_in_minutes', 'genre'])
data2["duration_in_minutes"] = data2["duration_in_minutes"].str[:3].astype(int) #Supression des parenthèse autour de la date & et du mot "min" + conversion en int
data2["year_of_release"] = data2["year_of_release"].str[1:5]
data2.title = data2.title.apply(lambda x:x.replace(" ", "_")) #Remplacer l'espace par un _, pour s'adapter au site rottentomato 
data2.title = data2.title.apply(lambda x:x.replace("The_", "")) #Enlever le déterminant "the" des titres de films, pour s'adapter au site rottentomato 


## Ajout des scores de Rotten Tomatoes

df_found = data2.copy()

uri = 'https://www.rottentomatoes.com/m/'
urilist = []
scores_data=[] #Récupération du pop_corn Score
tomato_data=[] #Récupération du tomato score

#Modifications généralisables sur l'ensemble des not_found et quelques modifications à la main 
df_found.title = df_found.title.apply(lambda x:x.replace("ä", "a"))
df_found.title = df_found.title.apply(lambda x:x.replace("-", ""))
df_found.title = df_found.title.apply(lambda x:x.replace(".", ""))
df_found.title = df_found.title.apply(lambda x:x.replace(":", ""))
df_found.title = df_found.title.apply(lambda x:x.replace("'", ""))
df_found.title = df_found.title.apply(lambda x:x.replace(",", ""))
df_found.title = df_found.title.apply(lambda x:x.replace("Dark_Knight", "the_Dark_Knight"))
df_found.title = df_found.title.apply(lambda x:x.replace("Lord_of_the_Rings_Fellowship_of_the_Ring", "the_lord_of_the_rings_the_fellowship_of_the_ring"))
df_found.title = df_found.title.apply(lambda x:x.replace("In_the_Mood_for_Love", "in_the_mood_for_love_2001"))
df_found.title = df_found.title.apply(lambda x:x.replace("Lord_of_the_Rings_Return_of_the_King", "the_lord_of_the_rings_the_return_of_the_king"))


#Création d'une liste avec les differents liens pour nos films
for i in df_found["title"]:
    response = (f'{uri}{str(i)}')  
    urilist.append(response) 


# Boucler sur les urls définies plus haut
for url in urilist:
    # récupérer le html de la page
    pag = requests.get(url)
    #Vérifier si la page internet existe
    if pag.status_code == 200:
            
    # ajouter les données de la page html à BeautifulSoup   
        soup1 = BeautifulSoup(pag.content, "html.parser")
   
        audience = soup1.find("score-board")["audiencescore"]
    
        scores_data.append(audience)
        
    else: 
        audience = "Not found"
        
        scores_data.append(audience)

# Boucler sur les urls définies plus haut
for url in urilist:
    # récupérer le html de la page
    pag = requests.get(url)
    
    if pag.status_code == 200:
            
    # ajouter les données de la page html à BeautifulSoup   
        soup1 = BeautifulSoup(pag.content, "html.parser")
   
        audience = soup1.find("score-board")["tomatometerscore"]
    
        tomato_data.append(audience)
        
    else: 
        audience = "Not found"
        
        tomato_data.append(audience)

    
#Conversion de la liste en Df
df_scores_pop = pd.DataFrame(scores_data, columns=['pop_score'])
df_scores_tomato = pd.DataFrame(tomato_data, columns=['tomato_score'])

#Merge du l'index
df_in = df_found.merge(df_scores_tomato, how='inner', left_index=True, right_index=True)
df_clean = df_in.merge(df_scores_pop, how='inner', left_index=True, right_index=True)

#Conversion CSV pour visualiser sur powerBI
df_clean.to_csv('C:/Users/Utilisateur/Desktop/df_clean_BI.csv', index = False)