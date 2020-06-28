import sys
import csv
import math
from bs4 import BeautifulSoup
import datetime

# Load the SVG map
svg = open('counties.svg', 'r').read()

#read in FIPS population numbers to array "allfips"
allfips = {}
reader = csv.reader(open('FIPS-Population.txt'), delimiter=",")
 # 1001,55869
for row in reader:

	try: 
		fipsnum = row[0]
		population = row[1]
		allfips[fipsnum] = population
	except:
		pass

# Read in case/death numbers
alldates = {}
reader = csv.reader(open('us-counties.csv'), delimiter=",")
#reader = csv.reader(open('6-20-2020.txt'), delimiter=",")

next(reader)	# not the header


 # 2020-06-20,Autauga,Alabama,01001,431,9

# create array of all dates in the csv
for row in reader:

	csvdate = datetime.datetime.strptime(row[0], '%Y-%m-%d')
	csvdate = int(csvdate.strftime('%j'))

	try:
		len(alldates[csvdate])
	except:
		alldates[csvdate] = {}


# for each date in the array, create an array of counties

#	try:
	fipsnum = row[3]
	fips = "FIPS_" + fipsnum
	cases = int(row[4])
	deaths = int(row[5])
	
	alldates[csvdate][fips] = {} # total, new, new/pop

	alldates[csvdate][fips][0] = cases # total cases to date
	alldates[csvdate][fips][1] = 0 # avg new cases per day
	alldates[csvdate][fips][2] = 0 # avg new cases per sqrt(population)
	alldates[csvdate][fips][3] = deaths # total deaths to date
	alldates[csvdate][fips][4] = 0 # avg new deaths per day
	alldates[csvdate][fips][5] = 0 # avg new deaths per sqrt(population)
	
	try:	# weekly rolling average
		alldates[csvdate][fips][1] = (cases - alldates[csvdate-7][fips][0])/7
		alldates[csvdate][fips][4] = (deaths - alldates[csvdate-7][fips][3])/7

#		# daily cases per sqrt(population)
#		alldates[csvdate][fips][2] = float(alldates[csvdate][fips][1]) / math.sqrt(float(allfips[fipsnum])) 
#		alldates[csvdate][fips][5] = float(alldates[csvdate][fips][4]) / math.sqrt(float(allfips[fipsnum])) 

		# daily cases per population/1000
		alldates[csvdate][fips][2] = float(alldates[csvdate][fips][1]) / (float(allfips[fipsnum])/1000)
		alldates[csvdate][fips][5] = float(alldates[csvdate][fips][4]) / (float(allfips[fipsnum])/1000) 

	except:
		pass



# Output maps
for csvdate in alldates:
	print(csvdate)
	original_stdout = sys.stdout # Save a reference to the original standard output

	# Load into Beautiful Soup
	soup = BeautifulSoup(svg,features="html.parser")

	# Find counties
	paths = soup.findAll('path')

	# County style
	path_style = 'font-size:12px;fill-rule:nonzero;stroke:#333333;stroke-opacity:1;stroke-width:0.1;stroke-miterlimit:4;stroke-dasharray:none;stroke-linecap:butt;marker-start:none;stroke-linejoin:bevel;fill:'

	min_value = 0
	max_value = .5 # .25 for sqrt .5 for /1000

	# Color the counties based on case numbers
	for p in paths:
	 
		if p['id'] not in ["State_Lines", "separator"]:

		# pass
			try:
				cases = float(alldates[csvdate][p['id']][2])
			except:
				continue

			# adjust for oddities like negative case numbers
			if cases > max_value:
				cases = max_value
			if cases < min_value:
				cases = min_value
			
			#red% value of RGB set to match adjusted case numbers
			red =  math.floor( (float(cases - min_value) / float(max_value - min_value)) * 100 )
			green = math.floor(red/2)
			blue = math.floor(green/2)
			#set color string to append to style string
			color = 'rgb(' + str(red) + '%,' + str(green) + '%,' + str(blue) + '%);'
								
			p['style'] = path_style + color

# adding a new text tag at the end of the <svg> tag
#		<text x="350" y="340" fill="rgb(100,100,140)" font-size="1em" font-family="Arial, Helvetica, sans-serif">June 24, 2020</text>

	datetag = soup.new_tag("text")
	datetag['x'] = 350 # lower right
	datetag['y'] = 340
	datetag['style'] = 'fill:rgb(100,100,140); font-size:1em; font-family:Arial, Helvetica, sans-serif;'
	soup.svg.append(datetag)

	svgdate = datetime.datetime.strptime(str(csvdate), '%j')
	svgdatestring = svgdate.strftime('%B %-d, 2020')

	datetag.string = svgdatestring

	mapfile = str(csvdate).zfill(3) + "_map.svg"
	with open(mapfile, 'w') as f:
		sys.stdout = f # Change the standard output to the file we created.
		print(soup.prettify())
		
	sys.stdout = original_stdout # Reset the standard output to its original value
