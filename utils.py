from datetime import date
from math import e,log,ceil
from operator import itemgetter
from collections import OrderedDict

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

def load_landkreise():
    with open(module_path+psep+"landkreise") as f:
        return eval(f.read())

def load_stadtkreise():
    with open(module_path+psep+"stadtkreise") as f:
        return eval(f.read())

def load_kreise():
    return load_landkreise() + load_stadtkreise()

class Day20(date):
    """
    A date in the year 2020.
    Create one with: \"Day_20(month,year)\"
    """
    def __new__(self,month,day):
        return date(2020,month,day)

def k(covid_data):
    """
    calculates the konstant \"k\" in f=num_infected^(t*k)
    (t is in days)
    """
    # TODO: check the time range part of this function
    kk=[]
    l=min(10,len(covid_data))
    l0=ceil(l/2)
    for i in range(len(covid_data)-l):
        days  = ( covid_data[i+l]['Meldedatum'] - covid_data[i]['Meldedatum'] ).days
        ratio = covid_data[i+l]['AnzahlFall'] / covid_data[i]['AnzahlFall']
        try:
            kk.append((covid_data[i]['Meldedatum'].day+l0,(1/days)*log(ratio)))
        except ValueError as e:
            if ratio == 0:
                pass
            else:
                print(e,file=stderr)
    return kk

def get_krit_gt0(altersgruppe,krit_gt0):
    """
    returns the data and the count of
    datasets where the "krit"- parameter is greater than zero
    counted is the parameters count not the number of datasets 
    """
    count=0
    ret=[]
    for d in data:
        if d[krit_gt0] >0 and d['Altersgruppe'] in altersgruppe:
            count += d[krit_gt0]
            ret.append(d)
    return ret,count

def gen_covid19_data(data,landkreis_id):
    lk_data=[]
    for d in data:
        if landkreis_id==d['IdLandkreis']:
            lk_data.append(d)
    lk_data.sort(key=itemgetter("Meldedatum"))
    data=OrderedDict()
    for d in lk_data:
        key=d['Meldedatum'].isoformat()
        if not key in data.keys():
            data.update({key:{'AnzahlFall':1,'Meldedatum':d['Meldedatum']}})
        else:
            data[key]['AnzahlFall']+=d['AnzahlFall']
    ret=[]
    for d in data.values():
        ret.append(d)
    return ret

def gen_plot_file(data,landkreis_id):
    with open('plot.data','wt') as f:
        f.write("\n".join([ str(i)+" "+str(j) for i,j in k(gen_covid19_data(data,landkreis_id=landkreis_id))]))

def gen_plot_data(data,landkreis_id):
    return [ (i,j) for i,j in k(gen_covid19_data(data,landkreis_id=landkreis_id))]

def gen_plot_data_1(covid_data):
    return [ (i,j) for i,j in k(covid_data)]



    


# vim: set foldmethod=indent foldlevel=0 foldnestmax=1 :
