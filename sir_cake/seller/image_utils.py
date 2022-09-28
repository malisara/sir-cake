
def crop_center(img, cropped_width, cropped_height):
    img_width, img_height = img.size
    return img.crop(((img_width - cropped_width) // 2,
                    (img_height - cropped_height) // 2,
                    (img_width + cropped_width) // 2,
                    (img_height + cropped_height) // 2))


def crop_max_square(img):
    return crop_center(img, min(img.size), min(img.size))
