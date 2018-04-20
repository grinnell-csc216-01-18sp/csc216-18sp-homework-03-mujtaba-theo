##
# CSC 216 (Spring 2018)
# Reliable Transport Protocols (Homework 3)
#
# Sender-receiver code for the RDP simulation program.  You should provide
# your implementation for the homework in this file.
#
# Your various Sender implementations should inherit from the BaseSender
# class which exposes the following important methods you should use in your
# implementations:
#
# - sender.send_to_network(seg): sends the given segment to network to be
#   delivered to the appropriate recipient.
# - sender.start_timer(interval): starts a timer that will fire once interval
#   steps have passed in the simulation.  When the timer expires, the sender's
#   on_interrupt() method is called (which should be overridden in subclasses
#   if timer functionality is desired)
#
# Your various Receiver implementations should also inherit from the
# BaseReceiver class which exposes thef ollowing important methouds you should
# use in your implementations:
#
# - sender.send_to_network(seg): sends the given segment to network to be
#   delivered to the appropriate recipient.
# - sender.send_to_app(msg): sends the given message to receiver's application
#   layer (such a message has successfully traveled from sender to receiver)
#
# Subclasses of both BaseSender and BaseReceiver must implement various methods.
# See the NaiveSender and NaiveReceiver implementations below for more details.
##

from sendrecvbase import BaseSender, BaseReceiver

import Queue

class Segment:
    def __init__(self, msg, dst, bit=False):
        self.msg = msg
        self.dst = dst
        self.bit = bit

    def is_corrupt(self):
        return self.msg == '<CORRUPTED>'

def ack(bit=False):
    return Segment('<ACK>', 'sender', bit)

def nak(bit=False):
    return Segment('<NAK>', 'sender', bit)

class NaiveSender(BaseSender):
    def __init__(self, app_interval):
        super(NaiveSender, self).__init__(app_interval)

    def receive_from_app(self, msg):
        seg = Segment(msg, 'receiver')
        self.send_to_network(seg)

    def receive_from_network(self, seg):
        pass    # Nothing to do!

    def on_interrupt(self):
        pass    # Nothing to do!

class NaiveReceiver(BaseReceiver):
    def __init__(self):
        super(NaiveReceiver, self).__init__()

    def receive_from_client(self, seg):
        self.send_to_app(seg.msg)

class AltSender(BaseSender):
    def __init__(self, app_interval):
        super(AltSender, self).__init__(app_interval)
        self.bit = False
        self.wait = False

    def receive_from_app(self, msg):
        if self.wait == True:
            return
        self.curr_msg = msg
        seg = Segment(msg, 'receiver', self.bit)
        self.send_to_network(seg)
        self.wait = True

    def receive_from_network(self, seg):
        if self.wait == False or seg.is_corrupt() or seg.msg != '<ACK>':
            seg = Segment(self.curr_msg, 'receiver', self.bit)
            self.send_to_network(seg)
        else:
            self.wait = False
            self.bit = not self.bit

    def on_interrupt(self):
        pass


class AltReceiver(BaseReceiver):
    def __init__(self, bit=False):
        super(AltReceiver, self).__init__()
        self.bit = bit

    def receive_from_client(self, seg):
        if seg.is_corrupt():
            self.send_to_network(nak())
        elif seg.bit != self.bit:
            self.send_to_network(ack())
        else:
            self.send_to_app(seg.msg)
            self.send_to_network(ack())
            self.bit = not self.bit

class GBNSender(BaseSender):
    # TODO: fill me in!
    pass

class GBNReceiver(BaseReceiver):
    # TODO: fill me in!
    pass
