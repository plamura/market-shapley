
#!/usr/bin/env python3
import math
from math import *
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import scipy
from scipy.optimize import linear_sum_assignment
import itertools
from cooperative_game import * 
import pickle
import string

def powerset(s):
     x = len(s)
     masks = [1 << i for i in range(x)]
     for i in range(1 << x):
         yield [ss for mask, ss in zip(masks, s) if i & mask]

def goldenapp():
     entries={}
     party_names={}
     polls={}

     entries = pickle.load( open( 'save.p', "rb" ) )
          
     s=0
     party_num=0
     g=0
     g = int(len(entries)/5)+1
     print(g)
     for k in range(0, g):
         try:
             polls[k]=float(entries[k+1,3])
             s=s+1
         except ValueError:
             party_num=s
             break
     print(party_num)
     
     # Initialize parties and coalitions (labelled by letters)

     labels=['']*party_num
     colors=['']*party_num
     excluded=['']*party_num
     values=['']*party_num
     
     parties = list(string.ascii_uppercase)[0:party_num]
     print(parties)
          

     for k in range(0, party_num):
         party_names[k]=str(entries[k+1,0])
         labels[k]=str(entries[k+1,1])
         colors[k]=str(entries[k+1,2])
         excluded[k]=list(str(entries[k+1,4]))
         values[k]=entries[k+1,3]

     print(party_names)
     print(values)
     
     # print({k:entries[k] for k in l if k in entries})
          
          
     label = dict(zip(parties,labels))  
     color = dict(zip(parties,colors))
     value = dict(zip(parties,values))
     coalitions = powerset(parties)


     r=0
     b=0    
     for k in parties:
          if color[k]==str('blue'):
               b=b+1
          if color[k]==str('red'):
               r=r+1

     numval = np.zeros((r,b))    
     for h in range(0,r):
          for j in range(0,b):
               numval[h,j]=max(0,float(entries[h+1,3])-float(entries[r+j+1,3]))

#     numval={}
#     numval= np.array([[5, 8, 2, 0, 0,  0,  0,  0], [7, 9, 6, 0,  0,  0,  0,  0], [2, 3, 0,  0,  0,  0,  0,  0], [0, 0,  0,  0,  0,  0,  0,  0], [0, 0,  0,  0,  0,  0,  0,  0], [ 0,  0,  0,  0,  0,  0,  0,  0,], [ 0,  0,  0,  0,  0,  0,  0,  0], [ 0,  0,  0,  0,  0,  0,  0,  0], [ 0,  0,  0,  0, 0,  0,  0,  0], [ 0,  0,  0,  0,  0,  0,  0,  0]])
     print(numval)
     
     row_ind, col_ind = linear_sum_assignment(numval, maximize=True)
     print(row_ind, col_ind)
     print(numval[row_ind, col_ind].sum())
     

     
     # print(tuple(coalitions))
     worth = {}      
     
     for i in tuple(coalitions):
         numval2 = np.zeros((r,b))
         for j in range(0,r):
            for k in range(0,b):
                numval2[j,k]=0 
                h=set(i).intersection(set(parties[j]))
                l=set(i).intersection(set(parties[r+k]))
                if set(parties[j] ) == h:
                    if set(parties[r+k]) == l:
                         # print(numval2)
                         numval2[j,k]=numval[j,k] 
                         # print(i, parties[j], parties[r+k], numval2[j,k])  
         row_ind, col_ind = linear_sum_assignment(numval2, maximize=True)
         # print(numval2)
         worth[tuple(i)] = numval2[row_ind, col_ind].sum()

     # Introduce campaign commitments

     fr={}
     friends={}
     for k in range(0,party_num):
         fr[k]=list(set(parties) - set(excluded[k]))

     for k in range(0,party_num):
         friends[parties[k]]=fr[k]

     # Computing seats, Shapley values and all winning coalitions

     P=0
     for i in range(len(polls)):
         P += polls[i]


     # Initialize proportions of seats (precise and rounded)    

     s ={}
     sround = {}    
     pl = {} 
     i = 0  
     for p in parties:
         pl[p]=polls[i]
         s[p] = polls[i]
         sround[p]= round(float(s[p]),1)
         i+=1

     
     letter_game = CooperativeGame(worth)
     sh = letter_game.shapley_value()
     print( "{:<10} {:<10} {:<10} {:<10} {:<10}".format('Label', 'Party', 'Votes (%)', 'Seats (%)', 'Strength') )
     for k in parties:
         lb = label[k]
         num = sround[k]
         v = max(sh[k],0)
         print( "{:<10} {:<10} {:<10} {:<10} {:<10}".format(k, lb, round(float(pl[k]),2), num, v) )    

     letter_function = {}
     for k in worth.keys():            # Find all winning coalitions
         if worth[k] != 0:
             letter_function[k]=worth[k]

     # print(letter_function)

     # Find all minimal winning coalitions

     #non_minimal_winning={}
     #for k in letter_function.keys():
     #    for j in letter_function.keys():
     #        if (j!= k) and (set(k).intersection(set(j)) == set(k)):             
     #            non_minimal_winning[j]=letter_function[j]

     #minimal_winning={}
     #for k in letter_function.keys():
     #    if not(k in non_minimal_winning.keys()):
     #        minimal_winning[k]=letter_function[k]
     
     minimal_winning={}
     minimal_winning=letter_function
     print(minimal_winning)

     # Find all stable coalitions

     plt.figure(0)                
     chi = {}
     power = {}
     for k in minimal_winning.keys():
         S = 0
         for j in k:
             S += max(sh[j],0)
         chi[k] = minimal_winning[k]/S

         u=''
         b = 0
         for j in k:
             po=''
             pc=''
             power[j] = max(0,sh[j])*chi[k]
             if power[j]==0:
                 po='('
                 pc=')'
             u = u + po + label[j].split('/')[0] + pc + ' '  
         for i in k:
             plt.bar(u, power[i], bottom = b, color = color[i])
             b = b +power[i]
         plt.bar(u, 0.03, bottom=(chi[k]-1)*(0.9), color='white', width=.2) 
     plt.xticks(rotation=-20, fontsize=8, horizontalalignment='left')

     print('Minimal winning coalitions and Power distribution') 
     print('( Power = Strength x Stability ):')            

     S = 0
     for j in parties:
         S += max(sh[j],0)

     plt.figure(1)                
     for i in parties:
         plt.bar(label[i], s[i], color = color[i], width=0.3, align='center')
         plt.bar(label[i], 0.003, bottom = max(0,sh[i])/S, color = 'red', width=0.6, align='center')         
     plt.xticks(rotation=-20, fontsize=8, horizontalalignment='left')
     
     plt.figure(2)
     G = nx.Graph()
     G.add_nodes_from(parties)
     for i in tuple(parties):
         for j in tuple(parties):
             if set(i).intersection(friends[j])!=set():
                 G.add_edge(i,j)
     pos = nx.spring_layout(G)  # positions for all nodes
     # nodes 
     deg=dict(nx.degree(G))

     nx.draw_networkx_nodes(G, pos, nodelist=parties, node_color=colors, edgecolors='black', alpha=0.5, node_size=[v * 10000 for v in s.values()])
     nx.draw_networkx_nodes(G, pos, nodelist=parties, node_color=colors, edgecolors='red', alpha=0.5, node_size=[v * 10000 for v in sh.values()])

     # edges
     nx.draw_networkx_edges(G, pos, alpha=0.2, width=1.5)
     # labels
     nx.draw_networkx_labels(G, pos, labels=label, font_size=10, font_family='sans-serif')

     plt.axis('off')
     plt.show()
     print(chi)
