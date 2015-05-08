#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
'''
Created on 23 mars 2015

@author: jpmena
'''
from os.path import *
from os import system, getcwd
from domaine import GPXHandler

def fit_to_plotdata(path_fit):
    path_gpx = "{0}.gpx".format(join(dirname(path_fit),basename(path_fit)))
    workspace = dirname(dirname(getcwd()))
    #cela a été compilé avec un JDK8, il faut le recompiler avec un JDK compatible poste de travail le JDK8 n'étant que sur la 14.10 par défaut!!!!
    #toDO faire une tâche ANT ou Gradle !!!
    russian_command = "cd ../fit2gpx && ./fit2gpx.sh {0}".format(path_fit)
    system(russian_command)
    #path_plot_data = "{0}.csv".format(os.path.join(dirname(path_fit),basename(path_fit)))
    #GPXHandler.traduction_gpx_vers_csv(path_gpx)
   
    


if __name__ == '__main__':
    path_fit = "/home/jpmena/.virtualenvs/monProjet/workspace/TracesGPX/JPM/2015-03-21-10-20-27.fit"
    fit_to_plotdata(path_fit)
    path_gpx = "{0}.gpx".format(path_fit)
    dict_fichiers_csv  = GPXHandler.traduction_gpx_vers_csv(path_gpx)
    GPXHandler.plot_datas_csv(dict_fichiers_csv)