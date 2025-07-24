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
        self.visited = set()
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
        return colour if colour else 'black'

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
        border.sort(key=lambda p: (p[0], p[1]), reverse=bool(cc))
        y, x = border[0]
        dy, dx = [(0, 1), (1, 0), (0, -1), (-1, 0)][dp]
        ny, nx = y + dy, x + dx
        if 0 <= ny < self.height and 0 <= nx < self.width:
            if self.get_colour((ny, nx)) != 'black':
                return (ny, nx)
        return None

    def try_rotate(self):
        for _ in range(8):
            self.cc = (self.cc + 1) % 2 if self.dp % 2 else self.cc
            self.dp = (self.dp + (1 if self.cc == 0 else 0)) % 4
            block = self.DFS(self.pointer)
            border = self.get_border(block, self.dp)
            next_pos = self.step_from_border(border, self.dp, self.cc)
            if next_pos and self.get_colour(next_pos) != 'black':
                return next_pos
        return None

    def execute_command_from(self, curr, next_pos):
        colour_from = self.get_colour(curr)
        colour_to = self.get_colour(next_pos)

        if isinstance(colour_from, str) or isinstance(colour_to, str):
            return

        hue_change = (colour_to[0] - colour_from[0]) % 6
        lightness_change = (colour_to[1] - colour_from[1]) % 3
        command = get_command(hue_change, lightness_change)

        if self.debug and self.breakpoint_found:
            print(f"Command: {command}")

        self.execute_command(command)

    def pop_safe(self):
        if self.stack:
            return self.stack.pop()
        return None

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
                    self.stack.append(vals[0] + vals[1])
            elif command == 'subtract':
                if (vals := self.pop2_safe()):
                    self.stack.append(vals[0] - vals[1])
            elif command == 'multiply':
                if (vals := self.pop2_safe()):
                    self.stack.append(vals[0] * vals[1])
            elif command == 'divide':
                if (vals := self.pop2_safe()):
                    self.stack.append(vals[0] // vals[1] if vals[1] != 0 else 0)
            elif command == 'mod':
                if (vals := self.pop2_safe()):
                    self.stack.append(vals[0] % vals[1] if vals[1] != 0 else 0)
            elif command == 'not':
                val = self.pop_safe()
                if val is not None:
                    self.stack.append(0 if val else 1)
            elif command == 'greater':
                if (vals := self.pop2_safe()):
                    self.stack.append(1 if vals[0] > vals[1] else 0)
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
