#!/usr/bin/env python3

# append current dir to include path
from os import getcwd
from os.path import dirname,sep as psep,normpath,isabs
from sys import path,argv,exit
if not isabs(argv[0]):
    p=getcwd()+psep+argv[0]
else:
    p=argv[0]
module_path = normpath(dirname(p))
include_parent=normpath(psep.join(normpath(module_path).split(psep)[:-1]))
path.append(include_parent)

from covid19py.utils import *
from covid19py.curlquery import *
from subprocess import check_call,call
from operator import itemgetter
from pprint import pprint

def show_all(data,skip=0):
    """
    the old show function that is interactive
    """
    landkreise=load_kreise()
    danger=[]
    count=skip
    try:
        for lkid,lk in landkreise[skip:]:
            count+=1
            gen_plot_file(data,lkid)
            call(['gnuplot','-p','plot.gnuplot'])
            print(count,lkid,lk)
            inp=input("danger? Y/enter to continue")
            if inp=="Y":
                danger.append((lkid,lk))
    finally:
        print("danger lk:")
        for a,b in danger:
            print(a,b)

def how_dangerous(dataset):
    """
    Brain function that judges the data for \"danger\",
    whereby danger means a detection of a local outbreak.
    """
    if dataset is None:
        return None
    if not len(dataset) > 1:
        return None
    avg=sum(b for a,b in dataset)/len(dataset)
    if (dataset[-1][-1] * 0.9) > dataset[-2][-1]:
        trend="up"
    elif (dataset[-1][-1] * 1.1) < dataset [-2][-1]:
        trend="down"
    else:
        trend="level"

    if (dataset[-1][-1] * 0.9) > avg:
        avg_trend="up"
    elif (dataset[-1][-1] * 1.1) < avg:
        avg_trend="down"
    else:
        avg_trend="level"

    danger=0
    
    if trend == "up"   : danger+=1
    if trend == "down" : danger-=1
    if avg_trend == "up"   : danger+=1
    if avg_trend == "down" : danger-=1

    danger+= max(dataset[-1][-1]-0.1,0)*10
    danger+= max(avg-0.1,0)*10

    return danger

def show_danger(data,skip=0):
    """
    new show function
    """
    landkreise=load_kreise()
    danger=[]
    count=skip
    try:
        for lkid,lk in landkreise[skip:]:
            count+=1
            covid_data=gen_covid19_data(data,lkid)
            pd=gen_plot_data_1(covid_data)
            dangerous=how_dangerous(pd)
            if dangerous is None:
                af=0
                for i in covid_data:
                    af+=i['AnzahlFall']
                if af > 70:
                    print()
                    print("failed to evaluate dataset lk="+lk)
                    print("covid_data:")
                    pprint(covid_data)
                    print()

            if not dangerous is None and  dangerous >= 3:
                danger.append((lkid,lk,dangerous))
    finally:
        print("danger lk:")
        danger.sort(key=itemgetter(2),reverse=True)
        for a,b,c in danger:
            print("{:5} {:25.25} {:.3f}".format(a,b,c))

if __name__=="__main__":
    data=load_data()
    show_danger(data)

# vim: set foldmethod=indent foldlevel=0 :
