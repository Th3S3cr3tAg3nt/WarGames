import pygame, sys, os
import pygame.gfxdraw
import random
import math
from pygame.locals import *
pygame.init()
import requests
import json
import os.path
from pprint import pprint

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()
#print args.file

# ONLY OPTIONS HERE ############################################################
CURVE=True
DOTTEDLINES=True
LINE=False
PRINT=False
FLASHES=False
EXPLOSIONS=True
EXPLOSION_SIZE=20

VIDEO=False

DEFAULT_X=940
DEFAULT_Y=230

CURVE_HEIGHT=50

# Screen Size
w, h = 1920, 1080

# IPINFO API
TOKEN='123456789abcde' # PUT YOUR OWN IPINFO.IO API TOKEN HERE

# LOGFILE CONFIG
LOG_DELIMITER = '\" \"'
LOG_DATE = 1
LOG_TIME = 2
LOG_IP = 9
LOG_PROTOCOL = 11
LOG_SERVICE = 7

# To Do ########################################################################
# Destination IP geolocation
# Optional Labels?

running=True
speed=20

BLUE=(0,0,255)
FLASH=(128,255,255)
LAUNCH=(192,255,255)
FLASHA=(192,255,255,128)
ROCKET=(255,255,255)
ROCKETTRACE=(192,192,255)
RED=(255,0,0)
REDA=(255,0,0,127)
DARKRED=(128,0,0)
BLACK=(0,0,0)

# Set the size of the display
screen = pygame.display.set_mode((w, h))

# initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
#myfont = pygame.font.SysFont("sans", 18)
myfont = pygame.font.Font("FiraCode-Regular.ttf", 24)

countries={}
protocols={}

Missile = [[]]
Connections = []
Messages = []

worldmap = pygame.image.load(os.path.join("worldmap.jpg"))

Missile[0].append(DEFAULT_X)      # Source X
Missile[0].append(DEFAULT_Y)      # Source Y
Missile[0].append(DEFAULT_X)      # Dest X
Missile[0].append(DEFAULT_Y)      # Dest Y
Missile[0].append(100)      # TimeScale
Missile[0].append(True)     # Dropped
Missile[0].append("tcp")    # Protocol
Missile[0].append("80")     # Service

current_date_time = "DATE TIME"

file = open(args.file, "r")

line = file.readline()
#print line
#words = line.split(" ")
#print words[8]

paused=False

frame=0

