# STP

Reliable transport protocol over the UDP protocol
STP will include most (but not all) of the features of TCP. Examples
of these features include timeout, ACK, sequence number, Fast Retransmission, Duplicate ACKed.

User will use your STP protocol to transfer simple text
(ASCII) files (examples provided on the assignment webpage) from the sender to the receiver. STP as two separate programs:
Sender and Receiver. You only have to implement unidirectional transfer of data from the Sender to 
the Receiver. Data segments will flow 
from Sender to Receiver while ACK segments will flow from Receiver to
Sender. 

How To Run

Sender :
python sender.py receiver_host_ip receiver_port file.txt MWS MSS timeout pdrop seed

Receiver :
python receiver.py receiver_port file.txt
