from PIL import Image, ImageDraw, ImageFont


DIMS = (500, 726)
GREEN = (56, 161, 42)
YELLOW = (189, 186, 36)
RED = (166, 38, 38)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def makeImage(num, value, color, text_color):
    img = Image.new('RGB', DIMS, color=color)
    d = ImageDraw.Draw(img)

    fnt = ImageFont.truetype('arial.ttf', size=75)
    d.text((10, 10), str(value), font=fnt, fill=text_color)

    img.save(f"cardImages/{ num }.png")


# make multicolored 1
makeImage(13, 1, BLACK, WHITE)

# make the other cards
for value in range(1, 12):
    for c in range(3):
        if c == 0:
            color = GREEN
        elif c == 1:
            color = YELLOW
        else:
            color = RED
        num = 10 * value + c
        makeImage(num, value, color, WHITE)
        