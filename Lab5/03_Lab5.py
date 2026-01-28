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


def zagruzka_texturi(pixeli, tip):
    gl_tip = ARRAY_TO_GL_TYPE_MAPPING.get(pixeli.dtype)
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    glTexImage2D(GL_TEXTURE_2D, 0, tip, shirina, visota, 0, tip, gl_tip, pixeli)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


def zagruzka_izobrajeni9(im9_fayla):
    global izobrajeni3, shirina, visota, tip_izobrajeni9, max_9rkost
    izobrajeni3 = pydicom.read_file(im9_fayla)
    shirina = izobrajeni3['0028', '0011'].value
    visota = izobrajeni3['0028', '0010'].value
    tip_izobrajeni9 = np.dtype('int' + str(izobrajeni3['0028', '0100'].value))
    max_9rkost = np.iinfo(tip_izobrajeni9).max


def inicializaci9():
    global norm_pixeli
    norm_pixeli = normalizaci9(np.array(izobrajeni3.pixel_array))
    zagruzka_texturi(norm_pixeli, GL_LUMINANCE)
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)


def otobrajeni3():
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(0.0, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0.0, visota)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(shirina, visota)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(shirina, 0.0)
    glEnd()
    glFlush()


def izmeneni3(shirina, visota):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluOrtho2D(0.0, shirina, 0.0, visota)


def normalizaci9(pixeli):
    maximum = np.amax(pixeli)
    min_peak = int(float(maximum) * 0.25)
    max_peak = int(float(maximum) * 0.85)
    noviy_min = 0
    noviy_max = max_9rkost
    resultat = []
    for stroka in pixeli:
        novaya_stroka = []
        for pixel in stroka:
            noviy_pixel = ((pixel - min_peak) / (max_peak - min_peak)) * (noviy_max - noviy_min)
            if noviy_pixel < noviy_min:
                noviy_pixel = noviy_min
            if noviy_pixel > noviy_max:
                noviy_pixel = noviy_max
            novaya_stroka.append(noviy_pixel)
        resultat.append(novaya_stroka)
    return np.array(resultat, tip_izobrajeni9)


def is_out_of_bounds(point, length):
    return (point - 1 < 0) or (point + 1 > length)


def get_real(pixeli, maska, i, j):
    pixel = 0
    for y in range(-1, 2):
        for x in range(-1, 2):
            pixel += maska[y + 1][x + 1] * pixeli[i + y][j + x]
    return pixel


def get_mirror(pixeli, maska, i, j):
    pixel = 0
    for y in range(-1, 2):
        for x in range(-1, 2):
            curr_i = i + y
            curr_j = j + x
            if is_out_of_bounds(curr_i, shirina - 1):
                curr_i = i - y
            if is_out_of_bounds(curr_j, visota - 1):
                curr_j = j - x
            pixel += maska[y + 1][x + 1] * pixeli[curr_i][curr_j]
    return pixel


def najati3(key, x, y):
    global curr_pixeli
    if key == chr(27).encode():
        sys.exit(0)
    elif key == b'r':
        glEnable(GL_TEXTURE_2D)
        zagruzka_texturi(norm_pixeli, GL_LUMINANCE)
        otobrajeni3()
    elif key == b'1':
        curr_pixeli = filtr_gaussa(norm_pixeli)
        glEnable(GL_TEXTURE_2D)
        zagruzka_texturi(curr_pixeli, GL_LUMINANCE)
        otobrajeni3()
    elif key == b'2':
        curr_pixeli = operator_laplasa(curr_pixeli)
        glEnable(GL_TEXTURE_2D)
        zagruzka_texturi(curr_pixeli, GL_LUMINANCE)
        otobrajeni3()
    elif key == b'3':
        curr_pixeli = detekciya_porogov(curr_pixeli)
        glEnable(GL_TEXTURE_2D)
        zagruzka_texturi(curr_pixeli, GL_LUMINANCE)
        otobrajeni3()


def filtr_gaussa(pixeli):
    resultat = []
    for i, stroka in enumerate(pixeli):
        novaya_stroka = []
        for j, pixel in enumerate(stroka):
            if is_out_of_bounds(i, shirina - 1) or is_out_of_bounds(j, visota - 1):
                pixel_value = get_mirror(pixeli, maska_gausa, i, j)
            else:
                pixel_value = get_real(pixeli, maska_gausa, i, j)
            if pixel_value > max_9rkost:
                pixel_value = max_9rkost
            novaya_stroka.append(pixel_value)
        resultat.append(novaya_stroka)
    return np.array(resultat, tip_izobrajeni9)


def operator_laplasa(pixeli):
    resultat = []
    for i, stroka in enumerate(pixeli):
        novaya_stroka = []
        for j, pixel in enumerate(stroka):
            if is_out_of_bounds(i, shirina - 1) or is_out_of_bounds(j, visota - 1):
                pixel_value = get_mirror(pixeli, maska_laplaca, i, j)
            else:
                pixel_value = get_real(pixeli, maska_laplaca, i, j)
            if pixel_value > max_9rkost:
                pixel_value = max_9rkost
            novaya_stroka.append(pixel_value)
        resultat.append(novaya_stroka)
    return np.array(resultat, tip_izobrajeni9)


def detekciya_porogov(pixeli):
    resultat = np.zeros_like(pixeli)
    for i in range(1, pixeli.shape[0] - 1):
        for j in range(1, pixeli.shape[1] - 1):
            if pixeli[i][j] == 0:
                if (pixeli[i][j - 1] < 0 and pixeli[i][j + 1] > 0) or (
                        pixeli[i][j - 1] < 0 and pixeli[i][j + 1] < 0) or (
                        pixeli[i - 1][j] < 0 and pixeli[i + 1][j] > 0) or (
                        pixeli[i - 1][j] > 0 and pixeli[i + 1][j] < 0):
                    resultat[i][j] = max_9rkost
            if pixeli[i][j] < 0:
                if (pixeli[i][j - 1] > 0) or (pixeli[i][j + 1] > 0) or (pixeli[i - 1][j] > 0) or (pixeli[i + 1][j] > 0):
                    resultat[i][j] = max_9rkost
    return np.array(resultat, tip_izobrajeni9)


def glavnaya_funkci9(filename):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    zagruzka_izobrajeni9(filename)
    glutInitWindowSize(shirina, visota)
    glutInitWindowPosition(255, 255)
    glutCreateWindow('Babenko_lab5')
    inicializaci9()
    glutDisplayFunc(otobrajeni3)
    glutReshapeFunc(izmeneni3)
    glutKeyboardFunc(najati3)
    glutMainLoop()


# maska_gausa = [[0.01, 0.09, 0.01], [0.09, 0.64, 0.09], [0.01, 0.09, 10.01]]
maska_gausa = [[0.059, 0.097, 0.059], [0.097, 0.159, 0.097], [0.059, 0.097, 10.059]]
# maska_laplaca = [[0, -1, 0], [-1, 4, -1], [0, -1, 0]]
# maska_laplaca = [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]
# maska_laplaca = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
maska_laplaca = [[1, 1, 1], [1, -8, 1], [1, 1, 1]]


def parse_args():
    parser = argparse.ArgumentParser(description="Run Lab 5 filters on a DICOM image.")
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE_PATH,
        help="Path to the DICOM image.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    glavnaya_funkci9(str(args.image))
