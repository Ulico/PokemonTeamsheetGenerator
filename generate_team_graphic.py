from PIL import Image, ImageDraw, ImageFont, ImageChops
import csv
import math
import pokepy

# "champions" = Pokemon Champions style (default)
# "sv"        = Pokemon Scarlet/Violet style
MODE = "champions"

# Champions mode palette
_CHAMP_BG_BASE    = (253, 244, 200)
_CHAMP_BG_DIAMOND = (236, 224, 168)
_CHAMP_BOX_COLOR    = (128, 108, 192, 240)

def _make_corner_mask(w, h, tl, tr, br, bl, fill):
    """Rounded rectangle mask with independent per-corner radii."""
    img = Image.new("L", (w, h), fill)
    d = ImageDraw.Draw(img)
    d.rectangle([(0, 0), (tl, tl)], fill=0)
    if tl: d.ellipse([(0, 0), (tl*2-1, tl*2-1)], fill=fill)
    d.rectangle([(w-tr, 0), (w, tr)], fill=0)
    if tr: d.ellipse([(w-tr*2, 0), (w-1, tr*2-1)], fill=fill)
    d.rectangle([(w-br, h-br), (w, h)], fill=0)
    if br: d.ellipse([(w-br*2, h-br*2), (w-1, h-1)], fill=fill)
    d.rectangle([(0, h-bl), (bl, h)], fill=0)
    if bl: d.ellipse([(0, h-bl*2), (bl*2-1, h-1)], fill=fill)
    return img


def _add_dark_outline(img, color=(0, 0, 0), width=1):
    """Add a dark outline around item sprites only if one isn't already present."""
    import numpy as np
    from PIL import ImageFilter
    img = img.convert("RGBA")
    alpha_ch = img.split()[3]
    arr = np.array(img, dtype=np.uint8)
    a = arr[..., 3]
    # Edge pixels: opaque but adjacent to transparency (eroded alpha goes transparent)
    eroded = np.array(alpha_ch.filter(ImageFilter.MinFilter(size=width * 2 + 1)))
    edge_mask = (a > 128) & (eroded < 128)
    if edge_mask.any():
        edge_brightness = arr[edge_mask, :3].max(axis=1).mean()
        if edge_brightness < 60:   # already has a dark outline
            return img
    dilated = np.array(alpha_ch.filter(ImageFilter.MaxFilter(size=width * 2 + 1)))
    outline = (dilated > 128) & (a < 128)
    arr[outline] = [color[0], color[1], color[2], 255]
    return Image.fromarray(arr)


def _round_corners(img, radius):
    """Return a copy of img with rounded corners."""
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (img.width - 1, img.height - 1)],
                                            radius=radius, fill=255)
    img.putalpha(mask)
    return img


def _create_champions_background(width, height):
    img = Image.new("RGBA", (width, height), _CHAMP_BG_BASE + (255,))
    draw = ImageDraw.Draw(img)

    # Subtle diagonal diamond grid
    step = max(width, height) // 22
    for x in range(-height, width + height, step):
        draw.line([(x, 0), (x + height, height)], fill=_CHAMP_BG_DIAMOND + (255,), width=1)
        draw.line([(x, 0), (x - height, height)], fill=_CHAMP_BG_DIAMOND + (255,), width=1)

    # Bottom-right layered triangles (large, prominent)
    for size, alpha in [(900, 30), (680, 24), (500, 18), (340, 13), (210, 9)]:
        draw.polygon(
            [(width, height), (width - size, height), (width, height - size)],
            fill=_CHAMP_BG_DIAMOND + (alpha,)
        )

    # Bottom-left triangles
    for size, alpha in [(500, 20), (360, 14), (240, 9)]:
        draw.polygon(
            [(0, height), (size, height), (0, height - size)],
            fill=_CHAMP_BG_DIAMOND + (alpha,)
        )

    # Top-right subtle accent
    for size, alpha in [(300, 12), (180, 7)]:
        draw.polygon(
            [(width, 0), (width - size, 0), (width, size)],
            fill=_CHAMP_BG_DIAMOND + (alpha,)
        )

    return img


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
                name_item_line = lines[i].strip()
                item = None
                gender = None
                if ' @ ' in name_item_line:
                    name, item = name_item_line.split(' @ ')
                    name = name.strip()
                    item = item.strip()
                else:
                    name = name_item_line.strip()

                if '(' in name and ')' in name:
                    parts = name.split('(')
                    parts = [part.strip().strip(')') for part in parts]
                    if parts[-1] in ['M', 'F']:
                        name = parts[-2]
                        gender = parts[-1]
                    else:
                        name = parts[-1]

                ability = 'None'
                level = 100
                tera_type = 'None'
                moves = []

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

                team.append(Pokemon(name=name, item=item, ability=ability, level=level,
                                    tera_type=tera_type, moves=moves, gender=gender))
                i = j
            except (IndexError, ValueError):
                i += 1
        else:
            i += 1

    return team


