from sys import*
from socket import*
from header import*

class packet(object):
	"""docstring for packet"""
	def __init__(self, seq, ack, data,syn,fin):
		super(packet, self).__init__()
		self.data = data
		self.header = header(seq, ack, len(self.data),syn,fin)
		self.Dtype = 0;
		self.encoded = self.encode()

	def display(self):

		print str(self.header.seq) +" " + str(self.header.size)+" "+str(self.header.ack)+" "+str(self.header.syn)+" "+str(self.header.fin)


	def setType(self,Dtype):
		self.Dtype = Dtype


	def encode(self):
		encoded = str(self.header.seq) +"|SPLIT|" + str(self.header.size)+"|SPLIT|"+str(self.header.ack)+"|SPLIT|"+str(self.header.syn)+"|SPLIT|"+str(self.header.fin)+"|SPLIT|"+str(self.data)
		return encoded


