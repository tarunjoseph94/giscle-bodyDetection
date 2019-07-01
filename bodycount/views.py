from django.shortcuts import render
from django.http import HttpResponse
from bodycount.forms import ProfileForm
from django.core.files.storage import FileSystemStorage
import requests
import cv2
import base64
import hashlib
import time
import logging
import pymongo
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components

client = pymongo.MongoClient("localhost", 27017)
db = client.Test


def bodycount(filename):

	token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InRhcnVuam9zZXBoOTRAZ21haWwuY29tIiwidXNlcm5hbWUiOiJ0YXJ1bmpvc2VwaDk0IiwiZmlyc3RuYW1lIjoiVGFydW4ifQ.xj7miM4AA0NWsHEsxAa6maHFH5ikiAcBTu2LJwuOV5k"
	secret = "fbdf833e386eb88077f1cc3e28296262"
	imgPath = './media/'+filename
	img = open(imgPath,'rb')
	img = img.read()
	img_enc = base64.b64encode(img)
	img_enc = img_enc.decode('utf-8')
	re = requests.post('http://api.giscle.ml/body_detection',data={'image':img_enc},headers={'token': token})
	if re.ok:
		print(re.json())
		r = re.json()
		frame = cv2.imread(imgPath)
		for key in r['data'].keys():
			if key != 'total_person':
				x,y,h,w = (r['data'][str(key)])
				x,y,h,w = int(x),int(y),int(h),int(w)
				cv2.rectangle(frame, (x,y),(x+h,y+w), (255,0,0))
		# while True:
		# 	cv2.imshow("frame",frame)
		# 	if cv2.waitKey(1) & 0xFF == ord('q'):
		# 		break
		db.noOfBodies.insert_one({"image":filename,"total_persons":r['data']['total_person']}).inserted_id
		return r
	else:
		print(r.status_code)



def index(request):
	uploaded_file_url=""
	if request.method == 'POST' and request.FILES['myfile']:
		myImage=ProfileForm(request.FILES)
		myfile = request.FILES['myfile']
		fs = FileSystemStorage()
		filename = fs.save(myfile.name, myfile)
		uploaded_file_url = fs.url(filename)
		bodyCountJSON=bodycount(filename)
		return render(request, 'index.html', {'uploaded_file_url': uploaded_file_url,'bodycount':bodyCountJSON})
	return render(request, 'index.html',{})

def reports(request):
	xDict=list(db.noOfBodies.find({},{'_id':0,'image':1}))
	xLabel=[]
	for i in xDict:
		for j in i.values():
	 		xLabel.append(j)
	print(xLabel)
	yDict=list(db.noOfBodies.find({},{'_id':0,'total_persons':1}))
	yLabel=[]
	for i in yDict:
		for j in i.values():
	 		yLabel.append(j)
	print(yLabel)
	xCord=[]
	for i in range(1,len(yLabel)+1):
		xCord.append(i)
	print(xCord)
	p = figure(x_range=xLabel, plot_height=250, title="Body Counts",toolbar_location=None, tools="")
	p.vbar(x=xLabel, top=yLabel, width=0.9)
	script, div = components(p)

	# graph=plt.show()
	return render(request,'reports.html', {'script' : script , 'div' : div})
