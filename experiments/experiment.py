#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install pandas')


# In[4]:


import pandas as pd


# In[69]:


data = pd.read_table(r"C:\Users\033782565\Desktop\dataset\title.basics.tsv")


# In[70]:


data = data[(data['titleType']=="tvSeries") | (data['titleType']=="movie")]
# data = data[(data['titleType']!="tvEpisode")]
# data = data[(data['titleType']!="video")]
# data = data[(data['titleType']!="tvMovie")]



data


# In[59]:


data.describe()


# In[71]:


unique_categories = data['titleType'].unique()
unique_categories


# In[54]:


# fetch = data[data['originalTitle'].str.contains("Kissing", case=False, na=False)]
# fetch

# fetch = data[data['tconst']=="tt3799232"]
# fetch


# In[66]:


fetch = data[data['startYear']=="2018"]
fetch = fetch[fetch['originalTitle'].str.contains("kissing Boo", case=False, na=False)]
fetch


# In[ ]:




