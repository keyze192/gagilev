# vadim/steam.py
import requests
from django.conf import settings
from django.urls import reverse
from urllib.parse import parse_qs, urlparse
import re
from datetime import datetime

class SteamAPI:
    def __init__(self):
        self.api_key = getattr(settings, 'STEAM_API_KEY', '')
        self.return_url = getattr(settings, 'STEAM_RETURN_URL', 'http://127.0.0.1:8000/steam/callback/')
    
    def get_login_url(self):
        params = {
            'openid.ns': 'http://specs.openid.net/auth/2.0',
            'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
            'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
            'openid.mode': 'checkid_setup',
            'openid.return_to': self.return_url,
            'openid.realm': 'http://127.0.0.1:8000',
        }
        
        from urllib.parse import urlencode
        return f"https://steamcommunity.com/openid/login?{urlencode(params)}"
    
    def validate_steam_response(self, request):
        params = request.GET.dict()
        if 'openid.mode' not in params or params['openid.mode'] != 'id_res':
            return None
        if 'openid.signed' not in params:
            return None
        claimed_id = params.get('openid.claimed_id', '')
        match = re.search(r'https?://steamcommunity\.com/openid/id/(\d+)', claimed_id)
        
        if match:
            steam_id = match.group(1)
            return steam_id
        
        return None
    
    def get_player_summary(self, steam_id):
        if not self.api_key:
            print("STEAM_API_KEY не настроен в settings.py")
            return None
        
        url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        params = {
            'key': self.api_key,
            'steamids': steam_id,
            'format': 'json'
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data and 'response' in data and 'players' in data['response'] and data['response']['players']:
                player = data['response']['players'][0]
                
                created_at = None
                if 'timecreated' in player:
                    created_at = datetime.fromtimestamp(player['timecreated'])
                
                return {
                    'steam_id': player.get('steamid'),
                    'personaname': player.get('personaname', ''),
                    'profileurl': player.get('profileurl', ''),
                    'avatar': player.get('avatar', ''),
                    'avatarmedium': player.get('avatarmedium', ''),
                    'avatarfull': player.get('avatarfull', ''),
                    'realname': player.get('realname', ''),
                    'loccountrycode': player.get('loccountrycode', ''),
                    'timecreated': created_at,
                    'personastate': player.get('personastate', 0),
                    'communityvisibilitystate': player.get('communityvisibilitystate', 0),
                }
        except Exception as e:
            print(f"Ошибка при получении данных Steam: {e}")
        
        return None
    
    def get_player_friends(self, steam_id):
        if not self.api_key:
            return []
        
        url = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/"
        params = {
            'key': self.api_key,
            'steamid': steam_id,
            'relationship': 'friend'
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data and 'friendslist' in data:
                return data['friendslist'].get('friends', [])
        except:
            pass
        
        return []