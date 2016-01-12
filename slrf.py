import numpy
import scipy.signal
import scipy.interpolate
from matplotlib import pyplot as plt
from breezylidar import URG04LX 

def flags2segs(Flags, window):
    '''
    ARGUMENTS:
     - Flags:     a sequence of class flags (per time window)
     - window:    window duration (in seconds)
    
    RETURNS:
     - segs:    a sequence of segment's limits: segs[i,0] is start and segs[i,1] are start and end point of segment i
     - classes:    a sequence of class flags: class[i] is the class ID of the i-th segment
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
    Scan = scipy.signal.medfilt(Scan, 3)
    Scan = scipy.signal.medfilt(Scan, 5)
    
    #f = scipy.interpolate.interp1d(angleRange, Scan, kind='cubic')
    
    I = Scan==0
            
    segs, classes = flags2segs(I, 1)
    Scan2 = numpy.copy(Scan)    
    for i in range(1, segs.shape[0]-1):
        if classes[i]:    
            a1 = angleRange[segs[i-1,0]:segs[i-1,1]]
            a2 = angleRange[segs[i+1,0]:segs[i+1,1]]
            a1 = a1[-1::]
            a2 = a2[0:1]
            A = numpy.concatenate((a1, a2))
            b1 = Scan[segs[i-1,0]:segs[i-1,1]]
            b2 = Scan[segs[i+1,0]:segs[i+1,1]]
            b1 = b1[-1::]
            b2 = b2[0:1]
            B = numpy.concatenate((b1, b2))
            #f = scipy.interpolate.interp1d(A, B, kind='cubic')        
            f = scipy.interpolate.interp1d(A, B)
            Scan2[segs[i,0]: segs[i,1]] = f(angleRange[segs[i,0]: segs[i,1]])    
    Scan2[Scan2<0] = 0
    
    Scan2 = scipy.signal.medfilt(Scan2, 3)
    Scan2 = scipy.signal.medfilt(Scan2, 5)    
    
    return Scan, Scan2

laser = URG04LX('/dev/ttyACM0') 

count = 0

angleRange = numpy.arange(-120, 120, 0.352)
print angleRange.shape
plt.figure(figsize=(6*3.13,4*3.13))
while True:
    count += 1
    Scan = laser.getScan()        
    Scan, Scan2 = preProcess(angleRange, Scan)
    if count==1:
        diffScan = numpy.zeros(Scan.shape)        
        diffScan2 = numpy.zeros(Scan2.shape)        
    else:
        diffScan = numpy.abs(Scan - ScanPrev)
        diffScan2 = numpy.abs(Scan2 - ScanPrev2)
        diffScan = scipy.signal.medfilt(diffScan, 3)
        diffScan = scipy.signal.medfilt(diffScan, 15)
        diffScan2 = scipy.signal.medfilt(diffScan2, 3)
        diffScan2 = scipy.signal.medfilt(diffScan2, 15)
        
        
    X = numpy.cos(numpy.deg2rad(angleRange)) * Scan
    Y = numpy.sin(numpy.deg2rad(angleRange)) * Scan

    X2 = numpy.cos(numpy.deg2rad(angleRange)) * Scan2
    Y2 = numpy.sin(numpy.deg2rad(angleRange)) * Scan2

    
    plt.clf()    
    ax = plt.subplot(2,3,1)
    plt.plot(angleRange, Scan)
    plt.plot(angleRange, Scan2, 'r')
    plt.title(count)
    plt.ylim([-120, 120])
    plt.ylim([0, 6000])
    ax.set_ylim([0, 6000])    
    
    ax = plt.subplot(2,3,2, aspect='equal')
    plt.plot(X, Y, '*')
    ax.set_xlim([-3000, 3000])
    ax.set_ylim([-3000, 3000])
    
    ax = plt.subplot(2,3,3, aspect='equal')
    plt.plot(X2, Y2, '*')
    ax.set_xlim([-3000, 3000])
    ax.set_ylim([-3000, 3000])

    ax = plt.subplot(2,3,4)
    plt.plot(angleRange, diffScan)    
    plt.plot(angleRange, diffScan2, 'r')    
    plt.title(count)
    plt.ylim([-120, 120])
    plt.ylim([0, 6000])
    ax.set_ylim([0, 6000])    


    plt.draw()
    plt.show(block=False)
    ScanPrev = Scan
    ScanPrev2 = Scan2
