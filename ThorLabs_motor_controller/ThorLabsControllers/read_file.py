#!/bin/env python
import os

def read_file(SN = None):
    filename = '\motor_settings.txt'
    filepath = os.path.dirname(__file__) + filename
    data = []
    lst = []
    with open(filepath,'r') as f:
        data =f.readlines()
    for i in range(len(data)):
        lst.append(data[i].split(','))
    for j in range(len(lst)):   
        #lst[j] = [i.replace(' ','') for i in lst[j]]    
        lst[j] = [i.replace('\n','') for i in lst[j]] 
    flag =  None
    for i in lst:
        for j in i:
            if j == str(SN):
                lst = i
    return lst
    
if __name__ == "__main__":
    lst = read_file(83000000)
