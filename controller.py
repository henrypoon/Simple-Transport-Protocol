from sys import*
from socket import*
from header import*
from packet import*
from common import*
import collections
import threading
import time
import random

#random.seed(50)
NOSS = 0
NOPD = 0
NORS = 0
NODA = 0
RSBuffer = {}
Total = 0




class controller(object):
	def __init__(self, content,socket,dest,logFile,MWS,MSS,timeout,pdrop):
		super(controller, self).__init__()
		self.MaxWS = MWS
		self.MaxSS = MSS
		self.content = content		#copy of the content
		self.sender_socket = socket
		self.dest = dest
		self.temp = 0			
		self.logFile = logFile
		self.senderBuffer = {}
		self.lastSend = 0
		self.lastAck = 0
		self.ISN = 0
		self.ISNR = 0
		self.finish = False
		self.iniTime = 0
		self.handleflag = False
		self.timeout = timeout
		self.LOSTRATE = pdrop


	def ini(self,ISN,ISNR):
		self.ISN = ISN
		self.ISNR = ISNR
		self.lastAck = ISN
		self.lastSend = ISN
		self.temp = ISN
		self.intTime = 0


	def getStatic(self):
		global NOSS
		global NOPD
		global NORS
		global NODA
		static = (NOSS,NOPD,NORS,NODA)
		return static


	def setIniTime(self,time):
		self.iniTime = time



	def GOTACK(self,receive_ack):

		global NODA
		global RSBuffer
		global Total
		if RSBuffer.has_key(receive_ack) == False:
			RSBuffer[receive_ack] = 1
		else:

			NODA += 1

		self.handleflag = True

		temp = 0
		#print len(self.senderBuffer)
		while self.senderBuffer.has_key(self.lastAck) == True:
			if receive_ack >= self.lastAck + len(self.senderBuffer[self.lastAck]):
				temp = self.lastAck
				self.lastAck += len(self.senderBuffer[self.lastAck])
				del self.senderBuffer[temp]
			else:
				break

	#	print len(self.senderBuffer)
		if self.lastAck >= self.ISN + len(self.content):
			self.finish = True

		self.handleflag = False
		print "test " + str(Total)
		return self.finish



	def sending(self):
		global NOSS
		while self.lastSend < len(self.content) + self.ISN and self.finish == False:
			#print "test" + str(self.lastSend)
			if self.handleflag == False:
			#	time.sleep(0.005)
			#	if len(self.WACK) < self.MaxWS:
				waitingACK = self.lastSend - self.lastAck
				if waitingACK <= self.MaxWS:
					if waitingACK != self.MaxWS:

						if self.MaxWS - waitingACK >= self.MaxSS:
							dataSize = self.MaxSS
						elif self.MaxWS - waitingACK < self.MaxSS:
							dataSize = self.MaxWS - waitingACK
					
						if self.lastSend + dataSize >= len(self.content) + self.ISN:
							print self.lastSend
							dataSize = len(self.content) + self.ISN - self.lastSend


						newPacket = packet(self.lastSend,self.ISNR,self.content[self.lastSend-self.ISN:self.lastSend+dataSize-self.ISN],0,0)	
						#self.WACK.append(newPacket)
						self.senderBuffer[self.lastSend] = self.content[self.lastSend-self.ISN:self.lastSend-self.ISN+dataSize]
					
						if self.lastSend == self.ISN:
							timer = threading.Timer(self.timeout,self.resend,args=(self.lastSend,0,))
							timer.start()
						NOSS += 1
						self.lastSend += dataSize
						self.PLD(newPacket)
		pass	



	#this method is used for resending packet and will check whether currnet base of slding windows
	# is equal to the packet that would to compare with previously. If they are the same, then resend,
	# call a new resend method afte two sec in the same way to check whether the packet still stay there
 	# And it starts running after the timeout. 
	

	def resend(self, seq ,mode):
		global NORS
		if seq <= len(self.content)+self.ISN and self.finish == False:
			if seq == self.lastAck:

				
				if mode == 0:
					print "Timeout " + str(seq)
				if mode == 1:
					print "Fast Retranmission"

				try:
					dataSize = len(self.senderBuffer[seq])
				except KeyError:
					pass
				else:

					newPacket = packet(seq,self.ISNR,self.content[seq-self.ISN:seq-self.ISN+dataSize],0,0)
					self.PLD(newPacket)
					NORS += 1
					timer = threading.Timer(self.timeout,self.resend,args=(seq,0,))
					timer.start()
		

	#this method is used to trigger(reset) a timer when 
	#sliding window moved

	def observer(self):
		while self.finish == False:
			if self.temp != self.lastAck:
				timer = threading.Timer(self.timeout,self.resend,args=(self.lastAck,0,))
				self.temp = self.lastAck
				timer.start()

	#this is the packet lost and delay modules


	def PLD(self,packet):		###packet lose and delay
		global Total
		global NOPD
		packet.display()
		pdrop = random.random()
		#print pdrop
		if pdrop > self.LOSTRATE:
			self.writeLOG("snd","D",packet.header.seq,packet.header.size,packet.header.ack)
		else:
			NOPD += 1
			self.writeLOG("drop","D",packet.header.seq,packet.header.size,packet.header.ack)			


		if pdrop > self.LOSTRATE:
			Total += 1
			self.sender_socket.sendto(packet.encoded, self.dest)
			
		
	#this method is used to write down the information on log file for
	#each packet that has been sent


	def writeLOG(self,state,type,seq,size,ack):
		T = time.time()-self.iniTime
		roundTime = round(T,3)
		self.logFile.write(str(state)+"  "+str(roundTime)+"   "+str(type)+"  "+str(seq)+" "+str(size)+"  "+str(ack)+"\n")
