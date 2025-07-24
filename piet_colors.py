piet_colors_list = {
    # Красный
    (255, 192, 192): (0, 0),
    (255, 0, 0):     (0, 1),
    (192, 0, 0):     (0, 2),

    # Жёлтый
    (255, 255, 192): (1, 0),
    (255, 255, 0):   (1, 1),
    (192, 192, 0):   (1, 2),

    # Зелёный
    (192, 255, 192): (2, 0),
    (0, 255, 0):     (2, 1),
    (0, 192, 0):     (2, 2),

    # Голубой
    (192, 255, 255): (3, 0),
    (0, 255, 255):   (3, 1),
    (0, 192, 192):   (3, 2),

    # Синий
    (192, 192, 255): (4, 0),
    (0, 0, 255):     (4, 1),
    (0, 0, 192):     (4, 2),

    # Фиолетовый
    (255, 192, 255): (5, 0),
    (255, 0, 255):   (5, 1),
    (192, 0, 192):   (5, 2),

    (0, 0, 0):       "black",
    (255, 255, 255): "white"
}

commands_list = [
    ["noop",     "push",     "pop"],
    ["add",      "subtract", "multiply"],
    ["divide",   "mod",      "not"],
    ["greater",  "pointer",  "switch"],
    ["duplicate","roll",     "in_number"],
    ["in_char",  "out_number","out_char"]
]

def get_color_by_number(hex_color):
    if hex_color.startswith('#'):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        return piet_colors_list.get((r, g, b), None)
    return None

def get_command(hue_change, lightness_change):
    return commands_list[hue_change % 6][lightness_change % 3]
