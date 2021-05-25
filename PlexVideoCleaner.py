#!/app/env/bin/python

from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount
from plexapi import utils

from datetime import datetime

import json
import math
import requests
import time
import os


#################################################
#
#
#
#################################################
debug = False

process_flag = {
    'show': True,
    'movie': False
}

baseurl = 'http:/localhost:32400'
token = None
username = None
password = None

days_to_retain = 0
percent_threshold = 100
sleep = 60

if 'PLEX_VIDEO_CLEANER_DAYS_TO_RETAIN' in os.environ:
    days_to_retain = utils.cast(int,os.environ['PLEX_VIDEO_CLEANER_DAYS_TO_RETAIN']) - 1
if 'PLEX_VIDEO_CLEANER_PERCENT_THRESHOLD' in os.environ:
    percent_threshold = utils.cast(int,os.environ['PLEX_VIDEO_CLEANER_PERCENT_THRESHOLD']) - 1
if 'PLEX_VIDEO_CLEANER_SLEEP' in os.environ:
    sleep = utils.cast(int,os.environ['PLEX_VIDEO_CLEANER_SLEEP'])

if 'PLEX_VIDEO_CLEANER_DEBUG' in os.environ:
    debug = utils.cast(bool,os.environ['PLEX_VIDEO_CLEANER_DEBUG'])
if 'PLEX_VIDEO_CLEANER_SHOWS' in os.environ:
    process_flag['show'] = utils.cast(bool,os.environ['PLEX_VIDEO_CLEANER_SHOWS'])
if 'PLEX_VIDEO_CLEANER_MOVIES' in os.environ:
    process_flag['movie'] = utils.cast(bool,os.environ['PLEX_VIDEO_CLEANER_MOVIES'])

if 'PLEX_VIDEO_CLEANER_BASEURL' in os.environ:
    baseurl = os.environ['PLEX_VIDEO_CLEANER_BASEURL']
if 'PLEX_VIDEO_CLEANER_TOKEN' in os.environ:
    token = os.environ['PLEX_VIDEO_CLEANER_TOKEN']
if 'PLEX_VIDEO_CLEANER_USERNAME' in os.environ:
    username = os.environ['PLEX_VIDEO_CLEANER_USERNAME']
if 'PLEX_VIDEO_CLEANER_PASSWORD' in os.environ:
    password = os.environ['PLEX_VIDEO_CLEANER_PASSWORD']

if token == None:
    if username == None or password == None:
        raise SystemError("No Authentication Information")

    account = MyPlexAccount(username, password)
    plex = account.resource(baseurl).connect()
    if plex._token:
        token = plex._token
    else:
        raise SystemError("Username/Password Failes")


def getDaysSince(then, now=datetime.now()):

    difference = now - then  # For build-in functions
    difference_in_s = difference.total_seconds()

    return math.floor(difference_in_s / 86400)


def process_delete(key):

    url = baseurl + key + '?X-Plex-Token=' + token
    r = requests.delete(url)
    if r.status_code != 200:
        print(url, "Error Code", r.status_code)

    time.sleep(10)


def refresh(key):

    print('***', 'REFRESHING', key, '***')
    url = baseurl + '/library/sections/' + str(key) + '/refresh?X-Plex-Token=' + token
    print(url)

    r = requests.delete(url)

    if r.status_code != 200:
        print(url, "Error Code", r.status_code)

#################################################
#
#
#
#################################################


def process_section(section):

    # If the section is for TV Shows, process that section
    # as a show
    if section.type == 'show':
        process_section_show(section)
        refresh(section.key)

    # If the section is for Movies, process that section
    # as a movie
    if section.type == 'movie':
        process_section_movie(section)
        refresh(section.key)


def process_section_show(section):

    # Loop through the list of shows in that
    # section
    for show in section.search():
        process_show(show)


def process_show(show):

    # Loop through the list of seasons for that
    # show
    for season in show.seasons():
        process_show_season(season)


def process_show_season(season):

    # Loop through the list of episodes for that
    # season
    for episode in season.episodes():
        process_show_season_episode(episode)


def process_show_season_episode(episode):

    # If it has been viewed partially, what percent
    # of the episode been viewed
    duration = episode.duration
    viewOffset = 0
    if episode.viewOffset:
        viewOffset = episode.viewOffset
    percent = math.floor((viewOffset / duration) * 100)


    daysSinceViewed = 0
    if episode.lastViewedAt:
        daysSinceViewed = getDaysSince(episode.lastViewedAt)

    # Does the viewCount or percentViewed meet the delete
    # threshold
    if episode.viewCount > 0 and daysSinceViewed > days_to_retain:
        delete_episode(episode)
        print(episode)
    else:
        if percent > percent_threshold and daysSinceViewed > days_to_retain:
            delete_episode(episode)
            print(episode)
        else:
            delete_episode(episode, False)



def delete_episode(episode, delete=True):

    key = episode.key
    showTitle = episode.grandparentTitle
    seasonEpisode = episode.seasonEpisode
    episodeTitle = episode.title
    action = '  KEEP'

    if delete:
        action = '  DELETE'

    if debug & delete:
        print(action, key, showTitle, seasonEpisode, episodeTitle)

    if delete:
        print(action, key, showTitle, seasonEpisode, episodeTitle)
        process_delete(key)


def process_section_movie(section):
    print("Movie Processing is not yet available")

#################################################
#
#
#
#################################################


def main():

    # for k, v in os.environ.items():
    #     print(f'{k}={v}')

    # dd/mm/YY H:M:S
    dt_string = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    print("***************************************")
    print("* ")
    print("* ", dt_string)
    print("* ")
    print("***************************************")

    plex = PlexServer(baseurl, token)

    # Load all sections
    sections = plex.library.sections()

    # Loop through the sections
    for section in sections:
        
        # If the process_flag for that type is true
        # process that section
        if process_flag[section.type]:
            process_section(section)


#################################################
#
#
#
#################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
