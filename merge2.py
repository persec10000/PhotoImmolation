#!/usr/bin/env python
from flask import Flask, render_template, Response
import io
import cv2
import re
import math
from flask import request
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import OpenPoseImage2


def merge2img(file_major,file_user):
    img = Image.open(file_user)#.convert("RGBA")
    print(img.size)
    background = Image.open(file_major)
    print(background.size)
    


    arrPos_major = OpenPoseImage2.getpose(file_major)
    arrPos_user = OpenPoseImage2.getpose(file_user)
    print (arrPos_major)
    print (arrPos_user)



    # resize the image
    dWidth_major = (math.hypot( arrPos_major[2][0] - arrPos_major[5][0],arrPos_major[2][1] - arrPos_major[5][1]))
    dWidth_user = (math.hypot( arrPos_user[2][0] - arrPos_user[5][0],arrPos_user[2][1] - arrPos_user[5][1]))
    print(dWidth_major)
    print(dWidth_user)
    #dWidth_major = OpenPoseImage2.calculateDistance( arrPos_major[2][0],arrPos_major[2][1],arrPos_major[5][0],arrPos_major[5][1] )
    #print(dWidth_major) # hypot == calculateDistance
    fRatio = (dWidth_major/dWidth_user)*1.2
    size = (int(img.size[0]*fRatio),int(img.size[1]*fRatio))
    print (size)
    img = img.resize(size,Image.ANTIALIAS)
    img.save('templates/resize_user.png',"PNG")

    #merge 2 images
    nCenter = 1
    dx = arrPos_major[nCenter][0] - int(arrPos_user[nCenter][0]*fRatio)
    dy = arrPos_major[nCenter][1] - int(arrPos_user[nCenter][1]*fRatio)
    print (arrPos_major[0][0])
    print ("dx:"+str(dx)+" dy:"+str(dy))
    background.paste(img, (dx, dy), img)
    background.save('templates/merge_by_func.png',"PNG")    

def mergeReplace(file_major,file_user,arrPos_major,arrPos_user):
    img = Image.open(file_user)#.convert("RGBA")
    print(img.size)
    background = Image.open(file_major)
    print(background.size)
    
    print (arrPos_major)
    print (arrPos_user)


    # resize the image
    dWidth_major = (math.hypot( arrPos_major[1][0] - arrPos_major[10][0],arrPos_major[1][1] - arrPos_major[10][1]))
    dWidth_user = (math.hypot( arrPos_user[1][0] - arrPos_user[10][0],arrPos_user[1][1] - arrPos_user[10][1]))
    print(dWidth_major)
    print(dWidth_user)
    #dWidth_major = OpenPoseImage2.calculateDistance( arrPos_major[2][0],arrPos_major[2][1],arrPos_major[5][0],arrPos_major[5][1] )
    #print(dWidth_major) # hypot == calculateDistance
    fRatio = (dWidth_major/dWidth_user)*1.11
    size = (int(img.size[0]*fRatio),int(img.size[1]*fRatio))
    print (size)
    img = img.resize(size,Image.ANTIALIAS)
    img.save(file_user+'_resize.png',"PNG")

    #merge 2 images
    nCenter = 1
    dx = arrPos_major[nCenter][0] - int(arrPos_user[nCenter][0]*fRatio)
    dy = arrPos_major[nCenter][1] - int(arrPos_user[nCenter][1]*fRatio)
    print (arrPos_major[0][0])
    print ("dx:"+str(dx)+" dy:"+str(dy))
    background.paste(img, (dx, dy), img)
    fSave = file_major+'_replace.png'
    background.save(fSave,"PNG")
    return fSave


if __name__ == '__main__':
    file_user = 'templates/download.png'
    file_major = 'templates/category1.jpg'
    merge2img(file_major,file_user)
