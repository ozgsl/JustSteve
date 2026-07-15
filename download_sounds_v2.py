import os
import urllib.request

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

ensure_dir('assets/sounds')

# InventivetalentDev minecraft-assets repodan orijinal sesler (1.16.5)
base_url = 'https://raw.githubusercontent.com/InventivetalentDev/minecraft-assets/1.16.5/assets/minecraft/sounds/'

sounds = {
    'hit.ogg': base_url + 'damage/hit1.ogg',
    'zombie.ogg': base_url + 'mob/zombie/say1.ogg',
    'creeper.ogg': base_url + 'random/fuse.ogg',
    'explode.ogg': base_url + 'random/explode1.ogg',
    'skeleton.ogg': base_url + 'mob/skeleton/say1.ogg',
    'enderman.ogg': base_url + 'mob/endermen/portal.ogg', # tp sesi
    'coin.ogg': base_url + 'random/levelup.ogg', # xp sound
    'jump.ogg': base_url + 'mob/slime/jump1.ogg',
    'stomp.ogg': base_url + 'mob/slime/attack1.ogg'
}

for name, url in sounds.items():
    path = os.path.join('assets/sounds', name)
    print(f"Downloading {name} from {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"[OK] {name}")
    except Exception as e:
        print(f"[ERROR] Failed to download {name}: {e}")

print("Sound download complete.")
