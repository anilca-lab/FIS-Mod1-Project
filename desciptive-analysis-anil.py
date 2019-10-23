#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code examines the relationship between return on investment (RoI) and movie characteristics.
RoI is defined as log difference to reduce dispersion.
For the same reason, budget and revenues are also converted to log terms.
Outliers in budget and revenue series are identified using the standard Q1-1.5IQR,
Q3+1.5IQR formula.
The outliers are left to further analysis. 
"""
data_directory = '/Users/flatironschol/fis_projects/Data/' 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
df_clean = pd.read_csv(data_directory+'export_df_clean.csv')
df_budget = df_clean.loc[(df_clean.production_budget.isna() == False) & \
                         (df_clean.domestic_gross.isna() == False) & \
                         (df_clean.worldwide_gross.isna() == False)]
# Convert budget and revenues to int and log terms
def clean_dollar_values(data_frame, series_name): 
    data_frame[series_name+'_int'] = [item.replace('$', '') for item in data_frame[series_name]] 
    data_frame[series_name+'_int'] = [item.replace(',', '') for item in data_frame[series_name+'_int']]
    data_frame[series_name+'_int'] = [" ".join(item.split()) for item in data_frame[series_name+'_int']]
    data_frame[series_name+'_int'] = data_frame[series_name+'_int'].astype('int64')
    return data_frame
for series_name in ['production_budget', 'domestic_gross', 'worldwide_gross']:
    df_budget = clean_dollar_values(df_budget, series_name)
df_budget['budget'] = np.log(df_budget.production_budget_int)
df_budget['domestic_revenues'] = np.log(df_budget.domestic_gross_int)
df_budget['world_revenues'] = np.log(df_budget.worldwide_gross_int)
# Clean out outliers in budget and worldwide revenue series
plt.boxplot([df_budget.budget, df_budget.world_revenues])
plt.set_xticklabels = [(1, 'Budget'), (2, 'Worldwide revenues')]
plt.show()
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
df_budget['roi'] = df_budget.world_revenues - df_budget.budget 
df_budget['roi_bottom'] = df_budget.loc[(df_budget.roi < calculate_whiskers(df_budget.roi)[0])].roi
df_budget['roi_top'] = df_budget.loc[(df_budget.roi > calculate_whiskers(df_budget.roi)[1])].roi
df_budget_roi_top = df_budget.loc[df_budget.roi_top.isna() == False]
df_budget_roi_bottom = df_budget.loc[df_budget.roi_bottom.isna() == False]
plt.scatter(df_budget.budget, df_budget.roi, color = 'grey', s = 3) 
plt.scatter(df_budget.budget, df_budget.roi_bottom, color = 'r') 
plt.scatter(df_budget.budget, df_budget.roi_top, color = 'g')
plt.xticks(np.arange(13, 20+(20-13)/4, (20-13)/4), (np.exp(np.arange(13, 20+(20-13)/4, (20-13)/4))*(10**(-6))).round(1), rotation = 90)
plt.xlabel('Budget (in millions)')
plt.yticks(np.arange(-6, 5+(5-(-6))/8, (5-(-6))/8), np.exp(np.arange(-6, 5+(5-(-6))/8, (5-(-6))/8)).round(2))
plt.ylabel('Return on investment\n(worldwide revenues/production budget)')
plt.title('Return on investment varies significantly')
plt.show()
# Show how movie characteristics vary across different ROI groups
# Release month
boxplot_data = []
for month in df_budget.release_month.unique():
    boxplot_data.append(list(df_budget.loc[df_budget.release_month == month].roi))
plt.boxplot(boxplot_data)
plt.ylabel('Return on investment\n(Worldwide revenues/Production cost)')
plt.yticks(np.arange(-6, 5+(5-(-6))/8, (5-(-6))/8), np.exp(np.arange(-6, 5+(5-(-6))/8, (5-(-6))/8)).round(2))
plt.xlabel('Release month')
plt.xticks(np.arange(13), ('', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'), rotation=90)
plt.title('October appears to be the riskiest month to release a movie')
plt.show() 
df_budget_roi_top['release_month'] = [item.split('-')[1] for item in df_budget_roi_top.release_year_month]
df_budget_roi_top_monthly_counts = df_budget_roi_top.groupby(['release_month']).title.count()
plt.bar(df_budget_roi_top_monthly_counts.index, df_budget_roi_top_monthly_counts)
plt.ylabel('Number of movies')
#plt.xticks(np.arange(10), ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October'), rotation=90)
plt.xlabel('Release month')
plt.title('Best performers in terms of return on investment')
plt.show() 
df_budget_roi_bottom['release_month'] = [item.split('-')[1] for item in df_budget_roi_bottom.release_year_month]
df_budget_roi_bottom_monthly_counts = df_budget_roi_bottom.groupby(['release_month']).title.count()
plt.bar(df_budget_roi_bottom_monthly_counts.index, df_budget_roi_bottom_monthly_counts)
plt.ylabel('Number of movies')
#plt.xticks(np.arange(10), ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October'), rotation=90)
plt.xlabel('Release month')
plt.title('Worst performers in terms of return on investment')
plt.show()
# Show ROI dispersion for <> $90 million movies
boxplot_data = [df_budget.loc[df_budget.production_budget_int <= 90*(10**6)].roi, df_budget.loc[df_budget.production_budget_int > 90*(10**6)].roi]
plt.boxplot(boxplot_data)
plt.ylabel('Return on investment\n(Worldwide revenues/Production cost)')
plt.yticks(np.arange(-6, 5+(5-(-6))/8, (5-(-6))/8), np.exp(np.arange(-6, 5+(5-(-6))/8, (5-(-6))/8)).round(2))
plt.xticks(np.arange(3), ('','Production budget\n<= $90 million', 'Production budget\n> $90 million'))
plt.title('Different business models')
plt.show()
lp_large = df_budget.loc[(df_budget.production_budget_int > 90*(10**6)) & (df_budget.roi < 0)] 
lp_small = df_budget.loc[(df_budget.production_budget_int <= 90*(10**6)) & (df_budget.roi < 0)]
# Show if there is a relationship between ROI and ratings
plt.scatter(np.log(df_budget.numvotes), df_budget.roi)
plt.scatter(np.log(df_budget.averagerating), df_budget.roi)
plt.scatter(np.log(df_budget.averagerating), np.log(df_budget.numvotes))
