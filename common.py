def send(sender_socket,packet,dest):
    sender_socket.sendto(packet.encoded, dest)

def decode(message):
	headerList = []
	headerList = message.split('|SPLIT|',6)
	return headerList
