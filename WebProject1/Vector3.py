from numpy.ma.core import sqrt
import math

class Vector3(object):
	x = 0
	y = 0
	z = 0

	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	@staticmethod
	def Zero():
		return Vector3(0.0,0.0,0.0)    
    
	@staticmethod
	def Distance(p1, p2):
		return math.sqrt(math.pow(p2.x - p1.x, 2) + math.pow(p2.y - p1.y, 2) + math.pow(p2.z - p1.z, 2))