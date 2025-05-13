import os
import requests
from pathlib import Path

def download_mega_stones():
    """Download all Mega Stone images from the Pokesprite repository."""
    base_url = "https://raw.githubusercontent.com/msikma/pokesprite/master/items/mega-stone/"
    output_dir = Path("assets/items")
    
    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # List of Mega Stone image filenames (replace with actual filenames if known)
    mega_stones = [
        "abomasite.png", "absolite.png", "aerodactylite.png", "aggronite.png", "alakazite.png",
        "altarianite.png", "ampharosite.png", "audinite.png", "banettite.png", "beedrillite.png",
        "blastoisinite.png", "blazikenite.png", "cameruptite.png", "charizardite-x.png", "charizardite-y.png",
        "diancite.png", "galladite.png", "garchompite.png", "gardevoirite.png", "glalitite.png",
        "gyaradosite.png", "heracronite.png", "houndoominite.png", "kangaskhanite.png", "latiasite.png",
        "latiosite.png", "lopunnite.png", "lucarionite.png", "manectite.png", "mawilite.png",
        "medichamite.png", "metagrossite.png", "mewtwonite-x.png", "mewtwonite-y.png", "pidgeotite.png",
        "pinsirite.png", "sablenite.png", "salamencite.png", "sceptilite.png", "scizorite.png",
        "sharpedonite.png", "slowbronite.png", "steelixite.png", "swampertite.png", "tyranitarite.png",
        "venusaurite.png"
    ]

    for stone in mega_stones:
        url = base_url + stone
        output_path = output_dir / stone

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(output_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"Downloaded: {stone}")
        except requests.RequestException as e:
            print(f"Failed to download {stone}: {e}")

if __name__ == "__main__":
    download_mega_stones()
