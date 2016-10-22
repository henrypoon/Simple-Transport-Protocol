from socket import socket, AF_INET, SOCK_DGRAM, timeout
from sys import argv
#from common import ip_checksum
import random
import time
import threading
from packet import*
from header import*
from common import*
from controller import*

dest_addr = argv[1]
dest_port = int(argv[2])
dest = (dest_addr, dest_port)
listen_addr = '127.0.0.1'
listen_port = 1501
listen = (listen_addr, listen_port)
filename = argv[3]
MWS = int(argv[4])
MSS = int(argv[5])
timeout = float(argv[6])/(1000*1.0)
pdrop = float(argv[7])

COMPLETE = False
temp = 0
FRTcounter = 0
random.seed(int(argv[8]))
NODA = 0
RSBuffer = {}



class sender(object):
	"""docstring for main"""
	def __init__(self):
		super(sender, self).__init__()
		self.ack = 1
		self.packetList = []
		self.sender_socket = socket(AF_INET,SOCK_DGRAM)
		self.sender_socket.bind(listen)
		self.logFile = open("Sender_log.txt","w")
		self.totalSize = 0
		
		with open(filename) as Source:
			self.content = Source.read()
			self.totalSize = len(self.content)
		Source.close()

		self.iniTime = 0
		self.controller = controller(self.content,self.sender_socket,dest,self.logFile,MWS,MSS,timeout,pdrop)
		self.ISN = random.randint(0,1000)
		self.ISNR = 0		#save the ISN for receiver
		self.wavehand = False			
		self.begin()
	

	#begin program
	def begin(self):
###### start send function#######
		self.iniTime = time.time()
		self.controller.setIniTime(self.iniTime)
		self.TWHS()

		l1 = threading.Thread(target = self.listen, args = (self.sender_socket,dest))
		l1.daemon=True
		l1.start()



		s1 = threading.Thread(target = self.send, args = (self.sender_socket,))
		s1.daemon=True
		s1.start()

		#while True:

		o1 = threading.Thread(target = self.observer, args = ())
		o1.daemon=True
		o1.start()

	#three-way hand shake
	def TWHS(self):
			
			SYNsegment = packet(self.ISN,0,'',1,0)
			self.sender_socket.sendto(SYNsegment.encoded, dest)
			self.writeLOG("snd","S",self.ISN,0,0)
			SYNsegment.display()

			try:
				message, address = self.sender_socket.recvfrom(4096)
				print "Received " + message
			except timeout:

				pass
			else:

				decoded= []
				decoded = decode(message)
				receive_seq = int(decoded[0])
				receive_ack = int(decoded[2])
				receive_data = str(decoded[5])
				receive_syn = int(decoded[3])
				receive_fin = int(decoded[4])
				self.ISNR = receive_seq
				self.writeLOG("rcv","SA",receive_seq,0,receive_ack)
				ACKsegment = packet(receive_ack,receive_seq+1,'',0,0)
				self.sender_socket.sendto(ACKsegment.encoded, dest)
				self.writeLOG("snd","A",receive_ack,0,receive_seq+1)
				ACKsegment.display()
				self.controller.ini(receive_ack,self.ISNR)
		

	def listen(self,sender_socket,dest):
		global RSBuffer	
		global NODA	
		while self.wavehand == False:
			try:
				#sLock.acquire()
				#print "check"
				message, address = self.sender_socket.recvfrom(4096)
				print "Received " + message
				#self.logFile.write("in\n")

			except timeout:

				pass
			else:
				decoded= []
				decoded = decode(message)
				receive_seq = int(decoded[0])
				receive_ack = int(decoded[2])
				receive_data = str(decoded[5])
				receive_syn = int(decoded[3])
				receive_fin = int(decoded[4])
				#self.logFile.write("in\n")
				self.writeLOG("rcv","D",receive_seq,0,receive_ack)

				self.FRTdetect(receive_ack)
				self.wavehand = self.controller.GOTACK(receive_ack)
		#finally:
			#sLock.release()
			#self.listen(self.sender_socket,dest)
		print "complete"
	#	print self.totalSize + self.ISN + 1
		self.FIN()


	#ending method for finalise the program including close socket, close log file

	def FIN(self):
			global NODA
			FINsegment = packet(self.totalSize + self.ISN + 1,self.ISNR+1,'',0,1)
			self.sender_socket.sendto(FINsegment.encoded, dest)
			self.writeLOG("snd","F", self.totalSize + self.ISN + 1 ,0,self.ISNR)
			FINsegment.display()
			
			try:
				message, address = self.sender_socket.recvfrom(4096)
			except timeout:
				pass
			else:
				print "FIN " + message
				decoded= []
				decoded = decode(message)
				receive_seq = int(decoded[0])
				receive_ack = int(decoded[2])
				receive_data = str(decoded[5])
				receive_syn = int(decoded[3])
				receive_fin = int(decoded[4])
				self.writeLOG("rcv","FA",receive_seq,0,receive_ack)
				ACKsegment = packet(receive_ack,receive_seq+1,'',0,0)
				self.sender_socket.sendto(ACKsegment.encoded, dest)
				self.writeLOG("snd","A",receive_ack,0,receive_seq+1)
				ACKsegment.display()


			static = self.controller.getStatic()
			self.logFile.write("Amount of Data Transferred: " + str(self.totalSize)+"\n")
			self.logFile.write("Number of Data Segments Sent: " + str(static[0])+"\n")
			self.logFile.write("Number of Packets Dropped: " + str(static[1])+"\n")
			self.logFile.write("Number of Retransmitted Segments: " + str(static[2])+"\n")
			self.logFile.write("Number of Duplicate Acknowledgements received: " + str(static[3])+"\n")


			self.sender_socket.close()
			self.logFile.close()
			time.sleep(1)
			global COMPLETE
			COMPLETE = True
			self.sender_socket.close()
			print "TRANSMISSION COMPLETED!"

		


	def send(self, sender_socket):
		self.controller.sending()

	#start the observer in contronlled

	def observer(self):
		self.controller.observer()

	#fast retranmission detector


	def FRTdetect(self, receive_ack):
		global COMPLETE
		if COMPLETE == False:
			global temp
			global FRTcounter
			
			if temp == receive_ack:
				FRTcounter += 1
				if FRTcounter == 3:
					FRTcounter = 0
					timer = threading.Thread(self.controller.resend(temp,1))
					timer.start()
			else:
				FRTcounter = 0
				temp = receive_ack

	#write down log for the packets has been sent or recevied during the 
	#hand shack and disconnect

	def writeLOG(self,state,type,seq,size,ack):
		T = time.time()-self.iniTime
		roundTime = round(T,3)
		self.logFile.write(str(state)+"  "+str(roundTime)+"   "+str(type)+" "+str(seq)+" "+str(size)+"  "+str(ack)+"\n")




if __name__ == "__main__":
	sender()

	while COMPLETE == False:
		pass
