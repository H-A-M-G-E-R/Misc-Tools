# Requires pillow
from PIL import Image, ImageSequence
import math

if __name__ == "__main__":
    gif = Image.open(sys.argv[1], "r")
    offset = 7
    print(f"{gif.width}:{gif.height}")

    arranged = Image.new("RGBA", (256*8, 256*math.ceil((gif.n_frames+offset)/8)))
    x = (256*offset) % (256*8)
    y = 0
    for i, frame in enumerate(ImageSequence.Iterator(gif)):
        print(frame.info)
        arranged.paste(frame.resize((256, 256), resample=Image.NEAREST), (x, y))
        x += 256
        if x == 256*8:
            x = 0
            y += 256
    arranged.save(sys.argv[2])
