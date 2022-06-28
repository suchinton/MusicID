import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

if len(sys.argv) > 1:
    name = ' '.join(sys.argv[1:])
else:
    name = 'Radiohead'

results = spotify.search(q='artist:' + name, type='artist')
items = results['artists']['items']
if len(items) > 0:
    artist = items[0]
    print(artist['name'], artist['images'][0]['url'])

## export SPOTIPY_CLIENT_ID='a2ab52da41ed4d4b9d94d6621fd987dc'
## export SPOTIPY_CLIENT_SECRET='20cf463d35104190991831bf2d30c7f0'