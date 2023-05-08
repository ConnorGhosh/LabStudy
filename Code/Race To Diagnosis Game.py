#!/usr/bin/env python
# coding: utf-8

# # Race To Diagnosis Game

# In[ ]:


import pandas as pd
import numpy as np
import names
import time


# In[ ]:


df = pd.read_csv('Lab Study Games-Copy1.csv')


# In[ ]:


gameID = 0 #change this ID for each new game
df = df.iloc[gameID]
name = names.get_first_name()


# # Game Scenario: Round 1

# In[ ]:


print('Game Scenario','\n Name: ',name, '\n Symptoms/Findings for Round 1: ',df['Round 1'])


# In[ ]:


time.sleep(2)
print('You have 2 minutes before you have to make a guess. Your time starts now.')
time.sleep(60)
print('You have 1 minute left')
time.sleep(60)
guess1 = input('Enter your guess: ')


# # Round 2

# In[ ]:


print('Round 2: No more symptoms this round')
time.sleep(2)
print('You have 2 minutes before you have to make a guess. Your time starts now.')
time.sleep(60)
print('You have 1 minute left')
time.sleep(60)
guess1 = input('Enter your guess: ')


# # Round 3

# In[ ]:


print('Symptoms/Findings for Round 3: ',df['Round 2'])
time.sleep(2)
print('You have 2 minutes before you have to make a guess. Your time starts now.')
time.sleep(60)
print('You have 1 minute left')
time.sleep(60)
guess2 = input('Enter your guess: ')


# # Round 4

# In[ ]:


print('Symptoms/Findings for Round 4: ',df['Round 3'])
time.sleep(2)
print('You have 2 minutes before you have to make a guess. Your time starts now.')
time.sleep(60)
print('You have 1 minute left')
time.sleep(60)
guess3 = input('Enter your guess: ')


# # Reveal Answer

# In[ ]:


print('The correct answer is: ')
time.sleep(2)
print(df['Disorder'])

