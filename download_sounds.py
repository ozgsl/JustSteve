import os
import urllib.request

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

ensure_dir('assets/sounds')

sounds = {
    'music_menu.mp3': 'https://ia800305.us.archive.org/30/items/MinecraftVolumeAlpha/09%20-%20Sweden.mp3',
    'music_game.mp3': 'https://ia800305.us.archive.org/30/items/MinecraftVolumeAlpha/03%20-%20Subwoofer%20Lullaby.mp3',
    'hit.mp3': 'https://www.myinstants.com/media/sounds/minecraft_hit.mp3',
    'zombie.mp3': 'https://www.myinstants.com/media/sounds/zombie-say1.mp3',
    'creeper.mp3': 'https://www.myinstants.com/media/sounds/creeper-hiss.mp3',
    'skeleton.mp3': 'https://www.myinstants.com/media/sounds/skeleton_say1.mp3',
    'enderman.mp3': 'https://www.myinstants.com/media/sounds/endermen-teleport.mp3',
    'coin.mp3': 'https://www.myinstants.com/media/sounds/mario-coin.mp3',
    'jump.mp3': 'https://www.myinstants.com/media/sounds/mario-jump-sound.mp3'
}

for name, url in sounds.items():
    path = os.path.join('assets/sounds', name)
    if not os.path.exists(path):
        print(f"Downloading {name}...")
        try:
            # Fake user agent to avoid 403 Forbidden
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
            print(f"[OK] {name}")
        except Exception as e:
            print(f"[ERROR] Failed to download {name}: {e}")
    else:
        print(f"[SKIP] {name} already exists.")

print("Sound download complete.")
