class header(object):
	"""docstring for header"""
	def __init__(self, seq,ack,size,syn,fin):
		super(header, self).__init__()
		self.self = self
		self.seq = seq
		self.size = size
		self.ack = ack
		self.syn = syn
		self.fin = fin

