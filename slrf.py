import numpy
import scipy.signal
import scipy.interpolate
from matplotlib import pyplot as plt
from breezylidar import URG04LX 

def flags2segs(Flags, window):
	'''
	ARGUMENTS:
	 - Flags: 	a sequence of class flags (per time window)
	 - window:	window duration (in seconds)
	
	RETURNS:
	 - segs:	a sequence of segment's limits: segs[i,0] is start and segs[i,1] are start and end point of segment i
	 - classes:	a sequence of class flags: class[i] is the class ID of the i-th segment
	'''

	preFlag = 0
	curFlag = 0
	numOfSegments = 0

	curVal = Flags[curFlag]
	segsList = []
	classes = []
	while (curFlag<len(Flags)-1):
		stop = 0
	 	preFlag = curFlag
		preVal = curVal
	 	while (stop==0):
			curFlag = curFlag + 1
			tempVal = Flags[curFlag]
			if ((tempVal != curVal) | (curFlag==len(Flags)-1)): # stop
				numOfSegments = numOfSegments + 1
				stop = 1
				curSegment = curVal
				curVal = Flags[curFlag]
				segsList.append((curFlag*window))
				classes.append(preVal)
	segs = numpy.zeros ((len(segsList),2))

	for i in range(len(segsList)):
		if i>0:
			segs[i, 0] = segsList[i-1]
		segs[i, 1] = segsList[i]
	return (segs, classes)


def preProcess(angleRange, Scan):
	Scan = numpy.array(Scan)
	Scan = scipy.signal.medfilt(Scan, 5)
	Scan = scipy.signal.medfilt(Scan, 3)
	
	#f = scipy.interpolate.interp1d(angleRange, Scan, kind='cubic')
	
	I = Scan==0
			
	segs, classes = flags2segs(I, 1)
	Scan2 = numpy.copy(Scan)
	for i in range(1, segs.shape[0]-1):
		if classes[i]:	
			a1 = angleRange[segs[i-1,0]:segs[i-1,1]]
			a2 = angleRange[segs[i+1,0]:segs[i+1,1]]
			a1 = a1[-3::]
			a2 = a2[0:3]
			A = numpy.concatenate((a1, a2))
			b1 = Scan[segs[i-1,0]:segs[i-1,1]]
			b2 = Scan[segs[i+1,0]:segs[i+1,1]]
			b1 = b1[-3::]
			b2 = b2[0:3]
			B = numpy.concatenate((b1, b2))
			#f = scipy.interpolate.interp1d(A, B, kind='cubic')		
			f = scipy.interpolate.interp1d(A, B)
			Scan2[segs[i,0]: segs[i,1]] = f(angleRange[segs[i,0]: segs[i,1]])	
	Scan2[Scan2<0] = 0
	return Scan, Scan2

laser = URG04LX('/dev/ttyACM0') 

count = 0

angleRange = numpy.arange(-120, 120, 0.352)
print angleRange.shape

while True:
	count += 1
	Scan = laser.getScan()		
	Scan, Scan2 = preProcess(angleRange, Scan)
	
	X = numpy.cos(numpy.deg2rad(angleRange)) * Scan
	Y = numpy.sin(numpy.deg2rad(angleRange)) * Scan

	X2 = numpy.cos(numpy.deg2rad(angleRange)) * Scan2
	Y2 = numpy.sin(numpy.deg2rad(angleRange)) * Scan2

	
	plt.clf()
	plt.subplot(1,3,1)
	plt.plot(angleRange, Scan)
	plt.plot(angleRange, Scan2, 'r')
	plt.title(count)
	plt.ylim([0, 6000])
	
	plt.subplot(1,3,2)
	plt.plot(X, Y, '*')
	plt.xlim([-6000, 6000])
	plt.ylim([-6000, 6000])
	plt.axis('equal')
	
	plt.subplot(1,3,3)
	plt.plot(X2, Y2, '*')
	plt.xlim([-6000, 6000])
	plt.ylim([-6000, 6000])
	plt.axis('equal')

	plt.draw()
	plt.show(block=False)
