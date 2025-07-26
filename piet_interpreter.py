import numpy as np
from piet_colors import get_color_by_number, get_command


class PietInterpreter:
    def __init__(self, image_array: np.ndarray):
        self.image_array = image_array
        self.height, self.width = image_array.shape[:2]
        self.pointer = (0, 0)
        self.stack = []
        self.dp = 0
        self.cc = 0
        self.block = set()
        self.breakpoint_found = False
        self.debug = True

    def run(self):
        while self.pointer is not None:
            block = self.DFS(self.pointer)
            self.block = block
            border = self.get_border(block, self.dp)
            next_pos = self.step_from_border(border, self.dp, self.cc)
            if next_pos is None or self.get_colour(next_pos) == 'black':
                next_pos = self.try_rotate()
            if next_pos is None:
                break
            self.execute_command_from(self.pointer, next_pos)
            self.pointer = next_pos

    def get_colour(self, pos):
        y, x = pos
        if not (0 <= y < self.height and 0 <= x < self.width):
            return None
        rgb = tuple(self.image_array[y, x][:3])
        hex_colour = self.convert_to_hex_colour(rgb)
        colour = get_color_by_number(hex_colour)
        return colour  # не превращаем в black по умолчанию!

    def convert_to_hex_colour(self, rgb):
        return '#%02x%02x%02x' % rgb

    def DFS(self, start):
        colour = self.get_colour(start)
        visited = set()
        stack = [start]
        while stack:
            pos = stack.pop()
            if pos in visited:
                continue
            visited.add(pos)
            y, x = pos
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = y + dy, x + dx
                npos = (ny, nx)
                if (0 <= ny < self.height and 0 <= nx < self.width
                        and self.get_colour(npos) == colour
                        and npos not in visited):
                    stack.append(npos)
        return visited

    def get_border(self, block, dp):
        dy, dx = [(0, 1), (1, 0), (0, -1), (-1, 0)][dp]
        max_coord = -float('inf')
        border = []
        for y, x in block:
            if y * dy + x * dx > max_coord:
                max_coord = y * dy + x * dx
                border = [(y, x)]
            elif y * dy + x * dx == max_coord:
                border.append((y, x))
        return border

    def step_from_border(self, border, dp, cc):
        if not border:
            return None
        if self.dp % 2 == 0:
            border.sort(key=lambda p: p[0], reverse=self.cc == 1)
        else:
            border.sort(key=lambda p: p[1], reverse=self.cc == 1)
        y, x = border[0]
        dy, dx = [(0, 1), (1, 0), (0, -1), (-1, 0)][dp]
        ny, nx = y + dy, x + dx
        if not (0 <= ny < self.height and 0 <= nx < self.width):
            return None
        next_color = self.get_colour((ny, nx))
        if next_color == 'white':
            return self.step_through_white((ny, nx), dp)
        elif next_color != 'black':
            return (ny, nx)
        return None

    def step_through_white(self, start_pos, dp):
        dy, dx = [(0, 1), (1, 0), (0, -1), (-1, 0)][dp]
        pos = start_pos
        while True:
            y, x = pos[0] + dy, pos[1] + dx
            if not (0 <= y < self.height and 0 <= x < self.width):
                return None
            color = self.get_colour((y, x))
            if color == 'black':
                return None
            elif isinstance(color, tuple):
                return (y, x)
            pos = (y, x)

    def try_rotate(self):
        for _ in range(8):
            self.cc = (self.cc + 1) % 2
            if self.cc == 0:
                self.dp = (self.dp + 1) % 4
            block = self.DFS(self.pointer)
            border = self.get_border(block, self.dp)
            next_pos = self.step_from_border(border, self.dp, self.cc)
            if next_pos and self.get_colour(next_pos) != 'black':
                return next_pos
        return None

    def execute_command_from(self, curr, next_pos):
        color_from = self.get_colour(curr)
        color_to = self.get_colour(next_pos)

        if isinstance(color_from, str) or isinstance(color_to, str):
            return

        hue_change = (color_to[0] - color_from[0]) % 6
        lightness_change = (color_to[1] - color_from[1]) % 3
        command = get_command(hue_change, lightness_change)

        if self.debug and self.breakpoint_found:
            print(f"Command: {command}")

        self.execute_command(command)

    def pop_safe(self):
        return self.stack.pop() if self.stack else None

    def pop2_safe(self):
        if len(self.stack) >= 2:
            a = self.stack.pop()
            b = self.stack.pop()
            return b, a
        return None

    def execute_command(self, command):
        try:
            if command == 'push':
                self.stack.append(len(self.block))
            elif command == 'pop':
                self.pop_safe()
            elif command == 'add':
                if (vals := self.pop2_safe()):
                    a, b = vals
                    self.stack.append(a + b)
            elif command == 'subtract':
                if (vals := self.pop2_safe()):
                    a, b = vals
                    self.stack.append(b - a)
            elif command == 'multiply':
                if (vals := self.pop2_safe()):
                    a, b = vals
                    self.stack.append(a * b)
            elif command == 'divide':
                if (vals := self.pop2_safe()):
                    a, b = vals
                    self.stack.append(b // a if a != 0 else 0)
            elif command == 'mod':
                if (vals := self.pop2_safe()):
                    a, b = vals
                    self.stack.append(b % a if a != 0 else 0)
            elif command == 'not':
                val = self.pop_safe()
                self.stack.append(0 if val else 1)
            elif command == 'greater':
                if (vals := self.pop2_safe()):
                    a, b = vals
                    self.stack.append(1 if b > a else 0)
            elif command == 'duplicate':
                if self.stack:
                    self.stack.append(self.stack[-1])
            elif command == 'roll':
                if len(self.stack) >= 2:
                    rolls = self.stack.pop()
                    depth = self.stack.pop()
                    if depth > 0 and len(self.stack) >= depth:
                        segment = self.stack[-depth:]
                        rolls %= depth
                        segment = segment[-rolls:] + segment[:-rolls]
                        self.stack[-depth:] = segment
            elif command == 'in_number':
                self.stack.append(int(input()))
            elif command == 'in_char':
                self.stack.append(ord(input()[0]))
            elif command == 'out_number':
                val = self.pop_safe()
                if val is not None:
                    print(val, end=" ")
            elif command == 'out_char':
                val = self.pop_safe()
                if val is not None:
                    print(chr(val), end="")
        except Exception as e:
            if self.debug:
                print("Ошибка при выполнении команды:", command, e)
