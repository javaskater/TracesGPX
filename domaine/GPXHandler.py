#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
'''
Created on Oct 24, 2013

@author: jpmena
'''

import os
from xml.etree.ElementTree import iterparse
from datetime import datetime
import math
import matplotlib.pyplot as plt
import matplotlib.dates as pldt
from macpath import dirname

#tiré de la page 186 de Python CookBook Third Edition
def parse_and_remove(filename):
    saxpath=['{http://www.topografix.com/GPX/1/1}trk', '{http://www.topografix.com/GPX/1/1}trkseg', '{http://www.topografix.com/GPX/1/1}trkpt']
    doc = iterparse(filename, ('start', 'end'))
    # Skip the root element
    next(doc)
    tag_stack = []
    elem_stack = []
    for event, elem in doc:
        if event == 'start':
            tag_stack.append(elem.tag)
            elem_stack.append(elem)
        elif event == 'end':
            if tag_stack == saxpath:
                yield elem #permet d'être utilisé dans une boucle cf. p 593 de Learning Python Fifth Edition
                elem_stack[-2].remove(elem)
            try:
                tag_stack.pop()
                elem_stack.pop()
            except IndexError:
                pass

#http://effbot.org/zone/element.htm
def recupere_donnees(element):
    retour = {}
    try:
        retour['latitude'] = float(element.get('lat'))
        retour['longitude'] = float(element.get('lon'))
    except ValueError as ve:
        print ("impossible de calculer latitude ou longitude car non décimal: message {0}\n".format(ve))
    for ele in element.getchildren():
        if ele.tag == '{http://www.topografix.com/GPX/1/1}time':
            try:
                retour['date']=datetime.strptime(ele.text,'%Y-%m-%dT%H:%M:%SZ')
            except ValueError as ve:
                try:
                    retour['date']=datetime.strptime(ele.text,'%Y-%m-%dT%H:%M:%S.1Z')
                except ValueError as ve:
                    print("impossible de recupere la date du point: message {0}\n".format(ve))
    return retour

def calcule_distance_parcourue(donnees_avant,donnees_actuelles):
    #abandon de la formule autralienne pour une formule trouvée sur developpez, donc une formule adaptée à la France
    #http://www.developpez.net/forums/d948034/webmasters-developpement-web/javascript/bibliotheques-frameworks/mappy/calculer-distance-entre-coordonnees/
    distance=None
    vitesse = -1
    if 'longitude' in donnees_avant.keys() and donnees_avant['longitude'] is not None:
        lon1=math.radians(donnees_avant['longitude'])
        if 'longitude' in donnees_actuelles.keys() and donnees_actuelles['longitude'] is not None:
            lon2=math.radians(donnees_actuelles['longitude'])
            t3 = math.cos(lon1 - lon2);
            if 'latitude' in donnees_avant.keys() and donnees_avant['latitude'] is not None:
                lat1=math.radians(donnees_avant['latitude'])
                if 'latitude' in donnees_actuelles.keys() and donnees_actuelles['latitude'] is not None:
                    lat2=math.radians(donnees_actuelles['latitude'])
                    t1 = math.sin(lat1) * math.sin(lat2);
                    t2 = math.cos(lat1) * math.cos(lat2);
                    t4 = t2 * t3;
                    t5 = t1 + t4;
                    if -t5 * t5 + 1 != 0:
                        rad_dist = math.atan(-t5 / math.sqrt(-t5 * t5 + 1)) + 2 * math.atan(1);
                        #we get a distance in meters
                        distance = (rad_dist * 3437.74677 * 1.1508) * 1.6093470878864446 * 1000
                        if 'date' in donnees_avant.keys() and donnees_avant['date'] is not None:
                            if 'date' in donnees_actuelles.keys() and donnees_actuelles['date'] is not None:
                                delta = donnees_actuelles['date'] - donnees_avant['date']
                                vitesse = None
                                try:
                                    vitesse = distance / delta.total_seconds() #speed in meter/second
                                except:
                                    print ("vitesse non calculable: {0} pas suffisante".format(delta))
                            else:
                                print ("timestamp du point 2 absente\n")
                        else:
                            print ("timestamp du point 1 absente\n")
                    else:
                        print ("on ne peut calculer la distance car diviseur =0\n")
                else:
                    print ("latitude du point 2 absente\n")
            else:
                print ("latitude du point 1 absente\n")
        else:
            print ("longitude du point 2 absente\n")
    else:
        print ("longitude du point 1 absente\n")
    return (distance , vitesse)

