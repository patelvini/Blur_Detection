# USAGE
# python detect_blur.py --images images [--threshold 120.0]

# import the necessary packages
from imutils import paths
import argparse
import cv2
import os
import json
from sklearn.metrics import accuracy_score

class BlurDetector:

	def __init__(self):
		self.path = os.getcwd()
		self.base_path = os.path.join(self.path,'results')
		self.blur_path = os.path.join(self.base_path,'blur_images')
		self.sharp_path = os.path.join(self.base_path,'sharp_images')
		self.json_data = []
		self.b_count = 0
		self.s_count = 0

		# check if the directory to store data exists
		if not os.path.exists(self.base_path):
			os.mkdir(self.base_path)
		if not os.path.exists(self.blur_path):
			os.mkdir(self.blur_path)
		if not os.path.exists(self.sharp_path):
			os.mkdir(self.sharp_path)

	def variance_of_laplacian(self, image):
		# compute the Laplacian of the image and then return the focus
		# measure, which is simply the variance of the Laplacian
		return cv2.Laplacian(image, cv2.CV_64F).var()


	def save_json(self, imagePath, fm, text):
		# store info in json file
		json_object = {
			"Image":imagePath,
			"Variance of Laplacian":fm,
			"Result":text
		}
		
		self.json_data.append(json_object)

		with open('jsonResult.json','w') as outfile:
			json.dump(self.json_data, outfile, indent=4)

	def separate_images(self, text, image):
		if (text == "Blurry"):
			filename = 'blur_'+str(self.b_count)+'.jpg'
			filename = os.path.join(self.blur_path,filename)
			cv2.imwrite(filename, image)
			cv2.waitKey(0)
			self.b_count += 1
		elif (text == "Sharp"):
			filename = 'sharp_'+str(self.s_count)+'.jpg'
			filename = os.path.join(self.sharp_path,filename)
			cv2.imwrite(filename, image)
			cv2.waitKey(0)
			self.s_count += 1
		else:
			pass
		

if __name__ == '__main__':

	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--images", required=True,
		help="path to input directory of images")
	ap.add_argument("-t", "--threshold", type=float, default=100.0,
		help="focus measures that fall below this value will be considered 'blurry'")
	args = vars(ap.parse_args())

	image_list = paths.list_images(args["images"])

	n = len(list(image_list))
	actual_list = []
	predicted_list = []
	for i in range (1,n+1):
		if i%3==0:
			actual_list.append(1)
		else:
			actual_list.append(0)

	print("Please Wait...")
	blur_detector = BlurDetector()

	# loop over the input images
	for imagePath in paths.list_images(args["images"]):
		# load the image, convert it to grayscale, and compute the
		# focus measure of the image using the Variance of Laplacian
		# method
		image = cv2.imread(imagePath)
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		fm = blur_detector.variance_of_laplacian(gray)
		text = "Sharp"

		# if the focus measure is less than the supplied threshold,
		# then the image should be considered "blurry"
		if fm < args["threshold"]:
			text = "Blurry"

		cv2.putText(image, "{}: {:.2f}".format(text, fm), (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
		
		print(f"{text} : {fm}")

		if (text == "Blurry"):
			predicted_list.append(0)
		elif (text == "Sharp"):
			predicted_list.append(1)

		blur_detector.save_json(imagePath, fm, text)
		blur_detector.separate_images(text, image)

	print("Done!!")
	print("Result stored into '//results' folder")

	print("Accuracy: ",accuracy_score(actual_list,predicted_list)*100,"%")
