from collections import deque
from piet_colors import piet_colors


class PietInterpreter:

    def __init__(self, pixels, width, height):
        self.pixels = pixels
        self.width = width
        self.height = height
        self.blocks = self.find_blocks()
        self.stack = []
        self.DP = 0
        self.CC = 0
        self.current_block_id = 0
        self.commands = {
            (1, 0): "push",
            (1, 1): "add",
            (1, 2): "subtract",
            (2, 0): "multiply",
            (2, 1): "divide",
            (2, 2): "mod",
            (3, 0): "not",
            (3, 1): "greater",
            (3, 2): "pointer",
            (4, 0): "switch",
            (4, 1): "duplicate",
            (4, 2): "roll",
            (5, 0): "in_number",
            (5, 1): "in_char",
            (5, 2): "out_number",
            (0, 0): None,  # переход без действия
            (0, 1): None,
            (0, 2): None,
        }

    @staticmethod
    def get_piet_color(rgb):
        return piet_colors.get(rgb, None)

    def find_blocks(self):
        visited = [[False] * self.height for i in range(self.width)]
        blocks = []
        block_id = 0

        for x in range(self.width):
            for y in range(self.height):

                if visited[x][y]:
                    continue

                rgb = self.pixels[x, y]
                color = self.get_piet_color(rgb)
                if color is None:
                    continue

                block_pixels = self.bfs(visited, x, y, rgb)
                blocks.append(
                    {
                        'id': block_id,
                        'color': color,
                        'rgb': rgb,
                        'pixels': block_pixels,
                        'size': len(block_pixels)
                    }
                )

                block_id += 1

        return blocks

    def bfs(self, visited, start_x, start_y, target_rgb):
        q = deque()
        q.append((start_x, start_y))
        block = []

        while q:
            x, y = q.popleft()
            if x < 0 or y < 0 or x >= self.width or y >= self.height:
                continue

            if visited[x, y]:
                continue

            if self.pixels[x, y] != target_rgb:
                continue

            visited[x, y] = True
            block.append((x, y))

            q.extend(
                (x + 1, y),
                (x - 1, y),
                (x, y - 1),
                (x, y + 1)
            )

        return block

    def execute_command(self, command, block_size):
        if command == "push":
            self.stack.append(block_size)

        elif command == "add":
            if len(self.stack) >= 2:
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a + b)

        elif command == "multiply":
            if len(self.stack) >= 2:
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a * b)

        elif command == "subtract":
            if len(self.stack) >= 2:
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(b-a)

        elif command == "mod":
            if len(self.stack) >= 2:
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(b%a)

        elif command == "divide":
            if len(self.stack) >= 2:
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(b//a)

        elif command == "not":
            if not self.stack:
                raise ValueError("Cтек пуст")
            value = self.stack.pop()
            result = 1 if value == 0 else 0
            self.stack.append(result)

        elif command == "greater":
            if len(self.stack) >= 2:
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(1 if b>a else 0)

        elif command == "duplicate":
            if not self.stack:
                raise ValueError("Cтек пуст")
            copy = self.stack[0]
            self.stack.append(copy)

        elif command == "in_number":
            try:
                number = int(input())
                self.stack.append(number)
            except ValueError:
                raise ValueError("Введено не число")

        elif command == "in_char":
            try:
                symbol = input()
                self.stack.append(symbol)
            except ValueError:
                raise ValueError("Ввод пуст")

        elif command == "switch":
            if self.stack.pop()%2 == 1:
                self.CC = 1 - self.CC

        elif command == "out_number":
            value = self.stack.pop()
            print(value, end = '')

        elif command == "roll":
            n = self.stack.pop()
            m = self.stack.pop()
            if m>len(self.stack) or m<0:
                raise ValueError()

            section = self.stack[-m:]
            n = n%m if m>0 else 0
            self.stack[-m:] = section[-n:]+section[:-n]

