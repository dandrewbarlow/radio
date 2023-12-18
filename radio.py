#! /usr/bin/env python3
# Andrew Barlow
# radio.py
# 
# Description
# simple CLI internet radio interface

# IMPORTS ##################################################

# TODO switch to the python vlc lib that I found out about after making this

# python libs
import subprocess
import os

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

def play_station(station):

    if (station == "Exit"):
        return 0

    display_info(station)

    # KeyboardInterrupt is our exit routine, not an error
    try:
        subprocess.run(['cvlc', station["url"] ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
    # TODO changing radio stations while running
    except KeyboardInterrupt as e:
        console.clear()
        return 1

# feedback
def display_info(station):
    # use rich tables for pretty output
    # https://rich.readthedocs.io/en/stable/tables.html
    table = Table(title="Radio", show_lines=True)

    table.add_column("Station Info")
    table.add_column("User Interface")
    table.add_row( f'Station Name: [purple]{station["name"]}[/purple]',  'Return to menu: [red]<ctrl> + c[/red]')
    table.add_row( f'Station URL: [blue]{station["url"]}[/blue]', 'Quit: 2x [red]<ctrl> + c[/red]')
    
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

main()
