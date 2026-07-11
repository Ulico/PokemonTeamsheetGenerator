# Pokémon Teamsheet Graphic Generator
This tool generates a visually appealing teamsheet graphic for Pokémon teams, styled after either **Pokémon Champions** or **Pokémon Scarlet/Violet**. A live hosted version can be found [here](https://ulico-pokemonteamsheetgenerator-app-ukjjki.streamlit.app/).

**Warning:** This tool is designed for Gen 9 Pokémon teams. While older teams may work correctly, certain issues may arise.

## Features
- **Two Styles**: Generate teamsheets in either the **Pokémon Champions** style (default) or the original **Pokémon Scarlet/Violet** style.
- **Dynamic Layout**: Automatically adjusts to fit all Pokémon boxes within the background dimensions.
- **Customizable Graphics**: Includes gradient panels, rounded corners, and stylized text, with a self-generated background in Champions mode and a battle-scene background in Scarlet/Violet mode.
- **Move and Type Icons**: Displays move types and Pokémon types with appropriate icons (style-specific icon sets for Champions and Scarlet/Violet).
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
  fonts/               # Font files for text rendering (incl. AbadMTProCondensed for Champions mode)
  icons/
    genders/           # Gender icons (male, female) - Scarlet/Violet style
    gender_champions/  # Gender icons - Pokémon Champions style
    items/             # Item icons
    tera_types/        # Tera type icons
    types/             # Type icons - Scarlet/Violet style
    types_champions/   # Type icons - Pokémon Champions style
  images/              # Background images (Scarlet/Violet mode)
  moves/               # Move icons
  sprites/             # Pokémon sprites

app.py                    # Streamlit web app front-end
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

2. **Choose a Style**:
   - The script defaults to the **Pokémon Champions** style. To generate a **Scarlet/Violet** style teamsheet instead, set `MODE = "sv"` at the top of `generate_team_graphic.py` (or, when using the Streamlit app, select "Pokémon Scarlet/Violet" from the style toggle).

3. **Run the Script**:
   Execute the script to generate the teamsheet:
   ```bash
   python generate_team_graphic.py
   ```

   Alternatively, run the Streamlit web app for an interactive UI with a style toggle:
   ```bash
   streamlit run app.py
   ```

4. **Output**:
   - The generated teamsheet will be saved as `teamsheet.png` in the project directory.

## Customization
- **Background Image**: In Scarlet/Violet mode, replace `assets/images/battle.jpg` with your own background image. Champions mode generates its background programmatically.
- **Fonts**: Update font files in the `assets/fonts/` directory.
- **Icons**: Add or replace icons in the respective folders under `assets/`, using the `_champions` variants for the Champions style.

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
