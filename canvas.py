from PIL import Image, ImageDraw

def show(maze, sight, player, gif, width=320, height=320):
    img = Image.new("RGB", (width, height), "#000000")
    draw = ImageDraw.Draw(img)
    draw.polygon(sight, fill=(200,190,66))
    for i in xrange(-1,len(maze)):
        draw.line((maze[i - 1][0], maze[i - 1][1], maze[i][0], maze[i][1]), fill=(100,100,100))
        draw.text((maze[i][0], maze[i][1]), str(i), fill=(130,130,130))
    draw.line((player[0]-3,player[1]-3,player[0]+3,player[1]+3), fill=(255,0,0))
    draw.line((player[0]-3,player[1]+3,player[0]+3,player[1]-3), fill=(255,0,0))
    gif.append(img)

