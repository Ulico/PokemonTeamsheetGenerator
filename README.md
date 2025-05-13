# Pokémon Teamsheet Graphic Generator

This tool generates a visually appealing teamsheet graphic for Pokémon teams. It dynamically adjusts layouts, integrates background images, and includes detailed information about each Pokémon, such as moves, abilities, and types.

## Features
- **Dynamic Layout**: Automatically adjusts to fit all Pokémon boxes within the background dimensions.
- **Customizable Graphics**: Includes semi-transparent black backgrounds, rounded corners, and stylized text.
- **Move and Type Icons**: Displays move types and Pokémon types with appropriate icons.
- **Gender and Nickname Support**: Handles Pokémon with nicknames and genders.
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
  genders/             # Gender icons (male, female)
  images/              # Background images
  items/               # Item icons
  sprites/             # Pokémon sprites
  tera_types/          # Tera type icons
  types/               # Type icons
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
