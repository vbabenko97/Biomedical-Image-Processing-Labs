# Copyright © 2020. All rights reserved.
# Authors: Vitalii Babenko
# Contacts: vbabenko2191@gmail.com

import argparse
from pathlib import Path
import sys
from math import radians, cos, sin

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
    glTexCoord3f(1.0, 0.0, 0.0)
    glVertex3f(shirina // 2, -shirina // 2, 0.0)
    glTexCoord3f(1.0, 1.0, 0.0)
    glVertex3f(-shirina // 2, -shirina // 2, 0.0)
    glTexCoord3f(0.0, 1.0, 0.0)
    glVertex3f(-shirina // 2, shirina // 2, 0.0)
    glTexCoord3f(0.0, 0.0, 0.0)
    glVertex3f(shirina // 2, shirina // 2, 0.0)
    glEnd()
    glFlush()


def izmeneni3(shirina, visota):
    global defoltnaya_matrica
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluOrtho2D(-shirina // 2, shirina // 2, -visota // 2, visota // 2)
    defoltnaya_matrica = glGetFloatv(GL_MODELVIEW_MATRIX)


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


def najati3(key, x, y):
    global curr_pixeli
    if key == chr(27).encode():
        sys.exit(0)
    elif key == b'r':
        glEnable(GL_TEXTURE_2D)
        zagruzka_texturi(norm_pixeli, GL_LUMINANCE)
        glLoadMatrixf(defoltnaya_matrica)
        otobrajeni3()
    elif key == b'1':
        glMultMatrixf(pervaya_matrica @ vtoraya_matrica)
        otobrajeni3()
    elif key == b'2':
        glMultMatrixf(np.linalg.inv(pervaya_matrica @ vtoraya_matrica))
        otobrajeni3()


def glavnaya_funkci9(filename):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    zagruzka_izobrajeni9(filename)
    glutInitWindowSize(shirina * 2, visota * 2)
    glutInitWindowPosition(255, 255)
    glutCreateWindow('Babenko_lab6')
    inicializaci9()
    glutDisplayFunc(otobrajeni3)
    glutReshapeFunc(izmeneni3)
    glutKeyboardFunc(najati3)
    glutMainLoop()


def parse_args():
    parser = argparse.ArgumentParser(description="Run Lab 6 transformations.")
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE_PATH,
        help="Path to the DICOM image.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    dict = {}
    dict['xvec'] = float(input("Vvedite vektor x dl9 pervoy transormacii: "))
    dict['yvec'] = float(input("Vvedite vektor y dl9 pervoy transormacii: "))
    dict['x'] = int(input("Vvedite vektor x dl9 vtoroy transormacii: "))
    dict['y'] = int(input("Vvedite vektor y dl9 pervoy transormacii: "))
    dict['alpha'] = float(input("Vvedite ugol x dl9 vtoroy transormacii: "))

    pervaya_matrica = np.array(
        [[1, 0, dict['xvec'], 0], [0, 1, dict['yvec'], 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        dtype=float,
    ).transpose()

    vtoraya_matrica = np.array(
        [
            [cos(radians(dict['alpha'])), sin(radians(dict['alpha'])), 0, 0],
            [-sin(radians(dict['alpha'])), cos(radians(dict['alpha'])), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ],
        dtype=float,
    ).transpose()

    glavnaya_funkci9(str(args.image))
