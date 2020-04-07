#!/usr/bin/env python3

# append current dir to include path
from os import getcwd
from os.path import dirname,sep as psep,normpath,isabs
from sys import path,argv,exit,stderr
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
from argparse import ArgumentParser

def parse_args():
    a=ArgumentParser()
    a.add_argument("-n","--number-of-list-len",default=15,type=int,help="determines the targeted lenght of the generated list")
    a.add_argument("-p","--offer-plot-popup",default=False,action="store_true",help="offer plot popup")
    a.add_argument("-m","--danger-min-level",default=2,type=float,help="min dangerousness level (this gets prioritized over the list lenght)")
    a.add_argument("-ma","--danger-max-level",default=2,type=float,help="max dangerousness level (use in combination with \"-r\",)(this option gets prioritized over the list lenght)")
    a.add_argument("-r","--reverse",action="store_true",default=False,help="reverse sort order and use the max-level option instead of the min level option")
    return a.parse_args()

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
        print("danger lk:",file=stderr)
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

def get_danger(data,landkreise,skip=0):
    danger=[]
    count=skip
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
                print(file=stderr)
                print("failed to evaluate dataset lk="+lk,file=stderr)
                print("covid_data:",file=stderr)
                pprint(covid_data,file=stderr)
                print(file=stderr)

        dangertuple=(lkid,lk,dangerous)
        if not dangerous is None:
            danger.append(dangertuple)
    return danger

def show_danger(data,skip=0,dangerous_min_level=3,dangerous_max_level=0,reverse=False,len_danger_list=10):
    """
    new show function
    """
    landkreise=load_kreise()
    try:
        no_change_loops=0
        len_b=0
        danger_ret=[]

        # get danger data
        danger_all=[]
        danger_all = get_danger(data,landkreise,skip=skip)
        current_dangerous_min_level=dangerous_min_level
        current_dangerous_max_level=dangerous_max_level
        while not len_b >= len_danger_list and not no_change_loops > 5:

            for d in danger_all:

                # break for loop if reached len
                if len_b >= len_danger_list:
                    break
                len_a=len_b
                if (d[-1] >= current_dangerous_min_level and not reverse ) or (reverse and d[-1] <= current_dangerous_max_level):
                    lk_ids = [i for i,j,k in danger_ret]
                    if not d[0] in lk_ids:
                        danger_ret.append(d)
                        len_b=len(danger_ret)
            
            # in case the for loop added nothing
            if not len_b > len_a:
                no_change_loops+=1
            # go down in min level in case list needs more entries
            if not reverse:
                current_dangerous_min_level = max(current_dangerous_min_level-0.1, dangerous_min_level)
            elif reverse:
                current_dangerous_max_level = min(current_dangerous_max_level+0.1, dangerous_max_level)

    finally:
        print("danger lk:",file=stderr)
        danger_ret.sort(key=itemgetter(2),reverse=not reverse)
        for a,b,c in danger_ret:
            print("{:5} {:25.25} {:.3f}".format(a,b,c))
            if args.offer_plot_popup:
                inp=input("Show plot ? (y/n):")
                if inp=="y":
                    gen_plot_file(data,a)
                    call(['gnuplot','-p','plot.gnuplot'])

if __name__=="__main__":
    args=parse_args()
    data=load_data()
    show_danger(data,len_danger_list=args.number_of_list_len,dangerous_min_level=args.danger_min_level,dangerous_max_level=args.danger_max_level,reverse=args.reverse)

# vim: set foldmethod=indent foldlevel=0 foldnestmax=1 :
