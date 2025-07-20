from PIL import Image

def load_image(path):
    image = Image.open(path).convert('RGB')
    pixels = image.load()
    width, height = image.size
    return pixels, width, height

def main():
    path = 'HelloWorld.png'
    pixels, width, height = load_image(path)

if __name__=="__main__":
    main()