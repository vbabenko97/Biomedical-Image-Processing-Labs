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

MIN = -0.2
MAX = 0.2
DEFAULT_IMAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "Images"
    / "ImageForLab2-6"
    / "DICOM_Image_16b.dcm"
)


def load_texture(pixels, type):
    gl_type = ARRAY_TO_GL_TYPE_MAPPING.get(pixels.dtype) # возвращает GL_SHORT
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    glTexImage2D(GL_TEXTURE_2D, 0, type, width, height, 0, type, gl_type, pixels)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


def load_image(filename):
    global width, height, image, current_pixels, max_brightness, image_type
    image = pydicom.read_file(filename)
    width = image['0028', '0011'].value
    height = image['0028', '0010'].value
    current_pixels = image.pixel_array
    image_type = np.dtype('int' + str(image['0028', '0100'].value)) # int16
    max_brightness = np.iinfo(image_type).max # максимальное значение int16


def init():
    global image
    load_texture(image.pixel_array, GL_LUMINANCE)
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)


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


def reshape(w, h):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluOrtho2D(0.0, w, 0.0, h)


def keyboard(key, x, y):
    global image, current_pixels
    if key == chr(27).encode():
        sys.exit(0)
    elif key == b'w':
        current_pixels = window_level_operation(np.array(image.pixel_array))
    elif key == b'e':
        current_pixels = equalize(np.array(image.pixel_array))
    elif key == b'r':
        current_pixels = image.pixel_array
    load_texture(current_pixels, GL_LUMINANCE)
    display()


def draw_text(text, x, y):
    glDisable(GL_TEXTURE_2D)
    glColor3f(255, 255, 255)
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(character))
    glEnable(GL_TEXTURE_2D)


def motion(x, y):
    global current_pixels
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)
    if 0 < x < width and 0 < y < height:
        text = "brightness: " + str(current_pixels[x][y])
        display()
        draw_text(text, 5, height - 15)
    else:
        display()
    glFlush()


def min_max_pixels(pixels):
    pixels_array = []
    for row in pixels:
        for pixel in row:
            pixels_array.append(pixel)
    return {'min': min(pixels_array), 'max': max(pixels_array)}


def window_level_operation(pixels):
    new_pixels = []
    min_max = min_max_pixels(pixels)
    max_pixel = min_max['max'] * MAX
    min_pixel = min_max['min'] * MIN
    level = (max_pixel - min_pixel) / 2
    window = max_pixel - min_pixel
    min_brightness = 0
    for row in pixels:
        new_row = []
        for value in row:
            if value <= level - window / 2:
                new_value = min_brightness
            elif value > level + window / 2:
                new_value = max_brightness
            else:
                new_value = min_brightness + (value - level) * (max_brightness - min_brightness) / window

            new_row.append(int(new_value))
        new_pixels.append(new_row)
    return np.array(new_pixels, image_type)


def equalize(pixels):
    global max_brightness, image_type
    max = max_brightness
    min = 0
    n = pixels.size
    histogram = np.zeros(max)
    for row in pixels:
        for value in row:
            histogram[value] = histogram[value] + 1
    sum = 0
    lut = np.zeros(n)
    for i in range(0, max):
        sum += histogram[i]
        lut[i] = min + (sum * (max - min)) / n
    result = []
    for row in pixels:
        new_row = []
        for value in row:
            new_row.append(lut[value])
        result.append(new_row)
    return np.array(result, image_type)


def main(filename):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    load_image(filename)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow('Babenko_lab2')
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutPassiveMotionFunc(motion)
    glutMainLoop()


def parse_args():
    parser = argparse.ArgumentParser(description="Run Lab 2 DICOM viewer.")
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
