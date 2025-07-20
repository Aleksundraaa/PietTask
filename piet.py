from PIL import Image
from piet_colors import piet_colors

def load_image(path):
    image = Image.open(path).convert('RGB')
    pixels = image.load()
    width, height = image.size
    return pixels, width, height

def main():
    path = 'HelloWorld.png'
    pixels, width, height = load_image(path)

def get_piet_color(rgb):
    if rgb in piet_colors:
        return piet_colors[rgb]
    else:
        raise ValueError(f'Неизвестный цвет: {rgb}')


if __name__=="__main__":
    main()