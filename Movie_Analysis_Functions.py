#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file defines the functions used in the FIS Module 1 project.
The project aims to provide four actionable recommendations to Microsoft on
what type of movies Microsoft should produce with a new movie studio.  
"""
import pandas as pd
# This function cleans the two Movie DB dataframes by eliminating whitespaces
# from movie titles, converting them to uppercase, converting the release date
# column to date/time format, and extracting month and year information.
def df_clean(data_frame, release_date_column, movie_title_column):
    data_frame.drop_duplicates(keep = 'first', inplace = True)
    if data_frame[release_date_column].dtypes == 'int64':
        data_frame[release_date_column] = pd.to_datetime(data_frame[release_date_column], \
                                                         format = '%Y').dt.to_period("Y") 
    else:
        data_frame['release_year_month'] = pd.to_datetime(data_frame[release_date_column]).\
                                           dt.to_period("M")
        data_frame[release_date_column] = pd.to_datetime(data_frame[release_date_column]).\
                                          dt.to_period("Y")
    data_frame[movie_title_column] = [" ".join(title.upper().split()) \
                                      for title in data_frame[movie_title_column]]
    data_frame[movie_title_column] = [title.replace('Â', "'") \
                                      for title in data_frame[movie_title_column]] 
    data_frame[movie_title_column] = [title.replace('#', '') \
                                      for title in data_frame[movie_title_column]] 
    data_frame[movie_title_column] = [title.replace('"', '') \
                                      for title in data_frame[movie_title_column]]               
    data_frame.drop_duplicates([movie_title_column, release_date_column], \
                               keep = False, inplace = True)
    data_frame.sort_values(by = [release_date_column, movie_title_column], \
                           ascending = [False, True], inplace = True)
    data_frame.rename(columns={release_date_column: 'release_year', \
                               movie_title_column: 'title'}, inplace = True)
    return data_frame
# This function converts budget and revenues from string to integer
def clean_dollar_values(data_frame, series_name): 
    data_frame[series_name+'_int'] = [item.replace('$', '') \
                                      for item in data_frame[series_name]] 
    data_frame[series_name+'_int'] = [item.replace(',', '') \
                                      for item in data_frame[series_name+'_int']]
    data_frame[series_name+'_int'] = [" ".join(item.split()) 
                                      for item in data_frame[series_name+'_int']]
    data_frame[series_name+'_int'] = data_frame[series_name+'_int'].astype('int64')
    return data_frame
# This function calculates the whiskers for a series with skewed distribution
def calculate_whiskers(df_series):
    distance = len(df_series) - 1
    index_p75 = int(0.75*distance)
    index_p25 = int(0.25*distance)
    df_series = df_series.sort_values(ascending = True)
    p75 = df_series.iloc[index_p75]
    p25 = df_series.iloc[index_p25] 
    iqr = p75-p25
    return [p25 - 1.5*iqr, p75 + 1.5*iqr] 