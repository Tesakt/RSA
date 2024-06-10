from PIL import Image
import requests
import os
from io import BytesIO


def dithering(image):
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            oldpixel = pixels[x, y][0]
            newpixel = 255 if oldpixel >= 128 else 0
            pixels[x, y] = (newpixel, newpixel, newpixel)
            quant_error = oldpixel - newpixel
            if x + 1 < width:
                pixels[x + 1, y] = tuple(int(a + quant_error * 7 / 16) for a in pixels[x + 1, y])
            if x - 1 >= 0 and y + 1 < height:
                pixels[x - 1, y + 1] = tuple(int(a + quant_error * 3 / 16) for a in pixels[x - 1, y + 1])
            if y + 1 < height:
                pixels[x, y + 1] = tuple(int(a + quant_error * 5 / 16) for a in pixels[x, y + 1])
            if x + 1 < width and y + 1 < height:
                pixels[x + 1, y + 1] = tuple(int(a + quant_error * 1 / 16) for a in pixels[x + 1, y + 1])
    return image

def image_to_binary_to_file(image):
    width, height = image.size
    binary_list = []
    for y in range(height):
        for x in range(width):
            pixel = image.getpixel((x, y))
            binary_list.append(1 if pixel[0] == 255 else 0)
            
    with open("trng/extractor_bites.bin", "ab") as file:
        for i in range(0, len(binary_list), 8):
            byte = 0
            for j in range(8):
                byte |= binary_list[i + j] << (7 - j)
            file.write(bytes([byte]))
            
    return binary_list

def arnold_cat_map(image, iterations=7):
    width, height = image.size
    N = width
    p, q = 1, 1

    for _ in range(iterations):
        new_image = Image.new("L", (width, height))

        for x in range(width):
            for y in range(height):
                nx = (x + p * y) % N
                ny = (q * x + (p * q + 1) * y) % N
                new_image.putpixel((nx, ny), image.getpixel((x, y)))

        image = new_image

    return image

def encrypt_image_blocks(image):
    width, height = image.size
    encrypted_blocks = []

    for y in range(0, height, 4):
        row = []
        for x in range(0, width, 4):
            black_pixel_count = 0

            for dy in range(4):
                for dx in range(4):
                    pixel = image.getpixel((x + dx, y + dy))
                    if pixel == 0:
                        black_pixel_count += 1

            encrypted_value = 0 if black_pixel_count % 2 == 0 else 1
            row.append(encrypted_value)

        encrypted_blocks.append(row)
    return encrypted_blocks

def zigzag_scan(matrix):
    if not matrix:
        return []

    result = []
    rows, cols = len(matrix), len(matrix[0])
    row, col = 0, 0
    going_down = True

    while row < rows and col < cols:
        result.append(matrix[row][col])
        if going_down:
            if row == rows - 1:
                col += 1
                going_down = False
            elif col == 0:
                row += 1
                going_down = False
            else:
                row += 1
                col -= 1
        else:
            if col == cols - 1:
                row += 1
                going_down = True
            elif row == 0:
                col += 1
                going_down = True
            else:
                row -= 1
                col += 1

    return [result[i:i+128] for i in range(0, len(result), 128)]

def post_process_random_sequence(combined_sequence):
    combined_sequence_str = ''.join(str(pixel) for block in combined_sequence for pixel in block)
    combined_sequence_str = combined_sequence_str.replace("1111111111", "1111011111")
    return combined_sequence_str

def process_image(Downloaded):
    dithered_image = dithering(Downloaded)
    image_to_binary_to_file(dithered_image)
    binary_image = dithered_image.convert('1')
    chaos_image = arnold_cat_map(binary_image)
    encrypted_blocks = encrypt_image_blocks(chaos_image)
    combined_sequence = zigzag_scan(encrypted_blocks)
    post_processed_sequence = post_process_random_sequence(combined_sequence)

    return post_processed_sequence

def run_TRNG():
    random_sequence = ""
    if os.path.exists("trng/random_sequence.bin"):
        open("trng/random_sequence.bin", "wb").close()
        
    if os.path.exists("trng/extractor_bites.bin"):
        open("trng/extractor_bites.bin", "wb").close()
    
    total_random_bits = 0
    # for i in range(0, 1):
    url = "https://picsum.photos/1024/1024"
    response = requests.get(url, stream=True)
    im = Image.open(BytesIO(response.content))
    
    random_sequence += process_image(im)
    total_random_bits += len(random_sequence)
    
    binary_data = bytes(int(random_sequence[i:i+8], 2) for i in range(0, len(random_sequence), 8))
    with open("trng/random_sequence.bin", "ab") as file:
        file.write(binary_data)

    print(f"Total random bits generated: {total_random_bits}")
    return random_sequence

if __name__ == "__main__":
    run_TRNG()
    print("Random sequences saved to random_sequence.bin and extractor_bites.bin")
