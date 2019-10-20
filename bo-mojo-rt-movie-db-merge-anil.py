"""
The code below cleans and merges movie data files from three sources:
    Box Office Mojo
    Rotten Tomatoes
    The Movie DB
"""

import pandas as pd
data_directory = '/Users/flatironschol/fis_projects/Data/'  
df_bom = pd.read_csv(data_directory+'bom.movie_gross.csv.gz') #Source: Box Office Mojo
df_rt_movies = pd.read_csv(data_directory+'rt.movie_info.tsv.gz', delimiter = '\t') #Source: Rotten tomatoes
df_rt_reviews = pd.read_csv(data_directory+'rt.reviews.tsv.gz', delimiter = '\t', encoding = 'cp437') #Source: Rotten tomatoes 
df_tmdb = pd.read_csv(data_directory+'tmdb.movies.csv.gz') # Source: MovieDB
df_tn = pd.read_csv(data_directory+'tn.movie_budgets.csv.gz') # Source: MovieDB

# The function cleans the two Movie DB dataframes
def df_clean(data_frame, release_date_column, movie_title_column):
    data_frame.drop_duplicates(keep = 'first', inplace = True)
    data_frame[release_date_column] = pd.to_datetime(data_frame[release_date_column]).dt.to_period("M") # Assume that movies released in the same month of the same year are the same.
    data_frame[movie_title_column] = [" ".join(title.upper().split()) for title in data_frame[movie_title_column]] # Remove whitespaces
    data_frame[movie_title_column] = [title.replace('Â', "'") for title in data_frame[movie_title_column]] 
    data_frame[movie_title_column] = [title.replace('#', '') for title in data_frame[movie_title_column]] 
    data_frame[movie_title_column] = [title.replace('"', '') for title in data_frame[movie_title_column]]               
    data_frame.drop_duplicates([movie_title_column, release_date_column], keep = False, inplace = True)
    data_frame.sort_values(by = [release_date_column, movie_title_column], ascending = [False, True], inplace = True)
    data_frame.rename(columns={release_date_column: 'release_date', movie_title_column: 'title'}, inplace = True)
    return data_frame
    
# Merge the two Movie DB dataframes
df_tmdb.drop('Unnamed: 0', axis = 1, inplace = True) # This is an extra index column
df_tmdb = df_clean(df_tmdb, 'release_date', 'title')
df_tn = df_clean(df_tn, 'release_date', 'movie')
df = pd.merge(df_tmdb, df_tn, how = 'outer', \
              left_on = ['title', 'release_date'], \
              right_on = ['title', 'release_date'], \
              indicator = True, validate="one_to_one", \
              sort = True)
