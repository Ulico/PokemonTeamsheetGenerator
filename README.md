# Pokémon Teamsheet Graphic Generator
This tool generates a visually appealing teamsheet graphic for Pokémon teams based on Scarlet Violet designs. A live hosted version can be found [here](https://ulico-pokemonteamsheetgenerator-app-ukjjki.streamlit.app/).

**Warning:** This tool is designed for Gen 9 Pokémon teams. While older teams may work correctly, certain issues may arise.

## Features
- **Dynamic Layout**: Automatically adjusts to fit all Pokémon boxes within the background dimensions.
- **Customizable Graphics**: Includes semi-transparent black backgrounds, rounded corners, and stylized text.
- **Move and Type Icons**: Displays move types and Pokémon types with appropriate icons.
- **Placeholder Icons**: Adds grey circles for missing moves or single-type Pokémon.

## Prerequisites
- Python 3.8+
- Required Python libraries:
  Install dependencies using:
```bash
pip install -r requirements.txt
```

## File Structure
```
assets/
  data/
    items.csv          # Pokémon item data
    pokemon.csv        # Pokémon data
  fonts/               # Font files for text rendering
  icons/               
    genders/           # Gender icons (male, female)
    items/             # Item icons
    tera_types/        # Tera type icons
    types/             # Type icons
  images/              # Background images
  moves/               # Move icons
  sprites/             # Pokémon sprites
  
generate_team_graphic.py  # Main script for generating the teamsheet
```

## Usage
1. **Prepare Input**:
   - Create a `team_paste.txt` file with your Pokémon team data in the following format:
     ```
     Pikachu (F) @ Light Ball
     Ability: Static
     Level: 50
     Tera Type: Electric
     - Thunderbolt
     - Quick Attack
     - Iron Tail
     - Protect
     ```

2. **Run the Script**:
   Execute the script to generate the teamsheet:
   ```bash
   python generate_team_graphic.py
   ```

3. **Output**:
   - The generated teamsheet will be saved as `teamsheet.png` in the project directory.

## Customization
- **Background Image**: Replace `assets/images/battle.jpg` with your own background image.
- **Fonts**: Update font files in the `assets/fonts/` directory.
- **Icons**: Add or replace icons in the respective folders under `assets/`.

## Contributing
Feel free to fork this repository and submit pull requests for new features or bug fixes.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Sources
This project utilizes assets and inspiration from the following sources:

- [Pokémon Type Icons by rwaltenberg](https://github.com/rwaltenberg/pokemon-type-icons)
- [Project Pokémon Sprite Index](https://projectpokemon.org/home/docs/spriteindex_148)
- [The Spriters Resource - Pokémon Scarlet and Violet](https://www.spriters-resource.com/nintendo_switch/pokemonscarletviolet/sheet/187089/)
- [Pokémon Tera Type Symbols by JormxDos](https://www.deviantart.com/jormxdos/gallery/85377027/pokemon-tera-type-symbols-paldea)
