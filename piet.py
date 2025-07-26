from PIL import Image
import numpy as np
import sys
import os
from piet_interpreter import PietInterpreter


def load_image(filename):
    image = Image.open(filename).convert('RGB')
    image_array = np.array(image)
    return image_array


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else 'fizzbuzz.png'

    if not os.path.exists(filename):
        print(f"Файл не найден: {filename}")
        return

    try:
        image_array = load_image(filename)
        interpreter = PietInterpreter(image_array)
        interpreter.run()
    except Exception as e:
        print("Ошибка", e)


if __name__ == "__main__":
    main()
