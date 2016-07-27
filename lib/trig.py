import math


def deg2rad(d): return d/360.0*2*math.pi

def rad2deg(r): return int(r/2/math.pi*360.0)


rads = [deg2rad(d) for d in xrange(360)]
sins = [round(math.sin(r), 3) for r in rads]
coss = [round(math.cos(r), 3) for r in rads]
tans = [round(math.tan(r), 3) for r in rads]


def sin(deg): return sins[int(deg) % 360]

def cos(deg): return coss[int(deg) % 360]

def tan(deg): return tans[int(deg) % 360]


def boundPointToSize(p, s):
	x, y = p
	if x < 0: x = 0
	if y < 0: y = 0
	if x >= s[0]: x = s[0]
	if y >= s[1]: y = s[1]
	return typ.Point(x, y)


def test1():
	for d in xrange(360):
		print "%+.3f %+.3f" % (sin(d), cos(d)), "|",

