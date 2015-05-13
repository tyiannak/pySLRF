import numpy
import scipy.signal
from matplotlib import pyplot as plt
from breezylidar import URG04LX 
laser = URG04LX('/dev/ttyACM0') 

count = 0

angleRange = numpy.arange(-120, 120, 0.352)
print angleRange.shape

while True:
	count += 1
	Scan = laser.getScan()		
	Scan = numpy.array(Scan)
	Scan = scipy.signal.medfilt(Scan, 5)
	Scan = scipy.signal.medfilt(Scan, 3)
	
	X = numpy.cos(numpy.deg2rad(angleRange)) * Scan
	Y = numpy.sin(numpy.deg2rad(angleRange)) * Scan
	
	plt.clf()
	plt.subplot(1,2,1)
	plt.plot(angleRange, Scan)
	plt.title(count)
	plt.ylim([0, 6000])
	plt.subplot(1,2,2)
	plt.plot(X, Y, '*')
	plt.xlim([-5000, 5000])
	plt.ylim([-5000, 5000])
	plt.draw()
	plt.show(block=False)
