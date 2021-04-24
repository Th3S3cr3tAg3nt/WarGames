import pygame, sys, os
import pygame.gfxdraw
import random
import math
from pygame.locals import *
pygame.init()
import requests
import json
import os.path
import socket
from pprint import pprint

import re

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()


# ONLY OPTIONS HERE ############################################################
CURVE=True
LAUNCH_SITE=True
MISSILE_TRACK=True
DOTTEDLINES=False
DOTTTEDLINESFADE=False
DOTTTEDLINESFOLLOW=False
LINE=False
PRINT=False
FLASHES=False
EXPLOSIONS=True
EXPLOSION_SIZE=20
LAUNCH_DITHER=0
LAUNCH_LOCATIONS=True
TRACK_LAUNCHSITES=True
ALERT_TIME=50
QUIT_ON_END=True

MESSAGE_LINES_PER_LOOP=10
speed=10

MESSAGE_GRANULARITY = "SECONDS"

shutdown=0

MESSAGE_SEARCH=True
MESSAGE_FLAG="FAILED"

VIDEO=True

# Screen Size
w, h = 1920, 1080

DEFAULT_X = []
DEFAULT_Y = []
#UK
DEFAULT_X.append(950)
DEFAULT_Y.append(230)

CURVE_HEIGHT=50

# IPINFO API
TOKEN='' # PUT YOUR OWN IPINFO.IO API TOKEN HERE

# LOGFILE CONFIG
#DATETIME,??,??,SourceApp,user,ip,message,service,user-agent
#Cowrie Incoming Passwords
LOG_DELIMITER = '[,;\n \/]'
LOG_DATE = 0
LOG_TIME = 0
LOG_IP = 6
LOG_USER = 9
LOG_PROTOCOL = 10
LOG_SERVICE = 10
LOG_MESSAGE = 11

DIRECTION='incoming' # incoming/outgoing
missile_direction = 'incoming'

#Cowrie outgoing TCP-DIRECT
LOG_IP_OUTGOING = 11
LOG_PROTOCOL_OUTGOING = 14

LOOP_SPEED = 0
LOOP_COUNTER = 0

def remove_prefix(text, prefix): # Change this to return something if the prefix isn't there
    # Checks for and removes prefix
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

# To Do ########################################################################
# Destination IP geolocation
# Optional Labels?

running=True

BLUE=(0,0,255)
BLUE_MISSILE=(128,255,255)
GREEN=(0,255,0)
FLASH=(128,255,255)
LAUNCH=(192,255,255)
FLASHA=(192,255,255,128)
#ROCKET=(255,255,255)
ROCKET=(255,0,0)

ORANGE=(255,165,0)
MAGENTA=(255,0,255)

#ROCKETTRACE=(128,128,255)
ROCKETTRACE=(255,128,128)
RED=(255,0,0)
REDA=(255,0,0,127)
DARKRED=(128,0,0)
BLACK=(0,0,0)
WHITE=(255,255,255)

# Set the size of the display
screen = pygame.display.set_mode((w, h))

# initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
myfont = pygame.font.Font("FiraCode-Regular.ttf", 20)
mysubtitle = pygame.font.Font("FiraCode-Regular.ttf", 12)

countries={}
protocols={}
users={}
services={}

Missile = [[]]
LaunchLocation = [[]]
LaunchLocationCount=0
Connections = []
Messages = []

worldmap = pygame.image.load(os.path.join("worldmap.jpg"))

Missile[0].append(DEFAULT_X[0])      # Source X
Missile[0].append(DEFAULT_Y[0])      # Source Y
Missile[0].append(DEFAULT_X[0])      # Dest X
Missile[0].append(DEFAULT_Y[0])      # Dest Y
Missile[0].append(1000)      # TimeScale
Missile[0].append(False)     # Dropped
Missile[0].append("tcp")    # Protocol
Missile[0].append("80")     # Service
Missile[0].append(1)        # Launch Color

current_date_time = "DATE TIME"

file = open(args.file, "r")

paused=False

frame=0

# Get the current time from the first line
current_line = file.readline()

NOW_YEAR = int(current_line[0:4])
NOW_MONTH = int(current_line[5:7])
NOW_DAY = int(current_line[8:10])
NOW_HOURS = int(current_line[11:13])
NOW_MINUTES = int(current_line[14:16])
NOW_SECONDS = int(current_line[17:19])

