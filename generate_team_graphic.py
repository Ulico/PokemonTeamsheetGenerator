from PIL import Image, ImageDraw, ImageFont
import csv
import pokepy

class Pokemon:
    def __init__(self, name, item, ability, level, tera_type, moves, gender=None):
        self.name = name
        self.item = item
        self.ability = ability
        self.level = level
        self.tera_type = tera_type
        self.moves = moves
        self.gender = gender

    def __repr__(self):
        return f"Pokemon(name={self.name}, item={self.item}, ability={self.ability}, level={self.level}, tera_type={self.tera_type}, moves={self.moves}, gender={self.gender})"

def parse_team_file(file_path):
    team = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        if lines[i].strip():
            try:
                # Parse name and item
                name_item_line = lines[i].strip()
                item = None
                gender = None
                if ' @ ' in name_item_line:
                    name, item = name_item_line.split(' @ ')
                    name = name.strip()
                    item = item.strip()

                    # Check if name includes a nickname or gender
                    if '(' in name and ')' in name:
                        parts = name.split('(')
                        # print(parts)
                        parts = [part.strip().strip(')') for part in parts]

                        if parts[-1] in ['M', 'F']:
                            name = parts[-2]
                            gender = parts[-1]
                        else:
                            name = parts[-1]
                else:
                    name = name_item_line.strip()

                # Initialize default values
                ability = 'None'
                level = 100  # Default to level 100 if not found
                tera_type = 'None'
                moves = []

                # Parse subsequent lines
                j = i + 1
                while j < len(lines) and lines[j].strip():
                    line = lines[j].strip()
                    if line.startswith('Ability: '):
                        ability = line.split(': ')[1]
                    elif line.startswith('Level: '):
                        level = int(line.split(': ')[1])
                    elif line.startswith('Tera Type: '):
                        tera_type = line.split(': ')[1]
                    elif line.startswith('- '):
                        moves.append(line[2:].strip())
                    j += 1

                # Create a Pokemon object with the necessary information
                team.append(Pokemon(name=name, item=item, ability=ability, level=level, tera_type=tera_type, moves=moves, gender=gender))

                # Move to the next Pokémon entry
                i = j
            except (IndexError, ValueError):
                # Skip malformed entries
                i += 1
        else:
            i += 1

    return team

def fetch_item_id(item_name):
    """Fetch the ID of a given Pokémon item using the items.csv file."""
    csv_file = "assets/data/items.csv"
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Item Name'].strip().lower() == item_name.strip().lower():
                    return f"{int(row['Item Number']):04d}"  # Format the ID as a 4-digit string
    except Exception as e:
        print(f"Error reading items.csv: {e}")
    return None

def get_pokedex_data(pokemon_name):
    """Fetch the Pokédex number and types for a given Pokémon name using pokemon.csv."""
    csv_file = "assets/data/pokemon.csv"
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Name'].strip().lower() == pokemon_name.strip().lower():
                    pokedex_number = row['Number'].strip()  # Ensure '#' is parsed correctly
                    type_1 = row['Type 1'].strip()
                    type_2 = row['Type 2'].strip() if row['Type 2'].strip() else None
                    return pokedex_number, [type_1, type_2] if type_2 else [type_1]
    except KeyError as e:
        print(f"KeyError: Missing column in pokemon.csv: {e}")
    except ValueError as e:
        print(f"ValueError: Invalid data in pokemon.csv: {e}")
    except Exception as e:
        print(f"Error reading pokemon.csv: {e}")
    return None, []

def get_sprite_path(pokedex_number):
    # print(f"Fetching sprite for Pokedex number: {pokedex_number}")
    if "_" in pokedex_number:
        base_number, suffix = pokedex_number.split("_")
        return f"assets/sprites/{base_number.zfill(4)}_{suffix}.png"
    else:
        return f"assets/sprites/{pokedex_number.zfill(4)}.png"

