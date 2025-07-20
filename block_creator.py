from collections import deque
from piet_colors import piet_colors


def get_piet_color(rgb):
    return piet_colors.get(rgb, None)


def find_blocks(pixels, width, height):
    visited = [[False] * height for i in range(width)]
    blocks = []
    block_id = 0

    for x in range(width):
        for y in range(height):

            if visited[x][y]:
                continue

            rgb = pixels[x, y]
            color = get_piet_color(rgb)
            if color is None:
                continue

            block_pixels = bfs(pixels, visited, width, height, x, y, rgb)
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


def bfs(pixels, visited, width, height, start_x, start_y, target_rgb):
    q = deque()
    q.append((start_x, start_y))
    block = []

    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= width or y >= height:
            continue

        if visited[x, y]:
            continue

        if pixels[x, y] != target_rgb:
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
