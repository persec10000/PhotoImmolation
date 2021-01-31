import os
from flask import Flask, request, redirect, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
import re
import merge2
import body_seg
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import OpenPoseImage2
from flask_sessionstore import Session
from shutil import copyfile

app = Flask(__name__)
app.config.from_object(__name__)
Session(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.arrPosUser = [(289, 150), (289, 233), (178, 217), (200, 367), (400, 333), (422, 267), (422, 500), (467, 367), (178, 584), (422, 617), (467, 634), (311, 534), (512, 567), (690, 684), (289, 116), (333, 150), (267, 100), (378, 166)]
app.fOrg='pose2.jpg'
app.fBody = app.fOrg+'_seg_body.png'
app.fGray = app.fOrg+'_seg_grey.png'
app.fPosePt = app.fOrg+'_Out-Keypoints.jpg'
app.fPoseLn = app.fOrg+'_Out-Skeleton.jpg'

app.arrPosMajor2=[(1085, 234), (1085, 281), (1057, 266), (1001, 250), (1029, 219), (1113, 297), (1113, 375), (1085, 438), (1029, 406), (973, 485), (1001, 563), (1085, 422), (1057, 516), (1113, 594), (1057, 234), (1085, 234), None, (1113, 234)]
app.arrPosMajor1=[(1085, 156), (1113, 203), (1057, 203), (1057, 281), (1057, 344), (1140, 203), (1140, 281), (1168, 360), (1085, 344), (1085, 453), (1085, 563), (1113, 344), (1113, 453), (1113, 516), (1085, 156), (1085, 156), None, (1113, 156)]

@app.route("/")
def index():
    images = os.listdir('./image_major')
    print (images)
    return render_template("index.html", images=images)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/ChangeFullBody")
def ChangeFullBody():
    #print('current-img:')
    #print(type(Session))
    #print(Session['sel_img'])
    fMajors = os.listdir('./image_major_bg')
    print(fMajors)

    images = []
    strSuffixReplace = '_replace.jpg'

    fReplace = merge2.mergeReplace('img_user_uploaded/'+fMajors[0],
        'img_user_uploaded/'+app.fBody,
        app.arrPosMajor1,
        app.arrPosUser
        )    
    fDst = fMajors[0]+app.fOrg+strSuffixReplace
    copyfile(fReplace, 'images/'+fDst)
    images.append(fDst)
    print(fDst)

    fReplace = merge2.mergeReplace('img_user_uploaded/'+fMajors[1],
        'img_user_uploaded/'+app.fBody,
        app.arrPosMajor2,
        app.arrPosUser
        )
    fDst = fMajors[1]+app.fOrg+strSuffixReplace
    copyfile(fReplace, 'images/'+fDst)
    images.append(fDst)
    print(fDst)

    return render_template("index.html", images=images)


@app.route("/ViewMajorPose")
def ViewMajorPose():
    images = os.listdir('./image_major_pose')
    return render_template("index.html", images=images)

@app.route("/UserImg")
def UserImg():
    print ("fPoseLn:"+app.fPoseLn)
    return render_template('uploaded.html',imgfile=app.fOrg,
        imgBody=app.fBody,
        imgGray=app.fGray,
        imgPosePt=app.fPosePt,
        imgPoseLn=app.fPoseLn,
        ) 

@app.route("/upload", methods=["GET","POST"])
def upload_file():
    if request.method=="GET":
        return render_template('upload.html',imgfile=app.fOrg,
        imgBody=app.fBody,
        imgGray=app.fGray,
        imgPosePt=app.fPosePt,
        imgPoseLn=app.fPoseLn,
        ) 
    dirUserUpload = 'img_user_uploaded/'
    target = os.path.join(APP_ROOT, dirUserUpload)
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)


    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination) 
        file.save(destination) 
        
        body_seg.body_segment_v2(destination) # +_seg_body.png, +_seg_grey.png
        app.arrPosUser = OpenPoseImage2.getpose(destination) # dest+_Out-Keypoints.jpg, dest+_Out-Skeleton.jpg
        print("app.arrPosUser")
        print(app.arrPosUser)
        app.fOrg = filename
        app.fBody = filename+'_seg_body.png'
        app.fGray = filename+'_seg_grey.png'
        app.fPosePt = filename+'_Out-Keypoints.jpg'
        app.fPoseLn = filename+'_Out-Skeleton.jpg'
        print ("fBody in for:"+app.fBody)
        print ("fPoseLn:"+app.fPoseLn)
        break;
    print ("fBody out for:"+app.fBody)
    print ("fPoseLn:"+app.fPoseLn)
    # return render_template('uploaded.html')
    return render_template('uploaded.html',imgfile=app.fOrg,
        imgBody=app.fBody,
        imgGray=app.fGray,
        imgPosePt=app.fPosePt,
        imgPoseLn=app.fPoseLn,
        ) 

@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

def send_image_for_filter(image):
    return render_template('filter.html', image=image)

@app.route('/img_user_uploaded/<filename>')
def send_image_for_user(filename):
    return send_from_directory("img_user_uploaded", filename)



@app.route("/filters")
def filter():
    return render_template('filters.html')

@app.url_defaults
def hashed_url_for_static_file(endpoint, values):
    if 'static' == endpoint or endpoint.endswith('.static'):
        filename = values.get('filename')
        if filename:
            if '.' in endpoint:  # has higher priority
                blueprint = endpoint.rsplit('.', 1)[0]
            else:
                blueprint = request.blueprint  # can be None too
            if blueprint:
                static_folder = app.blueprints[blueprint].static_folder
            else:
                static_folder = app.static_folder
            param_name = 'h'
            while param_name in values:
                param_name = '_' + param_name
            values[param_name] = static_file_hash(os.path.join(static_folder, filename))

def static_file_hash(filename):
    return int(os.stat(filename).st_mtime)

if __name__ == "__main__":
    app.run(port=80)