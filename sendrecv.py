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
        # print('received message {} from app'.format(msg))
        if self.wait == True:
            # print('but waiting, so dropping it')
            return
        self.curr_msg = msg
        seg = Segment(msg, 'receiver', self.bit)
        # print('sending to network')
        self.send_to_network(seg)
        self.wait = True

        self.timer_bit = self.bit
        self.start_timer(5)

    def is_valid_ack(self, seg):
        return seg.msg == '<ACK>' and seg.bit == self.bit

    def receive_from_network(self, seg):
        # print('received {} from network'.format(seg.msg))
        if self.wait == True and (not seg.is_corrupt()) and self.is_valid_ack(seg):
            # print('getting out of wait, changing bits')
            self.wait = False
            self.bit = not self.bit
        else:
            # print('but its corrupt or not ACK or different bit, so resending')
            # print('sender bit: {}, ACK bit: {}, are we in wait? {}'.format(self.bit, seg.bit, self.wait))
            seg = Segment(self.curr_msg, 'receiver', self.bit)
            self.send_to_network(seg)

            self.timer_bit = self.bit
            self.start_timer(5)

    def on_interrupt(self):
        if self.timer_bit == self.bit:
            self.start_timer(5)
            # print('Times up and bit hasnt changed, resending')
            seg = Segment(self.curr_msg, 'receiver', self.bit)
            self.send_to_network(seg)
            return
        # print('Times up and bit has changed, moving on')

class AltReceiver(BaseReceiver):
    def __init__(self, bit=False):
        super(AltReceiver, self).__init__()
        self.bit = bit

    def receive_from_client(self, seg):
        # print('received message {} from client'.format(seg.msg))
        if seg.is_corrupt():
            # print('but is corrupt, so sending NAK')
            self.send_to_network(Segment('<NAK>', 'sender', self.bit))
        elif seg.bit != self.bit:
            # print('but is wrong bit, so resending ACK')
            self.send_to_network(Segment('<ACK>', 'sender', not self.bit))
        else:
            # print('and its ok, so sending to app, sending ACK and switching bit')
            self.send_to_app(seg.msg)
            self.send_to_network(Segment('<ACK>', 'sender', self.bit))
            self.bit = not self.bit

class GBNSender(BaseSender):
    # TODO: fill me in!
    pass

class GBNReceiver(BaseReceiver):
    # TODO: fill me in!
    pass