def traduction_gpx_vers_csv(path_gpx):
    points=[]
    for domElem in parse_and_remove(path_gpx):
        points.append(recupere_donnees(domElem))
    print ("il y a {0} points\n".format(len(points)))
    #nous allons calculer la distance cumulée et l'enregistrer(la formule nous a retourné la distance directement en kms)
    iout_path='%s.inst_splot' %(path_gpx)
    iplot = open(iout_path, 'w')
    lout_path='%s.lissee_plot' %(path_gpx)
    lplot = open(lout_path, 'w')
    avancees = []
    prise_vitesse_avant = (None,0)  #le datetime de prise de la vitesse avant et la distance cumulée correspondante
    nombre_points_lissage = 10 #on ne meseure la vitesse que tous les 50m
    zone_lissage_points = []
    pAvant = None
    for p in points:
        if pAvant is None:
            pAvant = p
        else:
            avancee = {}
            pEnCours = calcule_distance_parcourue(pAvant,p)
            if pEnCours[0] is not None and pEnCours[1] > 0:
                avancee['t'] = p['date']
                avancee['d'] = pEnCours[0]
                avancee['v'] = pEnCours[1]
                if avancee['v'] is None:
                    if pAvant is not None:
                        avancee['v'] = pAvant[1]
                    else:
                        avancee['v'] = 0
            #on va tester le SMA: http://en.wikipedia.org/wiki/Moving_average
            nbPointsEnCours = len(zone_lissage_points)
            N = nbPointsEnCours + 1 
            if len(avancee) > 0 and nbPointsEnCours > nombre_points_lissage:
                pointAncien = zone_lissage_points[0]
                avancee['vl'] = (- pointAncien['vl'] + pEnCours[1]) / N + zone_lissage_points[-1]['vl']
                avancee['dc'] = zone_lissage_points[-1]['dc'] + avancee['d']
                zone_lissage_points.append(avancee)
                zone_lissage_points = zone_lissage_points[1:]
            elif len(avancee) > 0 and nbPointsEnCours > 0:
                vitesse_moyenne = 0
                for ppt in zone_lissage_points:
                    vitesse_moyenne += ppt['vl']
                vitesse_moyenne += avancee['v']
                avancee['vl'] = vitesse_moyenne / N
                avancee['dc'] = zone_lissage_points[-1]['dc'] + avancee['d']
                zone_lissage_points.append(avancee)
            elif len(avancee) > 0:
                avancee['vl'] = pEnCours[1]
                avancee['dc'] = avancee['d']
                zone_lissage_points.append(avancee)
            if len(avancee) > 0:
                avancees.append(avancee)
                pAvant = p
                iplot.write("{0} {1} {2} vitesse_instant\n".format(avancee['t'].strftime("%H:%M:%S"),avancee['dc'],avancee['v']))
                print ("{0} {1} {2} vitesse_instant\n".format(avancee['t'].strftime("%H:%M:%S"),avancee['dc'],avancee['v']))
                lplot.write("{0} {1} {2} vitesse_lissee\n".format(avancee['t'].strftime("%H:%M:%S"),avancee['dc'],avancee['vl']))
                print("{0} {1} {2} vitesse_lissee\n".format(avancee['t'].strftime("%H:%M:%S"),avancee['dc'],avancee['vl']))
            else:
               print("distance parouru None, point négligeable ...") 
    print ("il y a {0} distances calculées\n".format(len(avancees)))
    iplot.close()
    lplot.close()
    return {'origin':path_gpx,'iplot':iout_path,'lplot':lout_path,'donnees':avancees}

def plot_datas_csv(dict_fichiers_csv):
    print("{0}: fichier lisse, {1}: fichier instantane\n".format(dict_fichiers_csv['lplot'],dict_fichiers_csv['iplot']))
    donnees_x = []
    donnees_y = []
    for dict_data in  dict_fichiers_csv['donnees']:
        donnees_x.append(dict_data['t'])
        donnees_y.append(dict_data['vl']*3.6)
    #TODO utiliser numPy et matplotlib !!!! http://matplotlib.org/api/figure_api.html
    # http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.subplot
    plt.ylabel(u'Vitesse instantanée')
    plt.xlabel(u"Durée")
    dates = pldt.date2num(donnees_x)
    xformat = pldt.DateFormatter('%H:%M')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    #ax.xaxis.set_major_locator(pldt.MinuteLocator()) #affiche l'abscisse toutes les minutes !!!
    ax.xaxis.set_major_formatter(xformat)
    ax.plot(donnees_x, donnees_y)
    path_plot_figure = os.path.join(os.path.dirname(dict_fichiers_csv['origin']),"plot.png")
    plt.savefig(path_plot_figure)
    return path_plot_figure

if __name__ == '__main__':
    path_gpx = "/home/jpmena/workspace/TracesGPX/Solene/aulnay le 11 mars 2015.gpx"
    dict_fichiers_csv  = traduction_gpx_vers_csv(path_gpx)
    plot_datas_csv(dict_fichiers_csv)
        
    
        #print 'longitude {lon}'.format({'lon':repr(domElem)})
