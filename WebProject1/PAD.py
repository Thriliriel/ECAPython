from Vector3 import Vector3
import math

class PAD(object):
	"""description of class"""
	#pleasure
	pleasure = 0
	#arousal
	arousal = 0
	#dominance
	dominance = 0
	#boredom
	boredom = 0
	#comfort zone
	comfortZone = Vector3.Zero()
	#possible emotions points in PAD (dict<string,Vector3>)
	padEmotions = {}

	def __init__(self, newPleasure, newArousal, newDominance):
		self.StartPADEmotions()
		self.boredom = 0

		self.pleasure = newPleasure
		self.arousal = newArousal
		self.dominance = newDominance

		self.comfortZone = Vector3(newPleasure,newArousal,newDominance)

	def StartPADEmotions(self):
		self.padEmotions['Neutral'] = Vector3.Zero()
		self.padEmotions['Joyful'] = Vector3(0.76, 0.48, 0.35)
		self.padEmotions['Friendly'] = Vector3(0.69, 0.35, 0.3)
		self.padEmotions['Happy'] = Vector3(0.81, 0.51, 0.46)
		self.padEmotions['Surprised'] = Vector3(0.4, 0.67, -0.13)
		self.padEmotions['Angry'] = Vector3(-0.51, 0.59, 0.25)
		self.padEmotions['Enraged'] = Vector3(-0.44, 0.72, 0.32)
		self.padEmotions['Frustrated'] = Vector3(-0.64, 0.52, 0.35)
		self.padEmotions['Fearful'] = Vector3(-0.64, 0.6, -0.43)
		self.padEmotions['Confused'] = Vector3(-0.53, 0.27, -0.32)
		self.padEmotions['Depressed'] = Vector3(-0.72, -0.29, -0.41)
		self.padEmotions['Bored'] = Vector3(-0.65, -0.62, -0.33)
		self.padEmotions['Sad'] = Vector3(-0.63, -0.27, -0.33)
		self.padEmotions['Disgust'] = Vector3(-0.60, 0.35, 0.11)

	#Assuming that the absence ofstimuli is responsible for the emergence of boredom (as proposed by [11]), 
    #the degreeof boredom starts to increase linearly over time
    #The linear increase of boredom can be described by the equation Z(t + 1) = Z(t) - b,
    #where the parameter b is again a personality-related aspect of the emotion system
	def IncreaseBoredom(self, O, C, A): #more boredom = less O, less C, less A. A-> more important
		#if max boredom is reached, just whatever
		if self.boredom <= -1:
			self.boredom = -1
			return

		#divide by 1000, so the max increment is 0.001
		pBore = ((0.25 * (O)) + (0.25 * (1-C)) + (0.5 * (1-A))) / 1000

		self.boredom -= pBore

	#reset boredom
	def ResetBoredom(self):
		self.boredom = 0

	#update the pad (for now, based only on what people say)
	def UpdatePAD(self, polarity, emotion = ""):
		if emotion == "":
			#P = (P + polarity) / 2
			#A = |polarity| + boredom
			#also, depending on the personality of the agent, it can travel more or less distance on PAD dimensions (farther or closer to the comfort zone). 
			#Sajjadi 2019 considered only the E from OCEAN, but we can try to do a bit more later
			actualDist = Vector3.Distance(Vector3(self.pleasure, self.arousal, self.dominance), self.comfortZone)

			oldArousal = self.arousal

			self.pleasure = (self.pleasure + polarity) / 2.0
			self.arousal = math.abs(polarity) + self.boredom
			if self.arousal > 1: 
				self.arousal = 1
			if self.arousal < -1: 
				self.arousal = -1

			newDist = Vector3.Distance(Vector3(self.pleasure, self.arousal, self.dominance), self.comfortZone)
			#means it is approaching comfort zone, so has bonus
			if newDist < actualDist:
				if polarity > 0: 
					self.pleasure += 0.05
				elif polarity < 0:
					self.pleasure -= 0.05

				if self.arousal < oldArousal:
					self.arousal -= 0.05
				elif self.arousal > oldArousal: 
					self.arousal += 0.05
			#otherwise, it is getting further from comfort zone. So, has penality.
			elif newDist > actualDist:
				if polarity > 0: 
					self.pleasure -= 0.05
				elif polarity < 0: 
					self.pleasure += 0.05

				if self.arousal < oldArousal: 
					self.arousal += 0.05
				elif self.arousal > oldArousal: 
					self.arousal -= 0.05
		else:
			#if we have a specific emotion, we change to it.
			if emotion == "Joy":
				emotion = "Happy"
			if emotion == "Sadness": 
				emotion = "Sad"

			pe = self.padEmotions[emotion]
			self.pleasure = pe.x
			self.arousal = pe.y
