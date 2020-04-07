import cv2
import numpy as np
from nanoleaf import Aurora
import sys
from nanoleaf import setup
from collections import Counter
import mss
import mss.tools
from time import sleep
import colorsys
import os

###
# Commands for Aurora see Github 
# https://github.com/software-2/nanoleaf/blob/master/nanoleaf/aurora.py
# https://www.w3schools.com/colors/colors_rgb.asp
# https://www.w3schools.com/colors/colors_hsl.asp
###

def main():
	#the device to configure (ip, accesskey) see manual how to retrieve key)
	my_aurora = Aurora("IP of your NanoLeaf", "AccessKey generated from Nanoleaf insert here")
	
	#example
	my_aurora = Aurora("10.1.1.20", "loremipsumloremipsum")
	
	#if check_ping("10.1.1.20"):
	#need a try catch weil es errored wenn das gerät gar nicht vverfügbar ist
	#if my_aurora.on():
	if True:
		# set you screen resultion
		screen_size_width = 1920
		screen_size_height = 1080
		
		# how much shall we ignore, dueto black bars in movies, suggestion 20%, so set 20
		percent_to_ignore = 20

		# in % means, 10 = 10 % of all pixels, increases performance dramatically, 100 = all pixels
		pixels_2_analyse = 1.0
		
		# wait time when screen does not change
		wait_time = 0.1
		
		# time to incease each time nothing happens
		wait_time_increase = 0.25
		
		# maximum wait time to increase to, before aurora gets turned off,
		# will be turned on again automatically after wait_time interval 
		wait_time_maximum = 4.0
		
		# if something is wrong, debug = True can help to see why, check C:\out.txt
		debug = False
		
		###################################################################
		###################################################################
		############ No need to change any settings below here ############
		###################################################################
		###################################################################
		if debug: 
			from time import time
			import time
			sys.stdout = open("C:\\out.txt", "w")

		screen_dimensions = {
			"top": int(screen_size_width * ( percent_to_ignore / 100 ) ),
			"left": int(screen_size_height * ( percent_to_ignore / 100 ) ),
			"width": int(screen_size_width * ( 1 - percent_to_ignore*2 / 100 ) ),
			"height": int(screen_size_height * ( 1 - percent_to_ignore*2 / 100 ) )
		}
		
		x = screen_dimensions["width"] - screen_dimensions["left"]
		y = screen_dimensions["height"] - screen_dimensions["top"]
		every_x_pixels = int(100 / pixels_2_analyse)
		
		old_img = bytearray()
		color_old = np.array([0,0,0])
		darken_threshold = 50
		flag_aurora_off = False
		
		while True:
			if debug: start = time.time()
			with mss.mss() as sct:
				# Grab the screen data
				sct_img = sct.grab(screen_dimensions)
				
			# if screen was not changed, sleep
			if sct_img.raw == old_img:
				sleep(wait_time)
				
				# increase sleep time as long as nothing happens and maximum limit not reached
				if wait_time < wait_time_maximum:
					wait_time += wait_time_increase
					if debug: print( "Sleeping for ",wait_time)
				else:
					# check if aurora was already sent to go offline, if not go off
					if( not flag_aurora_off ):
						if debug: print("Sent Shutdown Signal to Aurora. Flag: ",flag_aurora_off)
						my_aurora.off = True
						flag_aurora_off = True
				continue
			else:
				if debug: print( "Reset sleep ",wait_time)
				wait_time = 0.1
				# flag_aurora_off = False

			old_img[:] = sct_img.raw

			# get list of all colors from img, but exclude colors darker than 50 rgb combined
			rgb_list = [[r,g,b] for r,g,b in zip(sct_img.raw[2::4][::every_x_pixels], sct_img.raw[1::4][::every_x_pixels], sct_img.raw[0::4][::every_x_pixels]) if (r+g+b>darken_threshold)]
			
			# calculates blacknessfactor based on all black pixels / total pixels
			blacknessfactor = (len(sct_img.raw[2::4][::every_x_pixels]) - len(rgb_list)) / float(len(sct_img.raw[2::4][::every_x_pixels]))
			
			# verify rgb_list contains more than 1 color set, otherwise cant calculate dominant color
			if len(rgb_list) > 1:
				# use dominant color:
				color_new = get_dominant_color(rgb_list, color_old)
			else:
				continue
				
			# make sure it is only a one Dimensional Array
			color_new = np.squeeze(color_new)
			
			#convert array to single values
			r,g,b = color_new

			#if debug: print("Before ",color_new)
					
			# if colors are too close to each other, they may be gray, white or black, so dont touch them
			if ( (abs(r-g) + abs(r-b)) > darken_threshold):
				# if color is darker than darken_threshold, black is domminant
				# reduce brightness of 2. color to 60%
				# if black is not dominant, but distance > 50, increase by 50% brightness
				if( (blacknessfactor * 100) > darken_threshold ):
					rgb_list = [[r,g,b] for r,g,b in rgb_list if r+g+b >= 20]
					color_new = get_dominant_color(rgb_list, color_old)
					brightness_factor = 0.3
				else:
					brightness_factor = 0.6
					
				r,g,b = color_new / 255.
				h,s,v = colorsys.rgb_to_hsv(r,g,b)
				#if debug: print("S:",s," V:",v)
				
				# multiple hsv with factor, clamp makes sure it is not larger as 3.arg and not smaller as 2.arg
				s = clamp(s * 1.2, 0.5, 1.0)	#farbsättigung
				v = clamp(v * brightness_factor, 0.1, 0.5) #helligkeit
				#if debug: print("S:",s," V:",v)
				
				#convert hsv back to rgb % and then real 255 numbers			
				color_new = np.array( [colorsys.hsv_to_rgb( h,s,v )] ) * 255
			else:
				color_new[:] = [r/2.,g/2.,b/2.]
				
			#if debug: print("After  ",color_new)

			# make sure it is only a one Dimensional Array
			color_new = np.squeeze(color_new)
			
			# catch white color wakeups when screen goes standby, so only flashes up and doest not show picuture
			if debug: print( "new color ",color_new)
			
			if flag_aurora_off:
				if np.array_equal(np.array([255,255,255]), color_new):
					continue
				else:
					flag_aurora_off = False
			
			# if it is a new color, sent it to aurora, if not leave it as it is
			if not np.array_equal(color_old, color_new):
				try:
					my_aurora.rgb = color_new
					color_old = color_new
				except:
					print("Erroneous color ",color_new)
			#if debug: print(time.time()-start)

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)
	
def get_dominant_color(lst, color_old):
	try:
		pixels = np.float32(lst)
		n_colors = 1
		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
		flags = cv2.KMEANS_RANDOM_CENTERS

		_, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
		_, counts = np.unique(labels, return_counts=True)

		dominant = palette[np.argmax(counts)]
	except:
		return color_old
	return dominant


def check_ping(hostname):
    response = os.system("ping -n 1 " + hostname)
    # and then check the response...
    if response == 0:
        pingstatus = "Network Active"
    else:
        pingstatus = "Network Error"
    return pingstatus
	
	
if __name__ == "__main__":
   main()