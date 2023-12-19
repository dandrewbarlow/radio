#! /usr/bin/env python3
# Andrew Barlow
# radio.py
# 
# Description
# simple CLI internet radio interface

# IMPORTS ##################################################

import time
import vlc

# python libs
import os
import requests

# rich: pretty python scripts
# https://rich.readthedocs.io/en/stable/index.html
from rich import print
from rich.console import Console
from rich.table import Table
from rich.traceback import install

# im lazy
import fzflib

# INIT ##################################################

# location of radio stations + metadata
# see README.md for formatting instructions
config_file = 'config.txt'

script_dir = os.path.abspath( os.path.dirname( __file__ ) )

# init rich traceback
install(show_locals=True)

# init rich console
console = Console();

# init fuzzy finder
fzf = fzflib.FZF()

# clear screen b4 running
console.clear()

# https://www.thiscodeworks.com/stream-internet-radio-playlist-with-python-vlc-python-music/61f74624b50e540015bbadad
instance = vlc.Instance('--intf dummy --verbose -1')

# non-verbose vlc env var
# ? doesn't work for all media types
os.environ["VLC_VERBOSE"] = str("-1")

# HELPER ##################################################

# read file into an array of its lines
def readFile(filepath):
    # define list file
    f = os.path.join(script_dir, filepath)

    # open that file
    file = open(f, 'r')

    # read file into an array
    lines = file.readlines()

    return lines;

def parse_stations(filepath):

    lines = readFile(filepath)

    # prep to loop through lines
    lineNum = 0
    stations = []

    # loop through lines
    for line in lines:

        lineNum += 1

        # if a url is found
        if line[0:4] == 'http':

            url = line.rstrip()

            station_name = ""

            # if no station name found, use url as ref
            if lines[lineNum-2][0] == '#':
                station_name = lines[lineNum-2][2:].strip()
            else:
                station_name = url

            # parse station data into dict
            station = {
                    'name': station_name,
                    'url': url
            }

            # add to station list
            stations.append(station);

    return stations

# UI to pick which station to listen to
def pick_station(stations):
    # create a list of just the names for fzf browsing
    stationList = [ s['name'] for s in stations ]

    stationList.append('Exit')

    # use fzf to pick station
    fzf.input = stationList

    station_choice = fzf.prompt()

    station = "Exit"

    for s in stations:
        if s['name'] == station_choice:
            station = s

    return station

# https://stackoverflow.com/questions/28440708/python-vlc-binding-playing-a-playlist
def verify_stream(url):

    print('Verifying stream...')

    ext = parse_extension(url)
    test_pass = False    

    try:
        if url[:4] == 'file':
            test_pass = True
        else:
            r = requests.get(url, stream=True)
            test_pass = r.ok
    except Exception as e:
        print('failed to get stream: {e}'.format(e=e))
        test_pass = False

    return test_pass

# get extension of a url
def parse_extension(url):
    ext = (url.rpartition(".")[2])[:3]
    return ext

# high level media playback
def play_station(station):

    # if the user chose to exit, return 0
    if (station == "Exit"):
        return 0

    # get station url
    url = station['url']

    if not verify_stream(url):
        return 1


    # check url extension
    ext = parse_extension(url)

    player = None

    # playlists / audio streams are handled differently
    if ext == 'pls' or ext == 'm3u':
        player = create_vlc_playlist_player(url)
    else:
        player = create_vlc_audio_player(url)

    # KeyboardInterrupt is our exit routine, not an error
    try:
        # start the stream
        player.play()

        # show stream info
        display_info(station)

        # TODO get user input
        while 1:
            time.sleep(1)
            pass

    except KeyboardInterrupt as e:
        # stop the stream
        player.stop()

        # clear the screen
        console.clear()
        return 1

# create a vlc player for an audio stream
def create_vlc_audio_player(url):
    player = instance.media_player_new("--verbose -1")
    media = instance.media_new(url)
    media.get_mrl()
    player.set_media(media)

    return player

# create a vlc player for a audio playlist
def create_vlc_playlist_player(url):
    media_list = instance.media_list_new([url])
    list_player = instance.media_list_player_new()
    list_player.set_media_list(media_list)

    return list_player

def get_meta_from_player(player):

    # extract the media player from a playlist player
    if type(player) == vlc.MediaListPlayer:
        player = player.get_media_player()

    media = player.get_media()

    # ? only metadata that seems to ever be parsed from internet streams
    # ? rarely useful or verbose
    # TODO find out if there's a better way
    meta = media.get_meta(vlc.Meta.Title)

    return meta

# feedback
def display_info(station):
    # use rich tables for pretty output
    # https://rich.readthedocs.io/en/stable/tables.html
    table = Table(title="Radio", show_lines=True)

    table.add_column("Station Info")
    table.add_column("User Interface")
    table.add_row( f'Station Name: [purple]{station["name"]}[/purple]',  'Return to menu: [red]<ctrl> + c[/red]')
    table.add_row( f'Station URL: [blue]{station["url"]}[/blue]', 'Quit: 2x [red]<ctrl> + c[/red]')
    
    console.clear()
    console.print(table)

def radio(filepath):
    stations = parse_stations(filepath)
    station = None

    try:
        station = pick_station(stations)
    except KeyboardInterrupt as e:
        return 0

    return play_station(station)


# MAIN ##################################################

def main():
    # it's not hacky if it works
    while(radio(config_file) != 0):
        pass

if __name__ == "__main__":
    main()