def fetch_item_id(item_name):
    csv_file = "assets/data/items.csv"
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Item Name'].strip().lower() == item_name.strip().lower():
                    return f"{int(row['Item Number']):04d}"
    except Exception as e:
        print(f"Error reading items.csv: {e}")
    return None


def get_pokedex_data(pokemon_name, gender=None):
    csv_file = "assets/data/pokemon.csv"
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if gender:
                gender_suffix = '-M' if gender == 'M' else '-F'
                for row in reader:
                    if row['Name'].strip().lower() == f"{pokemon_name.strip().lower()}{gender_suffix.lower()}":
                        type_1 = row['Type 1'].strip()
                        type_2 = row['Type 2'].strip() if row['Type 2'].strip() else None
                        return row['Number'].strip(), [type_1, type_2] if type_2 else [type_1]
                file.seek(0)
                next(reader)
            for row in reader:
                if row['Name'].strip().lower() == pokemon_name.strip().lower():
                    type_1 = row['Type 1'].strip()
                    type_2 = row['Type 2'].strip() if row['Type 2'].strip() else None
                    return row['Number'].strip(), [type_1, type_2] if type_2 else [type_1]
    except KeyError as e:
        print(f"KeyError: Missing column in pokemon.csv: {e}")
    except Exception as e:
        print(f"Error reading pokemon.csv: {e}")
    return None, []


def get_sprite_path(pokedex_number):
    if "_" in pokedex_number:
        base_number, suffix = pokedex_number.split("_")
        return f"assets/sprites/{base_number.zfill(4)}_{suffix}.png"
    return f"assets/sprites/{pokedex_number.zfill(4)}.png"


