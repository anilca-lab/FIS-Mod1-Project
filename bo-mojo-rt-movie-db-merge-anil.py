#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The code below cleans and merges movie data files from two sources:
    IMDB
    The Movie DB
"""

import pandas as pd
data_directory = '/Users/flatironschol/fis_projects/Data/'  
# df_bom = pd.read_csv(data_directory+'bom.movie_gross.csv.gz') #Source: Box Office Mojo
# df_rt_movies = pd.read_csv(data_directory+'rt.movie_info.tsv.gz', delimiter = '\t') #Source: Rotten tomatoes
# df_rt_reviews = pd.read_csv(data_directory+'rt.reviews.tsv.gz', delimiter = '\t', encoding = 'cp437') #Source: Rotten tomatoes 
df_imdb_basics = pd.read_csv(data_directory+'imdb.title.basics.csv.gz') # Source: IMDB
df_imdb_ratings = pd.read_csv(data_directory+'imdb.title.ratings.csv.gz') # Source: IMDB
df_mdb_ratings = pd.read_csv(data_directory+'tmdb.movies.csv.gz') # Source: MovieDB
df_mdb_revenues = pd.read_csv(data_directory+'tn.movie_budgets.csv.gz') # Source: MovieDB

# The function cleans the two Movie DB dataframes
def df_clean(data_frame, release_date_column, movie_title_column):
    data_frame.drop_duplicates(keep = 'first', inplace = True)
    if data_frame[release_date_column].dtypes == 'int64':
        data_frame[release_date_column] = pd.to_datetime(data_frame[release_date_column], format = '%Y').dt.to_period("Y") # Assume that movies released in the same month of the same year are the same.
    else:
        data_frame['release_year_month'] = pd.to_datetime(data_frame[release_date_column]).dt.to_period("M") # Assume that movies released in the same month of the same year are the same.
        data_frame[release_date_column] = pd.to_datetime(data_frame[release_date_column]).dt.to_period("Y") # Assume that movies released in the same month of the same year are the same.
    data_frame[movie_title_column] = [" ".join(title.upper().split()) for title in data_frame[movie_title_column]] # Remove whitespaces
    data_frame[movie_title_column] = [title.replace('Â', "'") for title in data_frame[movie_title_column]] 
    data_frame[movie_title_column] = [title.replace('#', '') for title in data_frame[movie_title_column]] 
    data_frame[movie_title_column] = [title.replace('"', '') for title in data_frame[movie_title_column]]               
    data_frame.drop_duplicates([movie_title_column, release_date_column], keep = False, inplace = True)
    data_frame.sort_values(by = [release_date_column, movie_title_column], ascending = [False, True], inplace = True)
    data_frame.rename(columns={release_date_column: 'release_year', movie_title_column: 'title'}, inplace = True)
    return data_frame
    
# Merge Movie DB dataframes
df_mdb_ratings.drop('Unnamed: 0', axis = 1, inplace = True) # This is an extra index column
df_mdb_ratings = df_clean(df_mdb_ratings, 'release_date', 'title')
df_mdb_revenues = df_clean(df_mdb_revenues, 'release_date', 'movie')
df_mdb = pd.merge(df_mdb_ratings, df_mdb_revenues, how = 'outer', \
              left_on = ['title', 'release_year_month', 'release_year'], \
              right_on = ['title', 'release_year_month', 'release_year'], \
              indicator = True, validate="one_to_one", \
              sort = True)

# Merge IMDB dataframes
df_imdb_basics = df_clean(df_imdb_basics, 'start_year', 'primary_title')
df_imdb = pd.merge(df_imdb_basics, df_imdb_ratings, how = 'outer', \
              on = 'tconst', \
              indicator = True, validate="one_to_one")

# Merge Movie DB and IMDB dataframes
df = pd.merge(df_imdb.drop(columns = '_merge'), df_mdb.drop(columns = '_merge'), how = 'outer', \
              left_on = ['title', 'release_year'], \
              right_on = ['title', 'release_year'], \
              indicator = True, validate="many_to_many", \
              sort = True)
df_merged = df.loc[df._merge == 'both']

# Clean the merged dataframe
df_clean = df.drop(columns = ['tconst', 'original_title_x', 'runtime_minutes', 'id_x', 'original_language', 'original_title_y', 'id_y'])
df_clean_drop = df_clean.loc[(df_clean.numvotes.isna()) & (df_clean.vote_count.isna())]
df_clean = df_clean.drop(df_clean_drop.index)

df_clean.to_csv (data_directory+'export_df_clean.csv', index = None, header=True) 
