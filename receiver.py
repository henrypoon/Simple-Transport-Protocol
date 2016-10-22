from socket import socket, AF_INET, SOCK_DGRAM
from sys import argv, stdout
from packet import*
from header import*
from common import*
import time
import random

receiverBuffer = {}
logFile = open("Receiver_log.txt","w") 
iniTime = 0
NODR = 0
NODS = 0
NODA = 0
RSBuffer = {}
random.seed(50)


def writeLOG(state,type,seq,size,ack):
    global logFile
    global iniTime
    T = time.time()-iniTime
    roundTime = round(T,3)
 #   logFile.write(str(state)+"  "+str(type)+"  "+str(seq)+" "+"   "+str(size)+"    "+str(ack)+"\n")
    logFile.write(str(state)+"  "+str(roundTime)+"   "+str(type)+"  "+str(seq)+" "+str(size)+"  "+str(ack)+"\n")

def search(receive_seq, content):
    global receiverBuffer
    global NODR
   # result = []
   # preSize = receiverBuffer[receive_seq]
    preSize = len(content)
    tempSeq = receive_seq + preSize
 #   first = True

    file.write(content)
    NODR += preSize
    #stdout.write(content)
    #time.sleep(0.5)
    while receiverBuffer.has_key(tempSeq) == True:
        #stdout.write(receiverBuffer[tempSeq])
        preSize = len(receiverBuffer[tempSeq])
        NODR += preSize
        file.write(receiverBuffer[tempSeq])
        del receiverBuffer[tempSeq]
        tempSeq = preSize + tempSeq

    ack = tempSeq
    return ack




if __name__ == "__main__":
    file = open(argv[2],"w")

    listen_addr = '127.0.0.1'
    listen_port = int(argv[1])
    listen = (listen_addr, listen_port)

    receiver_socket = socket(AF_INET, SOCK_DGRAM)
    receiver_socket.bind(listen)
    ISN = random.randint(0,1000)
    expecting_seq = 0
    ack = ISN + 1
    FinFlag = False
    Complete = False  
    print "Ready for receving"

    iniTime = time.time()
    while Complete == False:
      #  print "Start Receving"

        try:
            message, address = receiver_socket.recvfrom(4096)
            NODS += 1
        except timeout:
            pass
        else:
            dest_addr = address[0]
            dest_port = address[1]
            dest = (dest_addr, dest_port)
         #   print address
            decoded = []
            decoded = decode(message)
            receive_seq = int(decoded[0])
            receive_ack = int(decoded[2])
            receive_content = str(decoded[5])
            receive_syn = int(decoded[3])
            receive_fin = int(decoded[4])


            if RSBuffer.has_key(receive_seq) == False:
                RSBuffer[receive_seq] = 1
            else:
                print receive_seq
                NODA += 1
            
            
            #print decoded

            #print FinFlag
            if receive_syn == 1:
                NODS -= 1
                writeLOG("rcv","S",receive_seq,0,receive_ack)
                SYNACK = packet(ISN,receive_seq+1,'',1,0)
                send(receiver_socket,SYNACK,dest)
                writeLOG("snd","SA",ISN,0,receive_seq+1)
            elif receive_ack == ISN + 1 and len(receive_content) == 0 and receive_fin == 0:
                NODS -= 1
                expecting_seq = receive_seq
                writeLOG("rcv","A",receive_seq,0,receive_ack)

            elif receive_fin == 1:
                NODS -= 1
                writeLOG("rcv","F",receive_seq,0,receive_ack)
                FINACK = packet(receive_ack,receive_seq+1,'',0,1)
                #print receive_ack
               # FINACK.display()
                send(receiver_socket,FINACK,dest)
                FinFlag = True
                writeLOG("snd","FA",receive_ack,0,receive_seq+1)
                

            elif FinFlag == True:
                NODS -= 1
                send(receiver_socket,SYNACK,dest)
                writeLOG("rcv","A",receive_ack,0,receive_seq)

                Complete = True
               # print Complete
            
            else:
                writeLOG("rcv","D",receive_seq,len(receive_content),receive_ack)
                if receive_seq == expecting_seq:
                 #   print "check"
                    new_ack = search(receive_seq,receive_content)
                    new_seq = receive_ack
                    newpacket = packet(new_seq,new_ack,'',0,0)
                    send(receiver_socket,newpacket,dest)
                    writeLOG("snd","A",new_seq,len(receive_content),new_ack)
                    expecting_seq = new_ack
                    ack = receive_ack

                else:
                    if receiverBuffer.has_key(receive_seq) == True:
                        pass
                    else:
                        receiverBuffer[receive_seq] = receive_content
                    newpacket = packet(ack,expecting_seq,'',0,0)
                    send(receiver_socket,newpacket,dest)
                    writeLOG("snd","A",receive_ack,len(receive_content),expecting_seq)
    
    print "TRANSMISSION COMPLETED"
    logFile.write("Amount of Data Received: " + str(NODR)+"\n")
    logFile.write("Number of Data Segments Received: " + str(NODS)+"\n")
    logFile.write("Number of duplicate segments received: " + str(NODA-1)+"\n")
    receiver_socket.close()
    logFile.close()