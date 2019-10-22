#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The code looks at the relationship between budget and movie ratings
"""
data_directory = '/Users/flatironschol/fis_projects/Data/' 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
df_clean = pd.read_csv(data_directory+'export_df_clean.csv')
df_budget = df_clean.drop(df_clean.loc[(df_clean.production_budget.isna()) | \
                                       (df_clean.vote_count.isna())].index)
df_budget = df_budget.loc[(df_budget.release_year >= 2010) & (df_budget.release_year <= 2018)]
df_budget = df_budget.loc[df_budget.vote_count >= 25] #284

def clean_dollar_values(df_series): # this function is not working
    df_series_clean = pd.Series([item.replace('$', '') for item in df_series]) 
    df_series_clean = pd.Series([item.replace(',', '') for item in df_series_clean])
    df_series_clean = pd.Series([" ".join(item.split()) for item in df_series_clean]) 
    df_series_clean = df_series_clean.astype('int64')
    return df_series_clean

df_budget['budget'] = clean_dollar_values(df_budget.production_budget)

df_budget['budget'] = [item.replace('$', '') for item in df_budget.production_budget] 
df_budget['budget'] = [item.replace(',', '') for item in df_budget.budget]
df_budget['budget'] = [" ".join(item.split()) for item in df_budget.budget] 
df_budget['budget'] = df_budget['budget'].astype('int64')
df_budget['budget'] = np.log(df_budget['budget'])

df_budget['domestic_revenues'] = [item.replace('$', '') for item in df_budget.domestic_gross] 
df_budget['domestic_revenues'] = [item.replace(',', '') for item in df_budget.domestic_revenues]
df_budget['domestic_revenues'] = [" ".join(item.split()) for item in df_budget.domestic_revenues] 
df_budget['domestic_revenues'] = df_budget['domestic_revenues'].astype('int64')
df_budget['domestic_revenues'] = np.log(df_budget['domestic_revenues'])

df_budget['world_revenues'] = [item.replace('$', '') for item in df_budget.worldwide_gross] 
df_budget['world_revenues'] = [item.replace(',', '') for item in df_budget.world_revenues]
df_budget['world_revenues'] = [" ".join(item.split()) for item in df_budget.world_revenues] 
df_budget['world_revenues'] = df_budget['world_revenues'].astype('int64')
df_budget['world_revenues'] = np.log(df_budget['world_revenues'])
    
# Clean out outliers for budget and worldwide revenues
all_data = [df_budget.budget, df_budget.world_revenues]
plt.boxplot(all_data)
plt.set_xticklabels = [(1, 'Budget'), (2, 'Worldwide revenues')]

def calculate_whiskers(df_series):
    distance = len(df_series) - 1
    index_p75 = int(0.75*distance)
    index_p25 = int(0.25*distance)
    df_series = df_series.sort_values(ascending = True)
    p75 = df_series.iloc[index_p75]
    p25 = df_series.iloc[index_p25] 
    iqr = p75-p25
    return [p25 - 1.5*iqr, p75 + 1.5*iqr] 

df_budget['budget_outliers'] = df_budget.loc[(df_budget.budget < calculate_whiskers(df_budget.budget)[0]) | \
                                             (df_budget.budget > calculate_whiskers(df_budget.budget)[1])].budget
df_budget = df_budget.loc[df_budget.budget_outliers.isna()]
df_budget['world_revenues_outliers'] = df_budget.loc[(df_budget.world_revenues < calculate_whiskers(df_budget.world_revenues)[0]) | \
                                                     (df_budget.world_revenues > calculate_whiskers(df_budget.world_revenues)[1])].world_revenues
df_budget = df_budget.loc[df_budget.world_revenues_outliers.isna()]

# Show outliers for ROI
df_budget['roi'] = df_budget.world_revenues-df_budget.budget 
plt.scatter(df_budget.budget, df_budget.world_revenues)
plt.hist(df_budget.roi, bins = 100)
plt.boxplot(df_budget.roi)
df_budget['roi_bottom'] = df_budget.loc[(df_budget.roi < calculate_whiskers(df_budget.roi)[0])].roi
df_budget['roi_top'] = df_budget.loc[(df_budget.roi > calculate_whiskers(df_budget.roi)[1])].roi
df_budget_roi_top = df_budget.loc[df_budget.roi_top.isna() == False]
df_budget_roi_bottom = df_budget.loc[df_budget.roi_bottom.isna() == False]
plt.scatter(df_budget.budget, df_budget.roi, color = 'grey', s = 3) 
plt.scatter(df_budget.budget, df_budget.roi_bottom, color = 'r') 
plt.scatter(df_budget.budget, df_budget.roi_top, color = 'g')
plt.xlabel('Budget')
plt.ylabel('Return on investment')
plt.show()

   