def _draw_champions_layout(pokemon, image, draw, scale, types, move_types,
                            font_bold, font_medium, sprite_image, height):
    s = scale
    # Header takes ~1/4 of box height; three equal lower rows share the rest
    header_h  = int(height * 0.27)
    lower_h   = (height - header_h) // 3
    content_x = int(90 * s)             # close to sprite right edge
    divider_x    = int(415 * s)
    icon_sz      = int(30 * s)
    icon_t       = (icon_sz, icon_sz)
    icon_corner_r = max(int(icon_sz * 0.2), 2)

    move_icon_sz     = int(38 * s) - 4
    move_icon_t      = (move_icon_sz, move_icon_sz)
    move_icon_corner = max(int(move_icon_sz * 0.25), 3)
    move_text_oy     = (move_icon_sz - int(27 * s)) // 2   # vertically centred with icon

    def row_center(i):
        """Vertical centre of row i (0=header, 1-3=lower rows)."""
        if i == 0:
            return header_h // 2
        return header_h + (i - 1) * lower_h + lower_h // 2

    # ── Row 0 (darker full-width header): name + gender + types ──────────────
    rc0 = row_center(0)
    name_y = rc0 - int(font_bold.size) // 2 + int(6 * s) + 2
    draw.text((content_x - 2, name_y), pokemon.name, font=font_bold, fill="white")

    # Right-align gender + type icons near right edge of dark band
    icon_gap  = int(9 * s)
    g_sz      = int(30 * s)
    gender_w  = (g_sz + icon_gap) if pokemon.gender else 0
    total_icons_w = 2 * (icon_sz + icon_gap) - icon_gap + gender_w  # always reserve 2 slots
    type_x    = divider_x - int(28 * s) - total_icons_w - 5
    type_y    = rc0 - icon_sz // 2

    if pokemon.gender:
        try:
            g_name = 'male' if pokemon.gender == 'M' else 'female'
            g_icon = Image.open(f"assets/icons/gender_champions/{g_name}.png").resize((g_sz, g_sz))
            image.paste(g_icon, (type_x, rc0 - g_sz // 2), g_icon)
            type_x += g_sz + icon_gap
        except Exception:
            pass
    for type_name in types:
        try:
            icon = Image.open(f"assets/icons/types_champions/{type_name.lower()}.png").resize(icon_t)
            icon = _round_corners(icon, icon_corner_r)
            image.paste(icon, (type_x, type_y), icon)
            type_x += icon_sz + icon_gap
        except Exception:
            pass

    # ── Row 1: ability ───────────────────────────────────────────────────────
    rc1 = row_center(1)
    info_x = content_x + int(10 * s)
    try:
        font_ability = ImageFont.truetype("assets/fonts/AbadMTProCondensed.ttf", int(27 * s) + 5)
    except Exception:
        font_ability = font_medium
    draw.text((info_x, rc1 - (int(27 * s) + 1) // 2 + 5), pokemon.ability, font=font_ability, fill="white")

    # ── Row 2: item ──────────────────────────────────────────────────────────
    item_id = fetch_item_id(pokemon.item)
    if item_id is None:
        print(f"Could not fetch ID for item: {pokemon.item}")
        item_id = "0000"
        pokemon.item = "None"
    rc2 = row_center(2)
    item_icon_sz = int(44 * s)
    item_y = rc2 - item_icon_sz // 2
    item_icon_x = content_x - item_icon_sz - int(6 * s)
    item_text_oy = (item_icon_sz - int(24 * s)) // 2
    try:
        item_icon = Image.open(f"assets/icons/items/item_{item_id}.png").resize((item_icon_sz, item_icon_sz))
    except FileNotFoundError:
        item_icon = Image.open("assets/icons/items/item_0000.png").resize((item_icon_sz, item_icon_sz))
    item_icon = _add_dark_outline(item_icon)
    image.paste(item_icon, (item_icon_x, item_y), item_icon)
    draw.text((info_x, item_y + item_text_oy + 3), pokemon.item, font=font_ability, fill="white")

    # ── Moves: evenly spaced, centered in box height ─────────────────────────
    mx = divider_x + int(14 * s)
    move_slot_h = int(height * 0.235)
    moves_top = (height - 4 * move_slot_h) // 2
    try:
        font_moves = ImageFont.truetype("assets/fonts/AbadMTProCondensed.ttf", int(27 * s))
    except Exception:
        font_moves = ImageFont.truetype("assets/fonts/Roboto-Medium.ttf", int(27 * s))
    for i, (move, move_type) in enumerate(move_types):
        my = moves_top + i * move_slot_h + (move_slot_h - move_icon_sz) // 2
        try:
            icon = Image.open(f"assets/icons/types_champions/{move_type.lower()}.png").resize(move_icon_t)
            icon = _round_corners(icon, move_icon_corner)
            image.paste(icon, (mx, my), icon)
            draw.text((mx + move_icon_sz + int(12 * s), my + move_text_oy + 4), move, font=font_moves, fill="white")
        except Exception:
            pass

    return sprite_image


def _draw_sv_layout(pokemon, image, draw, scale, types, move_types,
                    font_bold, font_medium, sprite_image, height):
    s = scale

    draw.text((int(30 * s), int(20 * s)), pokemon.name, font=font_bold, fill="white")
    draw.text((int(30 * s), int(65 * s)), f"Lv. {pokemon.level}", font=font_medium, fill="white")

    if pokemon.gender:
        g_name = 'male' if pokemon.gender == 'M' else 'female'
        try:
            g_icon = Image.open(f"assets/icons/genders/{g_name}.png").resize((int(23 * s), int(23 * s)))
            image.paste(g_icon, (int(108 * s), int(68 * s)), g_icon)
        except Exception as e:
            print(f"Gender icon error: {e}")

    draw.text((int(30 * s), int(100 * s)), pokemon.ability, font=font_medium, fill="white")

    item_id = fetch_item_id(pokemon.item)
    if item_id is None:
        print(f"Could not fetch ID for item: {pokemon.item}")
        item_id = "0000"
        pokemon.item = "None"
    try:
        item_icon = Image.open(f"assets/icons/items/item_{item_id}.png").resize((int(40 * s), int(40 * s)))
    except FileNotFoundError:
        item_icon = Image.open("assets/icons/items/item_0000.png").resize((int(40 * s), int(40 * s)))
    image.paste(item_icon, (int(30 * s), int(140 * s)), item_icon)
    draw.text((int(80 * s), int(150 * s)), pokemon.item, font=font_medium, fill="white")

    if sprite_image:
        try:
            sprite = sprite_image.resize((int(130 * s), int(130 * s)))
            image.paste(sprite, (int(240 * s), int(52 * s)), sprite)
        except Exception as e:
            print(f"Sprite error: {e}")

    type_icon_size = (int(30 * s), int(30 * s))
    x_offset = int(280 * s)
    y_offset = int(20 * s)
    for type_name in types:
        try:
            icon = Image.open(f"assets/icons/types/{type_name.lower()}.png").resize(type_icon_size)
            image.paste(icon, (x_offset, y_offset), icon)
            x_offset += int(40 * s)
        except Exception as e:
            print(f"Type icon error: {e}")
    if len(types) == 1:
        try:
            none = Image.open("assets/icons/types/none.png").convert("RGBA").resize(type_icon_size)
            none = Image.eval(none, lambda p: p // 2 if p > 0 else p)
            image.paste(none, (x_offset, y_offset), none.split()[3])
            x_offset += int(40 * s)
        except Exception as e:
            print(f"None type icon error: {e}")

    # Tera icon
    draw.line([(x_offset, y_offset), (x_offset, y_offset + int(30 * s))], fill="gray", width=1)
    tera_icon_size = (int(36 * s), int(36 * s))
    tera_icon_path = f"assets/icons/tera_types/{pokemon.tera_type.lower()}.png"
    try:
        tera = Image.open(tera_icon_path).resize(tera_icon_size)
        if pokemon.tera_type.lower() == "none":
            tera = Image.eval(tera, lambda p: p // 2 if p > 0 else p)
        tera_x = x_offset + int(8 * s)
        tera_y = y_offset - (tera_icon_size[1] - type_icon_size[1]) // 2
        image.paste(tera, (tera_x, int(tera_y)), tera.split()[3])
        x_offset += int(50 * s)
    except FileNotFoundError:
        print(f"Tera icon not found: {tera_icon_path}")
    except Exception as e:
        print(f"Tera icon error: {e}")

    draw.line([(x_offset, int(12 * s)), (x_offset, height - int(12 * s))], fill="white", width=1)

    move_icon_size = (int(30 * s), int(30 * s))
    mx = x_offset + int(20 * s)
    my = (height - 4 * int(40 * s)) // 2
    for move, move_type in move_types:
        try:
            icon = Image.open(f"assets/icons/types/{move_type.lower()}.png").resize(move_icon_size)
            image.paste(icon, (mx, my), icon)
            draw.text((mx + int(40 * s), my), move, font=font_medium, fill="white")
            my += int(43 * s)
        except Exception as e:
            print(f"Move icon error: {e}")
    for _ in range(4 - len(move_types)):
        try:
            none = Image.open("assets/icons/types/none.png").convert("RGBA").resize(move_icon_size)
            none = Image.eval(none, lambda p: p // 2 if p > 0 else p)
            image.paste(none, (mx, my), none.split()[3])
            my += int(43 * s)
        except Exception as e:
            print(f"None move icon error: {e}")


def create_pokemon_graphic(pokemon, image, scale=0.85):
    """Draw Pokémon info onto the image. Returns the raw sprite Image in Champions mode."""
    draw = ImageDraw.Draw(image)
    _, height = image.size

    if MODE == "champions":
        try:
            font_bold   = ImageFont.truetype("assets/fonts/AbadMTProCondensed.ttf", int(38 * scale) + 2)
            font_medium = ImageFont.truetype("assets/fonts/AbadMTProCondensed.ttf",  int(26 * scale))
        except Exception:
            font_bold   = ImageFont.truetype("assets/fonts/Roboto-Bold.ttf",   int(30 * scale))
            font_medium = ImageFont.truetype("assets/fonts/Roboto-Medium.ttf", int(26 * scale))
    else:
        font_bold   = ImageFont.truetype("assets/fonts/Roboto-Bold.ttf",   int(30 * scale))
        font_medium = ImageFont.truetype("assets/fonts/Roboto-Medium.ttf", int(24 * scale))

    print(pokemon.name)
    pokedex_number, types = get_pokedex_data(pokemon.name, pokemon.gender)
    print(f"Pokédex number: {pokedex_number}, Types: {types}")

    if pokedex_number and "_" in pokedex_number:
        pokemon.name = pokemon.name.split("-")[0]

    # Load sprite image (rendering handled per-mode)
    sprite_image = None
    if pokedex_number:
        try:
            sprite_image = Image.open(get_sprite_path(str(pokedex_number)))
        except Exception as e:
            print(f"Sprite load error: {e}")

    # Fetch move types
    move_types = []
    client = pokepy.V2Client()
    try:
        for move in pokemon.moves:
            move_slug = move.lower().replace(' ', '-').replace("'", "")
            move_data = client.get_move(move_slug)[0]
            move_types.append((move, move_data.type.name))
    except Exception as e:
        print(f"Error fetching move types: {e}")

    if MODE == "champions":
        return _draw_champions_layout(pokemon, image, draw, scale, types, move_types,
                                      font_bold, font_medium, sprite_image, height)
    else:
        _draw_sv_layout(pokemon, image, draw, scale, types, move_types,
                        font_bold, font_medium, sprite_image, height)
        return None


def create_teamsheet(team, output_path):
    if MODE == "champions":
        sheet_width, sheet_height = 2560, 1440
        background = _create_champions_background(sheet_width, sheet_height)
    else:
        background = Image.open("assets/images/battle.JPG")
        sheet_width, sheet_height = background.size
        sheet_width *= 2
        sheet_height *= 2
        background = background.resize((sheet_width, sheet_height))

    teamsheet = Image.new("RGBA", (sheet_width, sheet_height))
    teamsheet.paste(background, (0, 0))

    box_width, box_height = int(1000 * 1.2), int(280 * 1.2)
    horizontal_spacing = 60
    vertical_spacing   = 60
    grid_width  = box_width * 2 + horizontal_spacing
    grid_height = box_height * 3 + vertical_spacing * 2
    x_offset_start = (sheet_width  - grid_width)  // 2
    y_offset_start = (sheet_height - grid_height) // 2

    scale = 1.7
    sprite_size = 130               # px; feet align with bottom of header band

    for i, pokemon in enumerate(team):
        bx = x_offset_start + (i % 2) * (box_width  + horizontal_spacing)
        by = y_offset_start + (i // 2) * (box_height + vertical_spacing)

        corner_radius = int(box_height * 0.12)

        # Box fill
        if MODE == "champions":
            mask_fill = _CHAMP_BOX_COLOR[3]
            box = Image.new("RGBA", (box_width, box_height), (0, 0, 0, 0))
            import numpy as np
            _box_edge = np.array([165, 148, 232], dtype=float)
            _box_mid  = np.array([132, 115, 206], dtype=float)
            _ty = np.linspace(0, 1, box_height)
            _tx = np.linspace(0, 1, box_width)
            _t2y = (1.0 - np.abs(_ty * 2 - 1.0)) ** 0.5
            _t2x = (1.0 - np.abs(_tx * 2 - 1.0)) ** 0.5
            _t2  = (_t2y[:, np.newaxis] * _t2x[np.newaxis, :]) ** 0.4  # dark centre, light all edges
            _arr = np.zeros((box_height, box_width, 4), dtype=np.uint8)
            for _c in range(3):
                _arr[:, :, _c] = np.clip(_box_edge[_c] + (_box_mid[_c] - _box_edge[_c]) * _t2, 0, 255).astype(np.uint8)
            _arr[:, :, 3] = mask_fill
            box = Image.fromarray(_arr, 'RGBA')
        else:
            box = Image.new("RGBA", (box_width, box_height))
            mask_fill = 130

        large_r = corner_radius
        small_r = max(int(box_height * 0.025), 4)
        mask = _make_corner_mask(box_width, box_height,
                                  tl=large_r, tr=small_r,
                                  br=large_r, bl=small_r,
                                  fill=mask_fill)
        box.putalpha(mask)

        # Darker header band with vertical gradient
        if MODE == "champions":
            header_h = int(box_height * 0.27)
            divider_x = int(400 * scale) + 2
            panel_draw = ImageDraw.Draw(box)
            br_r = int(header_h * 0.9)
            band_top = (138, 128, 202)
            band_bot = (88, 76, 152)
            for _y in range(header_h):
                _t = (_y / max(header_h - 1, 1)) ** 0.5
                _r = int(band_top[0] + (band_bot[0] - band_top[0]) * _t)
                _g = int(band_top[1] + (band_bot[1] - band_top[1]) * _t)
                _b = int(band_top[2] + (band_bot[2] - band_top[2]) * _t)
                _row = (_r, _g, _b, mask_fill)
                if _y < header_h - br_r:
                    _x_max = divider_x
                else:
                    _dy = _y - (header_h - br_r)
                    _inner = br_r * br_r - _dy * _dy
                    _x_max = int(divider_x - br_r + math.sqrt(max(_inner, 0)))
                panel_draw.line([(0, _y), (_x_max, _y)], fill=_row)
            box.putalpha(mask)

            # Scan lines drawn after band — two colours depending on region
            scan_draw = ImageDraw.Draw(box)
            for y_line in range(0, box_height, 10):
                if y_line < header_h:
                    if y_line < header_h - br_r:
                        x_band = divider_x
                    else:
                        _dy2 = y_line - (header_h - br_r)
                        _inner2 = br_r * br_r - _dy2 * _dy2
                        x_band = int(divider_x - br_r + math.sqrt(max(_inner2, 0)))
                    scan_draw.line([(0, y_line), (x_band, y_line)], fill=(96, 83, 175, 18), width=1)
                    scan_draw.line([(x_band, y_line), (box_width, y_line)], fill=(129, 110, 187, 18), width=1)
                else:
                    scan_draw.line([(0, y_line), (box_width, y_line)], fill=(129, 110, 187, 18), width=1)
            box.putalpha(mask)


        box_draw = ImageDraw.Draw(box)

        # B: Box number
        number_font  = ImageFont.truetype("assets/fonts/Roboto-ExtraBoldItalic.ttf", int(80 * scale))
        number_text  = str(i + 1)
        tb = number_font.getbbox(number_text)
        tw, th = int(tb[2] - tb[0]), int(tb[3] - tb[1])
        if MODE == "champions":
            pad = int(20 * scale)
            num_img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
            ImageDraw.Draw(num_img).text((pad - tb[0], pad - tb[1]), number_text,
                                          font=number_font, fill=(235, 235, 235, 30))
            shear = 0.3
            nh = num_img.height
            extra = int(shear * nh)
            num_sheared = num_img.transform(
                (num_img.width + extra, nh), Image.Transform.AFFINE,
                (1, shear, -shear * nh, 0, 1, 0), resample=Image.Resampling.BICUBIC)
            nx = box_width  - num_sheared.width  - int(2 * scale)
            ny = box_height - num_sheared.height - int(2 * scale)
            box.paste(num_sheared, (nx, ny), num_sheared)
            box_draw = ImageDraw.Draw(box)
        else:
            nx = box_width  - tw - int(15 * scale)
            ny = box_height - th - int(30 * scale)
            box_draw.text((nx, ny), number_text, font=number_font, fill=(0, 0, 0, 100))

        # Draw Pokémon info; Champions mode returns sprite for overflow placement
        sprite_img = create_pokemon_graphic(pokemon, box, scale=scale)

        # Thick solid border matching per-corner shape
        if MODE == "champions":
            bw = 5
            outer_m = _make_corner_mask(box_width, box_height,
                                         tl=large_r, tr=small_r, br=large_r, bl=small_r, fill=255)
            inner_m = _make_corner_mask(box_width - bw * 2, box_height - bw * 2,
                                         tl=max(large_r - bw, 1), tr=max(small_r - bw, 1),
                                         br=max(large_r - bw, 1), bl=max(small_r - bw, 1),
                                         fill=255)
            padded = Image.new("L", (box_width, box_height), 0)
            padded.paste(inner_m, (bw, bw))
            border_mask = ImageChops.subtract(outer_m, padded)
            border_layer = Image.new("RGBA", (box_width, box_height), (210, 195, 250, 255))
            border_layer.putalpha(border_mask)
            box = Image.alpha_composite(box, border_layer)

        teamsheet.paste(box, (bx, by), box)

        # A: Sprite — paste on teamsheet, feet at bottom of header band
        if MODE == "champions" and sprite_img:
            header_h = int(box_height * 0.27)
            sprite = sprite_img.resize((sprite_size, sprite_size), Image.Resampling.LANCZOS)
            sprite_y = by + header_h - sprite_size
            teamsheet.paste(sprite, (bx + 8, sprite_y), sprite)

    rgb_teamsheet = teamsheet.convert("RGB")
    rgb_teamsheet.save(output_path)


if __name__ == "__main__":
    team_file_path = "team_paste.txt"
    team = parse_team_file(team_file_path)
    if team:
        create_teamsheet(team, "teamsheet.png")
