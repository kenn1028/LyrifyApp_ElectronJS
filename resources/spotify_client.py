'''
Spotify Lyrics Player Project (June 2020)

> Spotify Web API Client Class <

References:
Authorization Guide using Authorization Code flow:  https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow

Authorization Scopes: https://developer.spotify.com/documentation/general/guides/scopes/

https://stackoverflow.com/questions/51842280/spotify-api-scopes-not-being-recognized-not-able-to-access-user-info

Dependencies:
pip install requests
'''

import base64
import datetime
from urllib.parse import urlencode
import webbrowser

import math
import json
import requests
# client_id = '835cea40f4bd4eec8809798ee62f1cf9'
# client_secret = '06e06fd5087246f7b644f28fa6d9924c'

class SpotifyAPI(object):
    access_token = None
    refresh_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"
    redirect_uri = "https://www.google.com"
    auth_url = 'https://accounts.spotify.com/authorize'
    auth_code = None

    def __init__(self, client_id = '835cea40f4bd4eec8809798ee62f1cf9', client_secret = '06e06fd5087246f7b644f28fa6d9924c', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    '''
    Authorization Code Flow
    1. Request for authorization (along with scopes, if needed); redirects user to a website

    *Input: client_id, client_secret
    *Output: auth_code, Authorization Code for access_token and refresh_token

    *relevant only
    '''

    def get_scopes(self):
        scopes = 'user-read-currently-playing user-read-playback-state playlist-read-private playlist-read-collaborative'
        params = urlencode({
            "client_id": f"{self.client_id}",
            "response_type": "code",
            "redirect_uri": f"{self.redirect_uri}",
            "scope": scopes
        })

        # redirect_url = f"{auth_url}?{params}"
        # return redirect_url
        #print(f"{self.auth_url}?{params}")
        webbrowser.open(f"{self.auth_url}?{params}")

    # def get_playback_scope(self):
    #     scopes = 'user-read-currently-playing user-read-playback-state'
    #     params = urlencode({
    #         "client_id": f"{self.client_id}",
    #         "response_type": "code",
    #         "redirect_uri": f"{self.redirect_uri}",
    #         "scope": scopes
    #     })
    #
    #     # redirect_url = f"{auth_url}?{params}"
    #     # return redirect_url
    #     #print(f"{self.auth_url}?{params}")
    #     webbrowser.open_new(f"{self.auth_url}?{params}")
    #     #return f"{auth_url}?{params}"

    '''
    2. Request for access_token and refresh_token

    *Input: auth_code
    *Output: access_token, refresh_token
    '''

    def get_token_headers(self):
        client_id = self.client_id
        client_secret = self.client_secret

        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

        return {
            'Authorization': f'Basic {client_creds_b64}'
        }

    def get_token_body(self):
        return {
            "grant_type" : "authorization_code",
            "code": f"{self.auth_code}",
            "redirect_uri": f"{self.redirect_uri}"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_body()
        token_headers = self.get_token_headers()

        r = requests.post(token_url, data = token_data, headers = token_headers)
        #print(r.status_code)
        if r.status_code not in range(200,299): #checks if status code is valid
            raise Exception("Could not authenticate client")
            # return False

        token_response_data = r.json() #returns json dict of access_token, 'token_type' = Bearer, 'scope', 'expires_in'

        #print(token_response_data)

        access_token = token_response_data['access_token']
        refresh_token  = token_response_data['refresh_token']
        self.access_token = access_token
        self.refresh_token = refresh_token

        with open("data/tokens.txt", "w") as token:
            token.write(f"{access_token} {refresh_token}")

        now = datetime.datetime.now()
        expires_in = token_response_data['expires_in'] #in seconds
        expires = now + datetime.timedelta(seconds=expires_in) #countsdown to 0
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now  #false if expires != 0
        return True

    def get_access_token(self):
        auth_done = self.perform_auth()
        if not auth_done:
                raise Exception("Authentication failed")
        access_token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif access_token == None:
            self.perform_auth()
            return self.get_access_token()
        return access_token

    def get_resource_headers(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization" : f"Basic {access_token}"
        }
        return headers

    '''
    3. Request functions

    *Input: access_token (basic or scoped), refresh_token
    *Output: varies (based from desired output of the function)

    See: https://developer.spotify.com/documentation/web-api/reference/
    '''

# ============================== Playlist and Album Fetch Functions ============================== #

    def get_current_song(self):
        '''
        Returns data of player's currently playing song

        Note: access token requires 'user-read-currently-playing user-read-playback-state' scopes
        '''
        endpoint = 'https://api.spotify.com/v1/me/player/currently-playing'
        headers = {
            "Authorization" : f"Bearer {self.access_token}"
        }

        self.perform_refresh()

        r = requests.get(endpoint, headers = headers)
        # print(r.status_code)

        if r.status_code == 204:
            raise ValueError("There is no song currently playing.")

        if r.status_code not in range(200,299):
            return {}
        # print(r.json())
        data = r.json()

        def convertMillis(millis):
            seconds = math.floor((millis/1000)%60)
            minutes = math.floor((millis/(1000*60))%60)
            hours = math.floor((millis/(1000*60*60))%24)

            if len(str(seconds)) == 1:
                if hours == 0:
                    return f"{minutes}:0{seconds}"
                return f"{hours}:{minutes}:0{seconds}"

            if hours == 0:
                return f"{minutes}:{seconds}"
            return f"{hours}:{minutes}:{seconds}"

        parsed_data = {
            "song_name": data['item']['name'],
            "song_link": data["item"]["external_urls"]["spotify"],
            "artist": data["item"]["artists"][0]["name"],
            'album': data['item']['album']['name'],
            "images": data["item"]["album"]["images"][1],
            "track_id": data['item']['id'],
            'artist_id': data['item']['artists'][0]['id'],
            'artist_link': data['item']['artists'][0]['external_urls']['spotify'],
            'song_length':  convertMillis(data["item"]["duration_ms"]),
            'song_progress': convertMillis(data["progress_ms"])
        }

        # print(parsed_data["song_link"], parsed_data["artist_link"])
        # print('\n', parsed_data)

        r = requests.get(parsed_data["images"]["url"])

        try:
            with open("data/song_cover.jpg", "rb") as image:
                bytes = base64.b64encode(image.read())

            with open("data/song_cover.jpg", "wb") as image:
                if bytes != r.content:
                    image.write(r.content)
        except:
            with open("data/song_cover.jpg", "wb") as image:
                image.write(r.content)

        image.close()
        return parsed_data

    def get_user_playlists(self, user_id):
        '''
        Returns list with dictionary of another user's public playlists {"name": 'playlist', "playlist_id": '1'}

        Example:
        playlist_list = [
            {'name': 'K-Indie Picks', 'playlist_id': '37i9dQZF1DXdTb8AG95jne'}
            {'name': 'Japanese City Pop', 'playlist_id': '4x2UJm2TpYcciuws1Mxj8L'}
            {'name': 'chill japanese vibes', 'playlist_id': '1KYCoW1hsKedCnKEF4RvVY'}
            {'name': '[KPOP] STAN LIST ', 'playlist_id': '6aneMCMSIzBNUWTqkgf4uk'}
        ]
        '''
        endpoint = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        headers = {
            "Authorization" : f"Bearer {self.access_token}"
        }

        self.perform_refresh()

        r = requests.get(endpoint, headers = headers)
        # print(r.status_code)


        if r.status_code not in range(200,299):
            return {}

        data = r.json()
        #print(json.dumps(data, sort_keys=True, indent=4, separators=(',', '; ')))

        playlist_list = []

        for i in range(len(data['items'])):
            playlist_list.append({
                "name": data['items'][i]['name'],
                "playlist_id": data['items'][i]['id']
            })
        #print(playlist_list)
        return playlist_list

    def get_current_playlists(self):
        '''
        Returns list with dictionary of current user's playlists {"name": 'playlist', "playlist_id": '1'}

        Example:
        playlist_list = [
            {'name': 'K-Indie Picks', 'playlist_id': '37i9dQZF1DXdTb8AG95jne'}
            {'name': 'Japanese City Pop', 'playlist_id': '4x2UJm2TpYcciuws1Mxj8L'}
            {'name': 'chill japanese vibes', 'playlist_id': '1KYCoW1hsKedCnKEF4RvVY'}
            {'name': '[KPOP] STAN LIST ', 'playlist_id': '6aneMCMSIzBNUWTqkgf4uk'}
        ]

        Note: access token requires 'playlist-read-private playlist-read-collaborative' scopes
        '''
        endpoint = 'https://api.spotify.com/v1/me/playlists'
        headers = {
            "Authorization" : f"Bearer {self.access_token}"
        }

        self.perform_refresh()

        r = requests.get(endpoint, headers = headers)
        #print(r.status_code)


        if r.status_code not in range(200,299):
            return {}

        data = r.json()
        #print(json.dumps(data, sort_keys=True, indent=4, separators=(',', '; ')))

        playlist_list = []

        for i in range(len(data['items'])):
            playlist_list.append({
                "name": data['items'][i]['name'],
                "playlist_id": data['items'][i]['id']
            })

        return playlist_list

    def get_playlist_tracks(self, playlist_id):
        '''
        Returns list with dictionary of playlist's tracks {"song_id": 'playlist', "title": 'name', "artist": 'artist'}

        Example:
        playlist_list = [
            {'song_id': '1e7eOq89QU6vGYCJp9yW2L', 'title': 'Sunrise', 'artist': 'GFRIEND'}
            {'song_id': '0iNFkX82Qba4d3MoT9BKz0', 'title': 'Compas', 'artist': 'GFRIEND'}
            {'song_id': '23XXMK9SQBFwndnbgbcMPa', 'title': 'WEE WOO', 'artist': 'PRISTIN'}
            {'song_id': '5kFakScPV7ZWXStUSvQmxA', 'title': 'BABE', 'artist': 'HyunA'}
        ]
        '''
        endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {
            "Authorization" : f"Bearer {self.access_token}"
        }

        self.perform_refresh()

        r = requests.get(endpoint, headers = headers)
        #print(r.status_code)


        if r.status_code not in range(200,299):
            return {}

        data = r.json()
        # print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))

        song_list = []

        for i in range(len(data['items'])):
            song_list.append({
                'song_id': data['items'][i]['track']['id'],
                'title': data['items'][i]['track']['name'],
                'artist': data['items'][i]['track']['artists'][0]['name']
            })

        next_page = data['next']
        #print(next_page)

        while next_page != None:
            r = requests.get(next_page, headers = headers)
            self.perform_refresh()
            if r.status_code not in range(200,299):
                return {}
            data = r.json()
            #print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

            try:

                for i in range(len(data['items'])):
                    song_list.append({
                        'song_id': data['items'][i]['track']['id'],
                        'title': data['items'][i]['track']['name'],
                        'artist': data['items'][i]['track']['artists'][0]['name']
                    })

                next_page = data['next']

            except:
                next_page = data['next']
                r = requests.get(next_page, headers = headers)
                data = r.json()
                for i in range(len(data['items'])):
                    song_list.append({
                        'song_id': data['items'][i]['track']['id'],
                        'title': data['items'][i]['track']['name'],
                        'artist': data['items'][i]['track']['artists'][0]['name']
                    })
                return song_list

        return song_list

#  ============================== User Profile Fetch Functions  ============================== #

    def get_current_profile(self):
        '''
        Returns current user's profile link and saves the image
        '''

        endpoint = "https://api.spotify.com/v1/me"
        headers = {
            "Authorization" : f"Bearer {self.access_token}"
        }

        self.perform_refresh()

        r = requests.get(endpoint, headers = headers)
        #print(r.status_code)


        if r.status_code not in range(200,299):
            return {}

        data = r.json()

        profile_link = data["external_urls"]["spotify"]
        image_link = data["images"][0]["url"]

        r = requests.get(image_link)

        try:
            with open('data/profile_picture.jpg', 'rb') as image:
                bytes = base64.b64encode(image.read())

            with open('data/profile_picture.jpg', 'wb') as image:
                if bytes != r.content:
                    image.write(r.content)
        except:
            with open('data/profile_picture.jpg', 'wb') as image:
                image.write(r.content)

        image.close()
        return profile_link

    def get_user_profile(self, user_id):
        pass

#  ============================== Search Functions  ============================== #

    # def get_resource(self, lookup_id, resource_type = "albums", version = "v1"):
    #     endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
    #     headers = self.get_resource_headers()
    #     r = requests.get(endpoint, headers = headers)
    #     if r.status_code not in range(200,299):
    #         return {}
    #     return r.json()
    #
    # def get_album(self, lookup_id):
    #     return self.get_resource(lookup_id, resource_type = 'albums', version = 'v1')
    #
    # def get_artist(self, lookup_id):
    #     return self.get_resource(lookup_id, resource_type = 'artists', version = 'v1')
    #
    # def base_search(self, query_params):
    #     headers = self.get_resource_headers()
    #     endpoint = "https://api.spotify.com/v1/search"
    #     lookup_url = f"{endpoint}?{query_params}"
    #     print(lookup_url)
    #     r = requests.get(lookup_url, headers = headers)
    #     if r.status_code not in range(200,299):
    #         return {}
    #     return r.json()
    #     #print(r.json())
    #
    # def search(self, query = None, operator = None, operator_query = None, search_type = 'track'):
    #     if query == None:
    #         raise Exception("A query is required")
    #     if isinstance(query, dict):
    #         query = " ".join([f"{k}:{v}" for k, v in query.items()]) #Converts dictionary into list
    #     if operator != None and operator_query != None:
    #         if operator.lower() == "or" or operator.lower() == "not":
    #             operator = operator.upper()
    #             if isinstance(operator_query, str):
    #                 query = f"{query} {operator} {operator_query}"
    #     query_params = urlencode({"q" : query, "type": search_type.lower()})
    #     print(query_params)
    #     return self.base_search(query_params)

    '''
    4. Request for new access_token using refresh_token; function similar to perform_auth() but uses refresh_token as new value for {auth_code}

    Note: access_token expires after 3600s or 1hr

    *Input: refresh_token
    *Output: access_token, refresh_token
    '''

    def get_refresh_body(self):
        return {
            "grant_type": "refresh_token",
            "refresh_token": f"{self.refresh_token}"
        }

    def perform_refresh(self):
        token_url = self.token_url

        if self.refresh_token == None:
            try:
                with open('data/tokens.txt', 'r') as tokens:
                    for lines in tokens:
                        token = lines.split()
                        #self.access_token = token[0]
                        self.refresh_token = token[1]
            except:
                pass

        token_data = self.get_refresh_body()
        token_headers = self.get_token_headers()

        r = requests.post(token_url, data = token_data, headers = token_headers)

        #print(r.status_code)
        if r.status_code not in range(200,299): #checks if status code is valid
            raise Exception("Could not authenticate client")
            # return False

        token_response_data = r.json() #returns json dict of access_token, 'token_type' = Bearer, 'scope', 'expires_in'

        #print(token_response_data)
        self.access_token = token_response_data["access_token"]

        now = datetime.datetime.now()
        expires_in = token_response_data['expires_in'] #in seconds
        expires = now + datetime.timedelta(seconds=expires_in) #countsdown to 0
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now  #false if expires != 0

        return True

#  ========================================================================================== #

#### void main() ####

# spotify = SpotifyAPI(client_id = client_id, client_secret = client_secret)
#
# spotify.get_scopes()
# spotify.auth_code = input("Enter Code: ")
# spotify.perform_auth()

### Current Song Test ###

# while True:
#     data = spotify.get_current_song()
#     for k in data:
#         print(k, data[k])
    #print(spotify.access_token, '/n', spotify.refresh_token)

### Playlist Scrape Test ###

# list = spotify.get_playlist_tracks("30lnYh0901lFkD3ev6GwYe")
# for i in list: print(i)
# print('Number of songs: ', len(list), "\n")
#
# list = spotify.get_current_playlists()
# print("Current User's playlists")
# for i in list: print(i)
#
# user_id = '2263xw43fnspn6cpngqylgszq'
# list = spotify.get_user_playlists(user_id = user_id)
# print('\n')
# print(user_id + "'s playlists")
# for i in list: print(i)

# spotify:user:uy6wcttkt4ycnqhe7gynrl3rq kenn
# 2263xw43fnspn6cpngqylgszq chai
