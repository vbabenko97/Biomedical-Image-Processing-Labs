# Copyright © 2020. All rights reserved.
# Authors: Vitalii Babenko
# Contacts: vbabenko2191@gmail.com

import argparse
from pathlib import Path
import sys

import numpy as np
import pydicom
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays.numpymodule import ARRAY_TO_GL_TYPE_MAPPING

DEFAULT_IMAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "Images"
    / "ImageForLab1"
    / "DICOM_Image_for_Lab_2.dcm"
)

# маски високочастотної фільтрації
masks = [
    [
        [-1 / 9, -1 / 9, -1 / 9],
        [-1 / 9, 8 / 9, -1 / 9],
        [-1 / 9, -1 / 9, -1 / 9]
    ],
    [
        [0, -1 / 6, 0],
        [-1 / 6, 4 / 6, -1 / 6],
        [0, -1 / 6, 0]
    ],
    [
        [-1 / 16, -2 / 16, -1 / 16],
        [-2 / 16, 12 / 16, -2 / 16],
        [-1 / 16, -2 / 16, -1 / 16]
    ],
]


def get_real(pixels, mask, i, j):
    pixel_value = 0
    for y in range(-1, 2):
        for x in range(-1, 2):
            pixel_value += mask[y + 1][x + 1] * pixels[i + y][j + x]
    return pixel_value


def get_extrapolation(pixels, mask, i, j):
    global height, width
    pixel_value = 0
    for y in range(-1, 2):
        for x in range(-1, 2):
            if is_out_of_bounds(i + y, width - 1) or is_out_of_bounds(j + x, height - 1):
                pixel_value += 0
            else:
                pixel_value += mask[y + 1][x + 1] * pixels[i + y][j + x]
    return pixel_value


def is_out_of_bounds(point, length):
    return (point - 1 < 0) or (point + 1 > length)


def filter(pixels, mask):
    global height, width, max_brightness, image_type
    result = []
    for i, row in enumerate(pixels):
        new_row = []
        for j, pixel in enumerate(row):
            if is_out_of_bounds(i, height - 1) or is_out_of_bounds(j, width - 1):  # якщо за межами зображення
                pixel_value = get_extrapolation(pixels, mask, i, j)
            else:
                pixel_value = get_real(pixels, mask, i, j)
            if pixel_value < 0:
                pixel_value = 0
            elif pixel_value > max_brightness:
                pixel_value = max_brightness
            new_row.append(pixel_value)
        result.append(new_row)
    return np.array(result, image_type)


def keyboard(key, x, y):
    global image, current_pixels
    if key == chr(27).encode():
        sys.exit(0)
    elif key == b'1':
        current_pixels = filter(np.array(image.pixel_array), masks[0])
    elif key == b'2':
        current_pixels = filter(np.array(image.pixel_array), masks[1])
    elif key == b'3':
        current_pixels = filter(np.array(image.pixel_array), masks[2])
    elif key == b'r':
        current_pixels = image.pixel_array
    load_texture(current_pixels, GL_LUMINANCE)
    display()
    print('Done')


def reshape(w, h):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluOrtho2D(0.0, w, 0.0, h)


def display():
    global width, height
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(0.0, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0.0, width)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(height, width)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(height, 0.0)
    glEnd()
    glFlush()


def load_texture(pixels, type):
    gl_type = ARRAY_TO_GL_TYPE_MAPPING.get(pixels.dtype)
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    glTexImage2D(GL_TEXTURE_2D, 0, type, width, height, 0, type, gl_type, pixels)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


def init():
    global image
    load_texture(image.pixel_array, GL_LUMINANCE)
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)


def load_image(filename):
    global width, height, image, current_pixels, max_brightness, image_type
    image = pydicom.read_file(filename)
    width = image['0028', '0011'].value
    height = image['0028', '0010'].value
    current_pixels = image.pixel_array
    image_type = np.dtype('int' + str(image['0028', '0100'].value))
    max_brightness = np.iinfo(image_type).max


def main(filename):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    load_image(filename)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow('Babenko_lab3')
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()


def parse_args():
    parser = argparse.ArgumentParser(description="Run Lab 3 filters on a DICOM image.")
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE_PATH,
        help="Path to the DICOM image.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(str(args.image))