CHECK_TIME = str(NOW_YEAR) + '-' + str(NOW_MONTH).zfill(2) + '-' + str(NOW_DAY).zfill(2) + 'T' + str(NOW_HOURS).zfill(2) + ':' + str(NOW_MINUTES).zfill(2) + ':' + str(NOW_SECONDS).zfill(2) + "."


file.seek(0)


if PRINT == True:
    print (current_line[0:11])
    print (CHECK_TIME)

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
    for M in Missile:                                                          # Draw launch sites
        #if (M[4]>(1000-speed)):
        #    pass
        #else:
        if (M[5]==True):
            r=M[4]/10
            if r>100: r=10 * (1500 - M[4])/500;
            if r>10: r=10;
            if r<0: r=0; M[5]=False;
            if M[8] == 1:
                pygame.draw.circle(screen, RED, (M[0],M[1]), int(r))
            else:
                pygame.draw.circle(screen, RED, (M[0],M[1]), int(r))
    if TRACK_LAUNCHSITES==True:
        for i in range(LaunchLocationCount):                                  # Track Launch Locations
            if LaunchLocation[i][0]>0 and LaunchLocation[i][1]>0:
                if LaunchLocation[i][3]=='incoming':
                    if LaunchLocation[i][2] > 0:
                        pygame.gfxdraw.aacircle(screen,LaunchLocation[i][0],LaunchLocation[i][1],20,RED)
                    else: 
                        pygame.draw.circle(screen, RED, (LaunchLocation[i][0],LaunchLocation[i][1]),5)
                else:
                    pygame.draw.circle(screen, BLUE, (LaunchLocation[i][0],LaunchLocation[i][1]),5)
    for M in Missile:                                                          # Draw explosions
        dx=M[0]+(M[4]*(M[2]-M[0])/float(1000))
        if CURVE == True:
            dy=M[1]+(M[4]*(M[3]-M[1])/float(1000))-CURVE_HEIGHT*math.sin(math.pi*M[4]/1000)
        else:
            dy=M[1]+(M[4]*(M[3]-M[1])/float(1000))
        if (M[4]>(1000-speed)):
            if M[5]==True:
                if M[4]>1000:
                    r=int((M[4]-1000)/25)
                    if r>EXPLOSION_SIZE: r=EXPLOSION_SIZE;
                    if EXPLOSIONS==True:
                        #pygame.draw.circle(screen, FLASH, (M[2],M[3]), r)
                        pygame.gfxdraw.aacircle(screen,M[2],M[3],r,FLASH)
                    #if r>EXPLOSION_SIZE:
                    #    M[5]=False
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
            if MISSILE_TRACK==True:                                            # Draw missiles
                if M[8]==2:
                    pygame.draw.circle(screen, MAGENTA, (int(dx),int(dy)), 4, 1)
                    pygame.draw.circle(screen, MAGENTA, (int(dx),int(dy)), 3)
                elif M[8]<0:
                    pygame.draw.circle(screen, ROCKET, (int(dx),int(dy)), 4)
                else:
                    pygame.draw.circle(screen, ROCKET, (int(dx),int(dy)), 4)
    for M in Missile:
        if DOTTEDLINES==True and M[5]==True and M[8]>0:                                   # Draw dotted lines
            line_length = M[4]
            if DOTTTEDLINESFOLLOW:
                excess_line_length = (line_length - 1000) * 2
                if excess_line_length < 20: excess_line_length=20
            else:
                excess_line_length = 20
            if line_length>1000:
                line_length=1000
            for d in range(excess_line_length, line_length,20):
                lx=M[0]+(d*(M[2]-M[0])/float(1000))
                if CURVE == True:
                    ly=M[1]+(d*(M[3]-M[1])/float(1000))-CURVE_HEIGHT*math.sin(math.pi*d/1000)
                else:
                    ly=M[1]+(d*(M[3]-M[1])/float(1000))
                if (M[4] - 1000) > 0:
                    if DOTTTEDLINESFADE:
                        rdot = 2 - 2 * float((M[4]-1000)/500)
                    else:
                        rdot = 2
                    pygame.draw.circle(screen, ROCKETTRACE, (int(lx),int(ly)), int(rdot))
                else:
                    pygame.draw.circle(screen, ROCKETTRACE, (int(lx),int(ly)), 1)
    if paused==False:                                                          # Read log file
            if PRINT == True:
                print ("============================================================")

            for MESSAGE_LINE in range(MESSAGE_LINES_PER_LOOP):
                FOUND_CHECK_TIME = True
                while FOUND_CHECK_TIME == True:
                    RESET_LOCATION = file.tell()
                    line = file.readline()
                    #print(line)
                    if line.startswith(CHECK_TIME):
                        #print ("starts with it")
                        if 'attempt ' in line:
                            missile_direction = 'incoming'
                            line=''
                        elif 'direct-tcp connection' in line:
                            missile_direction = 'outgoing'
                            #line = ''
                        else:
                            line = '' 
                        #words = line.split(LOG_DELIMITER)
                        words = re.split(LOG_DELIMITER, line)
                        if PRINT == True:
                            print ("Missile_Direction", missile_direction)
                            print (words)
                        if len(words)>3:
                            if len(words[LOG_DATE])>2 and len(words[LOG_TIME])>2:
                                if words[LOG_DATE]==words[LOG_TIME]:
                                    current_date_time=words[LOG_DATE]
                                else:
                                    current_date_time=words[LOG_DATE] + ' ' + words[LOG_TIME]
                            # Additions for :
                            #current_date_time = words[0] + ':' + words[1] + ':' + words[2] 
                            # Extract all the information we want form the log line here
                            #ip = remove_prefix(words[LOG_IP].translate(str.maketrans('','','!@#$\"')), 'ip=')
                            if missile_direction == 'outgoing':
                                host = words[LOG_IP_OUTGOING].translate(str.maketrans('','','!@#$\"\[\]'))
                                if host.count(':') == 1:
                                    ip, port = host.split(':')
                                elif host.count(':') == 6:
                                    ip1, ip2, ip3, ip4, ip5, ip6, port = host.split(':')
                                    ip = ip1 + ':' + ip2 + ':' + ip3 + ':' + ip4 + ':' + ip5 + ':' + ip6
                                else:
                                    ip = host
                                #ip = remove_prefix(words[LOG_IP_OUTGOING].translate(str.maketrans('','','!@#$\"\[\]')), '')
                            else:
                                ip = remove_prefix(words[LOG_IP].translate(str.maketrans('','','!@#$\"\[\]')), '')
                            aa=re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip)
                            if not aa:
                                host = ip
                                if PRINT == True: print ('CONVERTING HOST TO IP')
                                try:
                                    ip = socket.gethostbyname(host)
                                except:
                                    ip = host
                            if PRINT == True: print ('IP:' + ip)
                            protocol = words[LOG_PROTOCOL]
                            service = remove_prefix(words[LOG_SERVICE],'b\'') # Password
                            service = service[:-2]
                            user = remove_prefix(words[LOG_USER],'[b\'')
                            user = user[:-1]
                            if MESSAGE_SEARCH == True:
                                if MESSAGE_FLAG.upper() in  words[LOG_MESSAGE].upper():
                                    color=1
                                else:
                                    color=1
                            else:
                                color=2
                            if PRINT == True:
                                print (ip, protocol, service)

                            if missile_direction == 'incoming':

                                # Maintain list of top protocols
                                if service=='':
                                    service='No Password'
                                if service in protocols:
                                    protocols[service]+=1
                                else:
                                    protocols[service]=1

                                # Maintain list of top users
                                if user=='':
                                    user='No User'
                                if user in users:
                                    users[user]+=1
                                else:
                                    users[user]=1
                                #if user == 'test' and service == 'test':
                                #    color=2
                            else:
                                service=''
                                user=''
                            if len(ip)>7:
                                # Write something about it to screen
                                if missile_direction == 'incoming':
                                    Messages.append(ip + ' ' * (16 - len(ip)) + '[' + user + ':' + service + ']')
                                else:
                                    Messages.append(ip + ' ' * (16 - len(ip)) + '[' + host + ']')
                                if len(Messages) > 49:
                                    Messages.pop(0)

                                # Find if we have already cached this information
                                ipdata = 'ips/' + ip + '.json'
                                if not os.path.isfile(ipdata):
                                    if PRINT == True:
                                        print ('Retrieving data for ' + ip)
                                    url = 'https://ipinfo.io/' + ip + '?token=' + TOKEN
                                    r = requests.get(url)
                                    json_data = json.loads(r.text)
                                    with open(ipdata, "w") as write_file:
                                        json.dump(json_data, write_file)
                                if os.path.isfile(ipdata):
                                    if PRINT == True:
                                        print ('Reading data from file ' + ipdata)
                                    # path exists
                                    with open(ipdata) as jd:
                                        json_data = json.load(jd)
                                        if 'loc' not in json_data:
                                            if PRINT == True:
                                                print ("No location data")
                                        else:
                                            FreeMissile=-1 # This bit of code looks for dead missiles
                                            for i in range(len(Missile)):
                                                if Missile[i][5]==False:
                                                    FreeMissile=i
                                                    break
                                            loc = json_data["loc"].split(",")
                                            mx = int(w * (float(loc[1])+180)/360)
                                            my = int(h * ((float(loc[0])*-1)+90)/180)
                                            LaunchedAlready=False
                                            for i in range(LaunchLocationCount):
                                                if LaunchLocation[i][0] == mx and LaunchLocation[i][1] == my:
                                                    LaunchedAlready=True
                                                    break
                                            if LaunchedAlready == False:
                                                LaunchLocation.append([])
                                                LaunchLocation[LaunchLocationCount].append(mx)
                                                LaunchLocation[LaunchLocationCount].append(my)
                                                LaunchLocation[LaunchLocationCount].append(ALERT_TIME + random.randint(0,ALERT_TIME))
                                                LaunchLocation[LaunchLocationCount].append(missile_direction)
                                                LaunchLocationCount = LaunchLocationCount + 1
                                            mx = mx + random.randint(-LAUNCH_DITHER,LAUNCH_DITHER)
                                            my = my + random.randint(-LAUNCH_DITHER,LAUNCH_DITHER)
                                            if FreeMissile==-1:
                                                # If there are no dead missile to reuse, create a new one
                                                Missile.append([])
                                            else:
                                                while len(Missile[FreeMissile])>0:
                                                    # This loop clears out old values
                                                    Missile[FreeMissile].pop()
                                            location=random.randint(0,len(DEFAULT_X)-1)
                                            if missile_direction == 'incoming':
                                                Missile[FreeMissile].append(mx)
                                                Missile[FreeMissile].append(my)
                                                Missile[FreeMissile].append(DEFAULT_X[location])
                                                Missile[FreeMissile].append(DEFAULT_Y[location])
                                            else:
                                                Missile[FreeMissile].append(DEFAULT_X[location])
                                                Missile[FreeMissile].append(DEFAULT_Y[location])
                                                Missile[FreeMissile].append(mx)
                                                Missile[FreeMissile].append(my)
                                            Missile[FreeMissile].append(0)
                                            Missile[FreeMissile].append(True)
                                            Missile[FreeMissile].append(protocol)
                                            Missile[FreeMissile].append(service)
                                            if missile_direction == 'incoming':
                                                Missile[FreeMissile].append(color)
                                            else:
                                                Missile[FreeMissile].append(-color)
                                        if 'country' not in json_data:
                                            if PRINT == True:
                                                print ("No country data")
                                        else:
                                            if PRINT == True:
                                                print (json_data["country"])
                                            if missile_direction == 'incoming':
                                                if json_data["country"] in countries:
                                                    countries[json_data["country"]]+=1
                                                else:
                                                    countries[json_data["country"]]=1
                    else:
                        # Make sure we read this line again in a second...
                        if len(line)<1:
                            line="END"
                        else:
                            # reset the shutdown if we are still reading lines
                            shutdown=0
                        if line[0].isdigit():
                            NOW_SECONDS = NOW_SECONDS + 1
                            if NOW_SECONDS>59:
                                NOW_SECONDS=0
                                NOW_MINUTES = NOW_MINUTES + 1
                                if NOW_MINUTES > 59:
                                    NOW_MINUTES = 0
                                    NOW_HOURS = NOW_HOURS + 1
                                    if NOW_HOURS > 23:
                                        NOW_HOURS = 0
                                        NOW_DAY = NOW_DAY + 1
                                        if NOW_DAY > 31:
                                            NOW_DAY = 1
                                            NOW_MONTH = NOW_MONTH + 1
                            CHECK_TIME = str(NOW_YEAR) + '-' + str(NOW_MONTH).zfill(2) + '-' + str(NOW_DAY).zfill(2) + 'T' + str(NOW_HOURS).zfill(2) + ':' + str(NOW_MINUTES).zfill(2) + ':' + str(NOW_SECONDS).zfill(2) + "."
                            if PRINT == True:
                                print ("Now checking for:", CHECK_TIME)
                            file.seek(RESET_LOCATION)
                            #if PRINT == True:
                            #    print (line[0:24], "Not yet")
                        FOUND_CHECK_TIME = False
    if TRACK_LAUNCHSITES==True:
        for i in range(LaunchLocationCount):                                  # Track Launch Locations
            if LaunchLocation[i][0]>0 and LaunchLocation[i][1]>0:
                if LaunchLocation[i][2] > 0:
                    LaunchLocation[i][2] = LaunchLocation[i][2] - 1
                    if LaunchLocation[i][2] < ALERT_TIME:
                        if LaunchLocation[i][3]=='incoming':
                            launch_detected = mysubtitle.render('LAUNCH DETECTED', True, (255, 255, 255))
                        else:
                            pygame.gfxdraw.aacircle(screen,LaunchLocation[i][0],LaunchLocation[i][1],20,BLUE)
                            launch_detected = mysubtitle.render('TARGET AQUIRED', True, (255, 255, 255))
                        screen.blit(launch_detected,(LaunchLocation[i][0]-50,LaunchLocation[i][1]+28))
    # display date and Time
    textsurface = mysubtitle.render(CHECK_TIME, True, (192, 192, 255))
    screen.blit(textsurface,(10,10))
    # Display messages #########################################################
    my=468
    for message in Messages:
        messagesurface = mysubtitle.render(message, True, (192, 192, 255))
        screen.blit(messagesurface,(10,my))
        my+=12
    # Display TOP countries ####################################################
    top=0
    my=850
    total_values = sum(countries.values())
    for key, value in sorted(countries.items(), key=lambda x: x[1], reverse=True):
        top+=1
        if top<=16:
            percent = str(int(100 * float(value) / float(total_values)))
            messagesurface = mysubtitle.render(key + ' ' + percent + '%', True, (255, 63, 63))
            screen.blit(messagesurface,(1760,my))
            my+=12
    # Display TOP protocols
    top=0
    my=850
    total_values = sum(protocols.values())
    for key, value in sorted(protocols.items(), key=lambda x: x[1], reverse=True):
        top+=1
        if top<=16:
            percent = str(int(100 * float(value) / float(total_values)))
            messagesurface = mysubtitle.render(key + ' ' + percent + '%', True, (255, 255, 128))
            screen.blit(messagesurface,(1450,my))
            my+=12
    # Display TOP users
    top=0
    my=850
    total_values = sum(users.values())
    for key, value in sorted(users.items(), key=lambda x: x[1], reverse=True):
        top+=1
        if top<=16:
            percent = str(int(100 * float(value) / float(total_values)))
            messagesurface = mysubtitle.render(key + ' ' + percent + '%', True, (255, 255, 128))
            screen.blit(messagesurface,(1050,my))
            my+=12

    title = myfont.render('HONEYPOT WARGAMES [2021]', True, (128, 255, 128))
    screen.blit(title,(1623,10))
    subtitle = mysubtitle.render('WARGAMES BY TH3S3CR3TAG3NT', True, (255, 63, 63))
    screen.blit(subtitle,(1728,36))
    pygame.display.flip()
    if VIDEO==True:
        f = 'map' + str(frame).zfill(10) + '.png'
        pygame.image.save(screen, f)
        frame +=1
    if QUIT_ON_END==True:
        MissileCount=0
        for i in range(len(Missile)):
            if Missile[i][5]==True:
                MissileCount = MissileCount + 1
        if MissileCount==0:
            shutdown=shutdown+1
            if shutdown > 60:
                if PRINT == True:
                    print("Not enough missiles")
                running=False;
file.close()

pygame.quit()

print("Please run: ffmpeg -r 60 -i map0%09d.png -r 60 output.mp4")