while running==True:
    screen.blit(worldmap, (0, 0))
    for event in pygame.event.get():
        # test events, set key states
        if event.type == pygame.KEYDOWN:
            if event.key==K_SPACE:
                paused=True;
        if event.type == pygame.KEYUP:
            if event.key==K_ESCAPE:
                running=False;
            if event.key==K_SPACE:
                paused=False;
    for M in Missile:
        if paused==False:
            M[4]+=speed
    for M in Missile:
        #if (M[4]>(1000-speed)):
        #    pass
        #else:
        if (M[5]==True):
            r=M[4]/10
            if r>10: r=10;
            pygame.draw.circle(screen, RED, (M[0],M[1]), r)
    for M in Missile:
        if DOTTEDLINES==True and M[5]==True:
            line_length = M[4]
            if line_length>1000:
                line_length=1000
            for d in range(20, line_length,20):
                lx=M[0]+(d*(M[2]-M[0])/float(1000))
                if CURVE == True:
                    ly=M[1]+(d*(M[3]-M[1])/float(1000))-CURVE_HEIGHT*math.sin(math.pi*d/1000)
                else:
                    ly=M[1]+(d*(M[3]-M[1])/float(1000))
                pygame.draw.circle(screen, ROCKETTRACE, (int(lx),int(ly)), 2)
    for M in Missile:
        dx=M[0]+(M[4]*(M[2]-M[0])/float(1000))
        if CURVE == True:
            dy=M[1]+(M[4]*(M[3]-M[1])/float(1000))-CURVE_HEIGHT*math.sin(math.pi*M[4]/1000)
        else:
            dy=M[1]+(M[4]*(M[3]-M[1])/float(1000))
        if (M[4]>(1000-speed)):
            if M[5]==True:
                if EXPLOSIONS==True:
                    if M[4]>1000:
                        r=(M[4]-1000)/25
                        #pygame.draw.circle(screen, FLASH, (M[2],M[3]), r)
                        pygame.gfxdraw.aacircle(screen,M[2],M[3],r,FLASH)
                        if r>EXPLOSION_SIZE:
                            M[5]=False
                if FLASHES==True:
                    pygame.draw.line(screen, FLASH, (M[2],M[3]), (M[0],M[1]), 5)
                #M[5]=False
        else:
            #r=M[4]
            #if r>10: r=10;
            if LINE == True:
                pygame.draw.aaline(screen, DARKRED, (M[2],M[3]), (dx,dy), 1)
                pygame.draw.aaline(screen, RED, (M[0],M[1]), (dx,dy), 1)
            #pygame.draw.circle(screen, RED, (M[0],M[1]), r)
            if M[6]=="udp":
                pygame.draw.circle(screen, ROCKET, (int(dx),int(dy)), 5, 1)
                pygame.draw.circle(screen, BLACK, (int(dx),int(dy)), 4)
            else:
                pygame.draw.circle(screen, ROCKET, (int(dx),int(dy)), 5)
    if paused==False:
            if PRINT == True:
                print "============================================================"
            line = file.readline()
            words = line.split("\" \"")
            if len(words[LOG_DATE])>2 and len(words[LOG_TIME])>2:
                current_date_time=words[1] + ' ' + words[2]

            ip = words[LOG_IP].translate(None, '!@#$\"')
            protocol = words[LOG_PROTOCOL]
            service = words[LOG_SERVICE]
            if PRINT == True:
                print ip, protocol, service
            # Maintain list of top protocols
            if service in protocols:
                protocols[service]+=1
            else:
                protocols[service]=1
            if len(ip)>7:
                # Write something about it to screen
                Messages.append(ip + ' on ' + protocol + ':' + service)
                if len(Messages) > 10:
                    Messages.pop(0)

                # Find if we have already cached this information
                ipdata = 'ips/' + ip + '.json'
                if not os.path.isfile(ipdata):
                    if PRINT == True:
                        print 'Retrieving data for ' + ip
                    url = 'https://ipinfo.io/' + ip + '?token=' + TOKEN
                    r = requests.get(url)
                    json_data = json.loads(r.text)
                    with open(ipdata, "w") as write_file:
                        json.dump(json_data, write_file)
                if os.path.isfile(ipdata):
                    if PRINT == True:
                        print 'Reading data from file ' + ipdata
                    # path exists
                    with open(ipdata) as jd:
                        json_data = json.load(jd)
                        if 'loc' not in json_data:
                            if PRINT == True:
                                print "No location data"
                        else:
                            FreeMissile=-1 # This bit of code looks for dead missiles
                            for i in range(len(Missile)):
                                if Missile[i][5]==False:
                                    FreeMissile=i
                                    break
                            loc = json_data["loc"].split(",")
                            mx = int(w * (float(loc[1])+180)/360)
                            my = int(h * ((float(loc[0])*-1)+90)/180)
                            if FreeMissile==-1:
                                # If there are no dead missile to reuse, create a new one
                                Missile.append([])
                            else:
                                while len(Missile[FreeMissile])>0:
                                    # This loop clears out old values
                                    Missile[FreeMissile].pop()
                            Missile[FreeMissile].append(mx)
                            Missile[FreeMissile].append(my)
                            Missile[FreeMissile].append(DEFAULT_X)
                            Missile[FreeMissile].append(DEFAULT_Y)
                            Missile[FreeMissile].append(0)
                            Missile[FreeMissile].append(True)
                            Missile[FreeMissile].append(protocol)
                            Missile[FreeMissile].append(service)
                        if 'country' not in json_data:
                            if PRINT == True:
                                print "No country data"
                        else:
                            if PRINT == True:
                                print json_data["country"]
                            if json_data["country"] in countries:
                                countries[json_data["country"]]+=1
                            else:
                                countries[json_data["country"]]=1
    # display date and Time
    textsurface = myfont.render(current_date_time, True, (192, 192, 255))
    screen.blit(textsurface,(10,10))
    # Display messages #########################################################
    my=850
    for message in Messages:
        messagesurface = myfont.render(message, True, (192, 192, 255))
        screen.blit(messagesurface,(10,my))
        my+=20
    # Display TOP countries ####################################################
    top=0
    my=850
    total_values = sum(countries.values())
    for key, value in sorted(countries.items(), key=lambda x: x[1], reverse=True):
        top+=1
        if top<=10:
            percent = str(int(100 * float(value) / float(total_values)))
            messagesurface = myfont.render(key + ' ' + percent + '%', True, (255, 128, 128))
            screen.blit(messagesurface,(1760,my))
            my+=20
    # Display TOP protocols
    top=0
    my=850
    total_values = sum(protocols.values())
    for key, value in sorted(protocols.items(), key=lambda x: x[1], reverse=True):
        top+=1
        if top<=10:
            percent = str(int(100 * float(value) / float(total_values)))
            messagesurface = myfont.render(key + ' ' + percent + '%', True, (255, 255, 128))
            screen.blit(messagesurface,(1450,my))
            my+=20
    pygame.display.flip()
    f = 'map' + str(frame).zfill(10) + '.png'
    pygame.image.save(screen, f)
    frame +=1

file.close()

pygame.quit()
