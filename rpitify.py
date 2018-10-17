#!/usr/bin/python
import mpd
import pprint
import sys
import spotipy
import spotipy.util as util
from subprocess import Popen
import time

#https://python-mpd2.readthedocs.io/en/latest/topics/commands.html

# Spotify developer informations
USERNAME = "iot_pi"  # edit
CLIENT_ID = "dbd4c4b343d947d18659ad35c9b21830"  # edit
CLIENT_SECRET = "d43d3de39f9745f6b1196220d848efa7"  # edit
REDIRECT_URI = 'http://example.com/callback/'  # edit if you have change
# Scope for full access, adapt to needs
SCOPE = 'playlist-read-private playlist-read-collaborative playlist-modify-public '\
'playlist-modify-private streaming ugc-image-upload user-follow-modify '\
'user-follow-read user-library-read user-library-modify user-read-private '\
'user-read-birthdate user-read-email user-top-read user-read-playback-state '\
'user-modify-playback-state user-read-currently-playing user-read-recently-played'


class Rpitify():
    def __init__(self):
        self.modipy_proc = Popen('mopidy', shell=True)
        time.sleep(5)
        # Request access token to spotify
        token = util.prompt_for_user_token(
            USERNAME,
            scope=SCOPE,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI)
        self.sp = spotipy.Spotify(auth=token)
        self.playlists = self.sp.user_playlists('uq6n27o8m579h1370d5ln4r42')[
            'items']
        self.client = mpd.MPDClient(use_unicode=True)
        self.client.connect("localhost", 6600)
        self.client.clear()
        self.client.disconnect()

    def connect(self):
        self.client.connect("localhost", 6601)

    def disconnect(self):
        self.client.disconnect()

    def setVol(self, volume):
        self.client.setvol(volume)

    def loadPlaylist(self, playlist_name):
        for playlist in self.playlists:
            if playlist['name'] == playlist_name:
                results = self.sp.user_playlist(
                    'uq6n27o8m579h1370d5ln4r42',
                    playlist['id'],
                    fields="tracks,next")
                tracks = results['tracks']
                for i, item in enumerate(tracks['items']):
                    track = item['track']['uri']
                    #print(item['track']['uri'])
                    self.client.add(track)
                break

    def resume(self):
        self.client.pause(0)

    def pause(self):
        self.client.pause(1)

    def playPlaylist(self, track_num):
        self.client.play(track_num)

    def cleanup(self):
        print("Cleaning up modipy - i hope")
        self.client.close()
        self.modipy_proc.kill()
        self.client.kill()

    def shufflePlaylist(self):
        self.client.shuffle()
        '''
            for playlist in playlists['items']:
                if playlist['owner']['id'] == 'uq6n27o8m579h1370d5ln4r42':
                    print()
                    print(playlist['name'])
                    print('  total tracks', playlist['tracks']['total'])
                    results = sp.user_playlist(
                        'uq6n27o8m579h1370d5ln4r42',
                        playlist['id'],
                        fields="tracks,next")
                    my_playlists[playlist['uri']] = []
                    #print(playlist['id'])

                    tracks = results['tracks']

                    for i, item in enumerate(tracks['items']):
                        my_playlists[playlist['uri']].append(item['track']['uri'])
                        print(item['track']['uri'])



                        for playlist, tracks in my_playlists.items():
                            for track in tracks:
                                print(track)
                                client.add(track)
        '''
