import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from SPT_C import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET

def Spoti_Find(string):
    auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    track_data = sp.search(q='track:'+ string ,type='track', limit=20)

    track_result = []
    for i, item in enumerate(track_data['tracks']['items']):
        track = item['album']
        track_id = item['id']
        link = f"https://open.spotify.com/track/{track_id}"
        track_name = item['name']
        track_result.append({"Artist":track['artists'][0]['name'],
                             "Album":track['name'],
                             "Track":track_name,
                             "Link":link})
    return track_result