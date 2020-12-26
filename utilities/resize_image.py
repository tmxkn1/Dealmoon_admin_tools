import os
import sys
from shutil import copyfile
from PIL import Image

def resize_square(path, size, padding) -> Image.Image:
    img = Image.open(path)

    ratio = img.width/img.height
    if img.width > img.height:
        resize_width = size - padding
        resize_height = round(resize_width/ratio)
    else:
        resize_height = size - padding
        resize_width = round(resize_height*ratio)
    
    image_resize = img.resize((resize_width, resize_height), Image.ANTIALIAS)
    background = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    offset = (round((size - resize_width) / 2), round((size - resize_height) / 2))
    background.paste(image_resize, offset)
    return background.convert('RGB')

img_files = sys.argv[1:]
image_folder = os.path.join(os.getcwd(), 'image')
if not os.path.exists(image_folder):
    os.mkdir(image_folder)

sizes = [(600, 40), (400, 20)]
for f in img_files:
    for size in sizes:
        file_name = '.'.join(os.path.basename(f).split('.')[:-1])
        new_img = resize_square(f, size[0], size[1])
        file = os.path.join(image_folder, str(size[0])+'_'+file_name+'.jpg')
        new_img.save(file)