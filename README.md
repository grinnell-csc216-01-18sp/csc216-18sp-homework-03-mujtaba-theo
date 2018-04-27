# CSC 216 (Spring 2018) Homework 3

In this homework, you will implement the alternating-bit and go-back-N
reliable transport protocols discussed in class in the context of the
RTP simulation.

You should implement your protocols in `sendrecv.py`.  To run the
simulation, run `rtp.py`, *e.g.*,

~~~ {.console}
csc216-homework-03-starter $> python rtp.py -h
usage: rtp.py [-h] [--app-delay APP_DELAY] [--net-delay NET_DELAY]
              [--corr CORR_PROB] [--drop DROP_PROB]
              steps protocol

Simulates transportation layer network traffic.

positional arguments:
  steps                 number of steps to run the simulation
  protocol              protocol to use [naive|alt|gbn]

optional arguments:
  -h, --help            show this help message and exit
  --app-delay APP_DELAY
                        delay between application-level messages (default: 2)
  --net-delay NET_DELAY
                        network-level segment delay (default: 1
  --corr CORR_PROB      liklihood of segment corruption (default: 0.25)
  --drop DROP_PROB      likelihood of dropped packets (default: 0.0)
~~~

## Repository Information

* Theo Kalfas \[kalfasth\], Mujtaba Aslam \[aslammuj\]
* Python 2.7
* Nothing yet

### Notes

Special TCP packets, noted by their `syn` field, that are used to establish
and end connections are never dropped mainly due to the lack of a timer function
in the Receiver class. If `syn` packets sent by the Receiver were ever dropped
or corrupted, they would never be resent, since both parties are waiting.

Throughout the event loop of steps in the Simulation `run()` function, there's
a small probability of the connection closing by making a party send a `FIN` packet
to the other party, so as to test the closing of connections. The Sender and the
Receiver have an equal chance of being the party that initiates the end of the
connection.

Some code is repeated to make the implementation of the TCP-like opening and
closing of connections more clear.