def create_pokemon_graphic(pokemon, image, scale=0.85):
    """Draw Pokémon information directly onto the provided image object, scaled by the given factor."""
    draw = ImageDraw.Draw(image)

    # Retrieve dimensions from the provided image object
    width, height = image.size

    # Load fonts with increased scaling
    font_bold = ImageFont.truetype("assets/fonts/Roboto-Bold.ttf", int(28 * scale))  # Increased size
    font_medium = ImageFont.truetype("assets/fonts/Roboto-Medium.ttf", int(24 * scale))  # Increased size


    # Fetch Pokémon data to get the Pokédex number and types
    pokedex_number, types = get_pokedex_data(pokemon.name)

    print(f"Pokédex number: {pokedex_number}, Types: {types}")

    if "_" in pokedex_number:
        pokemon.name = pokemon.name.split("-")[0]

    # Draw Pokémon name
    draw.text((int(30 * scale), int(20 * scale)), pokemon.name, font=font_bold, fill="white")

    # Draw level
    draw.text((int(30 * scale), int(65 * scale)), f"Lv. {pokemon.level}", font=font_medium, fill="white")

    # Draw gender icon if available
    if pokemon.gender:
        gender_icon_path = f"assets/icons/genders/{'male' if pokemon.gender == 'M' else 'female'}.png"
        try:
            gender_icon = Image.open(gender_icon_path).resize((int(23 * scale), int(23 * scale)))  # Slightly bigger size
            image.paste(gender_icon, (int(108 * scale), int(68 * scale)), gender_icon)  # Closer to level text and shifted down
        except FileNotFoundError:
            print(f"Gender icon not found: {gender_icon_path}")
        except Exception as e:
            print(f"Error processing gender icon: {e}")

    # Draw ability
    draw.text((int(30 * scale), int(100 * scale)), pokemon.ability, font=font_medium, fill="white")

    # Draw item icon and name
    item_id = fetch_item_id(pokemon.item)
    if item_id is None:
        print(f"Could not fetch ID for item: {pokemon.item}")
        item_id = "0000"
        return

    item_icon_path = f"assets/icons/items/item_{item_id}.png"
    try:
        item_icon = Image.open(item_icon_path).resize((int(40 * scale), int(40 * scale)))
        
    except FileNotFoundError:
        print(f"Item icon not found: {item_icon_path}")
        item_icon = Image.open('assets/icons/items/item_0000.png').resize((int(40 * scale), int(40 * scale)))
    image.paste(item_icon, (int(30 * scale), int(140 * scale)), item_icon)
    draw.text((int(80 * scale), int(150 * scale)), pokemon.item, font=font_medium, fill="white")

    

    # Adjust Pokémon sprite size and position to align the bottom with the item text
    if pokedex_number:
        sprite_path = get_sprite_path(str(pokedex_number))
        try:
            sprite = Image.open(sprite_path).resize((int(130 * scale), int(130 * scale)))
            image.paste(sprite, (int(240 * scale), int(52 * scale)), sprite)
        except FileNotFoundError:
            print(f"Sprite not found: {sprite_path}")
        except Exception as e:
            print(f"Error processing sprite: {e}")

    # Shift type icons further upwards to align with the sprite
    type_icon_size = (int(30 * scale), int(30 * scale))
    x_offset = int(280 * scale)
    y_offset = int(20 * scale)

    for type_name in types:
        type_icon_path = f"assets/icons/types/{type_name.lower()}.png"
        try:
            # Load the PNG type icon
            type_icon = Image.open(type_icon_path).resize(type_icon_size)

            # Paste the type icon onto the image
            image.paste(type_icon, (x_offset, y_offset), type_icon)
            x_offset += int(40 * scale)
        except FileNotFoundError:
            print(f"Type icon not found: {type_icon_path}")
        except Exception as e:
            print(f"Error processing type icon for {type_name}: {e}")

    # Update the placeholder for a single type to make none.png 50% opaque
    if len(types) == 1:
        none_icon_path = "assets/icons/types/none.png"
        try:
            none_icon = Image.open(none_icon_path).convert("RGBA").resize(type_icon_size)
            # Adjust opacity to 50%
            none_icon = Image.eval(none_icon, lambda p: p // 2 if p > 0 else p)
            image.paste(none_icon, (x_offset, y_offset), none_icon.split()[3])  # Use the alpha channel as the mask
            x_offset += int(40 * scale)
        except FileNotFoundError:
            print(f"None type icon not found: {none_icon_path}")
        except Exception as e:
            print(f"Error processing None type icon: {e}")

    # Draw a small vertical line separating the Tera type icon from the other type icons
    draw.line([(x_offset, y_offset), (x_offset, y_offset + int(30 * scale))], fill="gray", width=1)

    # Position the Tera type icon directly to the right of the other type icons
    tera_icon_size = (int(50 * scale), int(50 * scale))
    tera_icon_path = f"assets/icons/tera_types/{pokemon.tera_type.lower()}.png"
    try:
        tera_icon = Image.open(tera_icon_path).resize((tera_icon_size[0], tera_icon_size[1]))

        if pokemon.tera_type.lower() == "none":
            # Adjust opacity to 50% for none.png
            tera_icon = Image.eval(tera_icon, lambda p: p // 2 if p > 0 else p)

        tera_x_offset = x_offset
        tera_y_offset = y_offset - (tera_icon_size[1] - type_icon_size[1]) // 2
        image.paste(tera_icon, (tera_x_offset, int(tera_y_offset)), tera_icon.split()[3])
        x_offset += int(50 * scale)
    except FileNotFoundError:
        print(f"Tera type icon not found: {tera_icon_path}")
    except Exception as e:
        print(f"Error processing Tera type icon: {e}")

    # Draw the large vertical line to the right of the Tera type icon
    draw.line([(x_offset, 17), (x_offset, height-17)], fill="white", width=1)

    # Fetch move types using pokepy
    move_types = []
    client = pokepy.V2Client()
    try:
        for move in pokemon.moves:
            formatted_move = move.lower().replace(' ', '-')
            move_data = client.get_move(formatted_move)[0]
            move_types.append((move, move_data.type.name))
    except Exception as e:
        print(f"Error fetching move types: {e}")

    # Adjust moves to be closer to the main vertical line
    move_icon_size = (int(30 * scale), int(30 * scale))
    x_offset = x_offset + int(20 * scale)
    y_offset = (height - (4 * int(40 * scale))) // 2  # Ensure space for 4 moves

    for move, move_type in move_types:
        type_icon_path = f"assets/icons/types/{move_type.lower()}.png"
        try:
            # Load the PNG type icon
            type_icon = Image.open(type_icon_path).resize(move_icon_size)

            # Paste the type icon onto the image
            image.paste(type_icon, (x_offset, y_offset), type_icon)

            # Draw the move name next to the icon
            draw.text((x_offset + int(40 * scale), y_offset), move, font=font_medium, fill="white")

            y_offset += int(43 * scale)
        except FileNotFoundError:
            print(f"Type icon not found: {type_icon_path}")
        except Exception as e:
            print(f"Error processing type icon for {move_type}: {e}")

    # Add grey circles for missing moves
    none_icon_path = "assets/icons/types/none.png"
    for _ in range(4 - len(move_types)):
        try:
            none_icon = Image.open(none_icon_path).convert("RGBA").resize(move_icon_size)
            # Adjust opacity to 50%
            none_icon = Image.eval(none_icon, lambda p: p // 2 if p > 0 else p)
            image.paste(none_icon, (x_offset, y_offset), none_icon.split()[3])
            y_offset += int(43 * scale)
        except FileNotFoundError:
            print(f"None type icon not found: {none_icon_path}")
        except Exception as e:
            print(f"Error processing None type icon: {e}")

def create_teamsheet(team, output_path):
    """Create a full teamsheet with 6 Pokémon boxes arranged in a 3x2 table."""
    # Load the background image
    background = Image.open("assets/images/battle.JPG")
    
    # Modify the final teamsheet to be twice as large
    sheet_width, sheet_height = background.size
    sheet_width *= 2
    sheet_height *= 2

    # Create a blank image for the teamsheet with the new dimensions
    teamsheet = Image.new("RGBA", (sheet_width, sheet_height))  # Solid black background
    background = background.resize((sheet_width, sheet_height))  # Resize the background
    teamsheet.paste(background, (0, 0))  # Add the resized background image

    # Calculate the grid layout dynamically based on the background dimensions
    box_width, box_height = int(1000 * 1.2), int(280 * 1.2)  # Adjusted dimensions for the boxes
    horizontal_spacing = 60
    vertical_spacing = 60
    grid_width = box_width * 2 + horizontal_spacing
    grid_height = box_height * 3 + vertical_spacing * 2
    x_offset_start = (sheet_width - grid_width) // 2
    y_offset_start = (sheet_height - grid_height) // 2

    # Add Pokémon boxes directly onto the teamsheet
    for i, pokemon in enumerate(team):
        # Calculate the position in the 3x2 grid with added spacing and margins
        x_offset = x_offset_start + (i % 2) * (box_width + horizontal_spacing)
        y_offset = y_offset_start + (i // 2) * (box_height + vertical_spacing)

        # Create a blank box for the Pokémon with a semi-transparent tint
        box = Image.new("RGBA", (box_width, box_height))  # Semi-transparent black tint

        # Create a mask for rounded corners with a smaller radius
        mask = Image.new("L", (box_width, box_height), 0)
        draw_mask = ImageDraw.Draw(mask)
        corner_radius = int(box_height * 0.1)  # Reduced corner radius
        draw_mask.rounded_rectangle(
            [(0, 0), (box_width, box_height)],
            radius=corner_radius,
            fill=130  # Fully white for the mask
        )

        # Apply the mask to the box to create rounded corners
        box.putalpha(mask)

        scale=1.7

        # Draw Pokémon information directly onto the box
        create_pokemon_graphic(pokemon, box, scale=scale)  # Slightly increase the contents' size

        # Create a draw object for the box
        box_draw = ImageDraw.Draw(box)

        # Add a number to the bottom right corner of the box
        number_font = ImageFont.truetype("assets/fonts/Roboto-ExtraBoldItalic.ttf", int(60 * scale))  # Slightly larger font size
        number_text = str(i + 1)  # Box number starts from 1
        text_bbox = number_font.getbbox(number_text)  # Use getbbox to calculate text dimensions
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        width_padding = int(15 * scale)  # Smaller padding for width
        height_padding = int(30 * scale)  # Keep the height padding the same
        number_x = box_width - text_width - width_padding  # Padding from the right
        number_y = box_height - text_height - height_padding  # Padding from the bottom

        # Apply even fainter semi-transparent white color for the number
        faint_white = (0, 0, 0, 100)  # RGBA with more transparency

        # Draw the number with the specified style
        box_draw.text((number_x, number_y), number_text, font=number_font, fill=faint_white)

        # Paste the Pokémon box onto the teamsheet
        teamsheet.paste(box, (x_offset, y_offset), box)

    # Save the final teamsheet
    teamsheet.save(output_path)

# Example usage
if __name__ == "__main__":
    team_file_path = "team_paste.txt"
    team = parse_team_file(team_file_path)
    if team:
        create_teamsheet(team, "teamsheet.png")