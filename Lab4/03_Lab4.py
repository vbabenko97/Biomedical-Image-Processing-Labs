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
    / "ImageForLab2-6"
    / "DICOM_Image_16b.dcm"
)


def display():
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


def reshape(w, h):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluOrtho2D(0.0, w, 0.0, h)


def load_image(filename):
    global image, width, height, image_type, max_brightness
    image = pydicom.read_file(filename)
    width = image['0028', '0011'].value
    height = image['0028', '0010'].value
    image_type = np.dtype('int' + str(image['0028', '0100'].value))
    max_brightness = np.iinfo(image_type).max


def init():
    global normalized_pixels
    normalized_pixels = normalize(np.array(image.pixel_array))
    load_texture(normalized_pixels, GL_LUMINANCE)
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)


def keyboard(key, x, y):
    if key == chr(27).encode():
        sys.exit(0)
    elif key == b's':
        new_pixels = niblack(normalized_pixels)
        load_texture(new_pixels, GL_LUMINANCE)
        display()
    elif key == b'r':
        load_texture(normalized_pixels, GL_LUMINANCE)
        display()


# Алгоритм Ніблека (Niblack thresholding)
def niblack(pixels):
    w = 15  # ширина вікна
    k = -0.2  # коефіцієнт чутливості
    threshold_array = []
    for i in range(pixels.shape[0]):
        row = []
        for j in range(pixels.shape[1]):
            window = []
            for y in range(-int(w / 2), int(w / 2) + 1):
                for x in range(-int(w / 2), int(w / 2) + 1):
                    point_i = i + y
                    point_j = j + x
                    if is_out_of_bounds(point_i, width - 1) or is_out_of_bounds(point_j, height - 1):
                        window.append(0)
                    else:
                        window.append(pixels[point_i][point_j])
            nu = np.mean(window)  # математичне сподівання (середнє значення)
            sigma = np.std(window)  # стандартне відхилення
            t = nu + k * sigma
            row.append(t)
        threshold_array.append(row)
    threshold_array = np.asarray(threshold_array)
    new_pixels = np.where(pixels <= threshold_array, 0, max_brightness)
    return np.array(new_pixels, image_type)


# Перевірка знаходження пікселя за межами зображення
def is_out_of_bounds(point, length):
    return (point - 1 < 0) or (point + 1 > length)


# Нормалізація пікселів (щоб зображення було нормально видно)
def normalize(pixels):
    global max_peak
    min_peak = int(float(np.amax(pixels)) * 0.25)
    max_peak = int(float(np.amax(pixels)) * 0.85)
    new_min = 0
    new_max = max_brightness
    result = []
    for row in pixels:
        new_row = []
        for pixel in row:
            new_pixel = ((pixel - min_peak) / (max_peak - min_peak)) * (new_max - new_min)
            if new_pixel < 0:
                new_pixel = 0
            if new_pixel > new_max:
                new_pixel = new_max
            new_row.append(new_pixel)
        result.append(new_row)
    return np.array(result, image_type)


def main(filename):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    load_image(filename)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow('BABENKO')
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()


def parse_args():
    parser = argparse.ArgumentParser(description="Run Lab 4 Niblack thresholding.")
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
