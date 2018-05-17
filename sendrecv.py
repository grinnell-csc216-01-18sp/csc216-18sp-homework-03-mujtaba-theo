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
    def __init__(self, msg, dst, bit=False, seqnum=0, syn=''):
        self.msg = msg
        self.dst = dst
        self.bit = bit
        self.seqnum = seqnum
        self.syn = syn

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
        self.requesting = False
        self.disallow_app_msgs()

    def is_valid_ack(self, seg):
        return seg.msg == '<ACK>' and seg.bit == self.bit

    def request_connection(self):
        seg = Segment('', 'receiver', syn='SYN')
        self.send_to_network(seg)
        self.start_timer(5)
        self.requesting = True

    def request_close(self):
        seg = Segment('', 'receiver', syn='FIN')
        self.send_to_network(seg)

    def receive_from_app(self, msg):
        self.curr_msg = msg
        seg = Segment(msg, 'receiver', bit=self.bit)
        self.send_to_network(seg)
        self.disallow_app_msgs()

        self.timer_bit = self.bit
        self.start_timer(5)

    def receive_from_network(self, seg):
        if seg.syn == 'SYNACK':
            seg = Segment('', 'receiver', syn='SYNFINAL')
            self.send_to_network(seg)
            self.requesting = False
            self.allow_app_msgs()
            self.end_timer()
            return
        elif seg.syn == 'FINACK':
            print('sender received FINACK, doing nothing?')
            # Do nothing?
            return
        elif seg.syn == 'FIN':
            print('sender received FIN, closing connection')
            seg = Segment('', 'receiver', syn='FINACK')
            self.send_to_network(seg)
            return

        if (not seg.is_corrupt()) and self.is_valid_ack(seg):
            self.allow_app_msgs()
            self.bit = not self.bit
            self.end_timer()
        else:
            seg = Segment(self.curr_msg, 'receiver', bit=self.bit)
            self.send_to_network(seg)

            self.timer_bit = self.bit
            self.start_timer(5)

    def on_interrupt(self):
        if self.requesting:
            self.request_connection()
            return
        self.start_timer(5)
        seg = Segment(self.curr_msg, 'receiver', bit=self.bit)
        self.send_to_network(seg)

class AltReceiver(BaseReceiver):
    def __init__(self, bit=False):
        super(AltReceiver, self).__init__()
        self.bit = bit
        self.requesting = False

    def request_close(self):
        seg = Segment('', 'sender', syn='FIN')
        self.send_to_network(seg)

    def receive_from_client(self, seg):
        if seg.syn == 'FINACK':
            print('receiver received FINACK, doing nothing?')
            # Do nothing?
            return
        elif seg.syn == 'FIN':
            print('receiver received FIN, closing connection')
            seg = Segment('', 'sender', syn='FINACK')
            self.send_to_network(seg)
            return
        elif seg.syn == 'SYN':
            seg = Segment('', 'sender', syn='SYNACK')
            self.send_to_network(seg)
            return
        elif seg.syn == 'SYNFINAL':
            return

        if seg.is_corrupt():
            self.send_to_network(Segment('<NAK>', 'sender', bit=self.bit))
        elif seg.bit != self.bit:
            self.send_to_network(Segment('<ACK>', 'sender', bit=not self.bit))
        else:
            self.send_to_app(seg.msg)
            self.send_to_network(Segment('<ACK>', 'sender', bit=self.bit))
            self.bit = not self.bit

class GBNSender(BaseSender):
    def __init__(self, app_interval, base=1, nextseq=1, N=5):
        super(GBNSender, self).__init__(app_interval)
        self.base = base
        self.nextseq = nextseq
        self.messages = {}
        self.N = N
        self.disallow_app_msgs()

    def request_connection(self):
        seg = Segment('', 'receiver', syn='SYN')
        self.send_to_network(seg)
        self.start_timer(5)
        self.requesting = True

    def request_close(self):
        seg = Segment('', 'receiver', syn='FIN')
        self.send_to_network(seg)

    def receive_from_app(self, msg):
        if self.nextseq >= self.base + self.N:
            self.disallow_app_msgs()
            return
        self.messages[self.nextseq] = msg
        seg = Segment(msg, 'receiver', seqnum=self.nextseq)
        self.send_to_network(seg)
        if self.base == self.nextseq:
            self.start_timer(5)
        self.nextseq = self.nextseq + 1

    def receive_from_network(self, seg):
        if seg.syn == 'SYNACK':
            seg = Segment('', 'receiver', syn='SYNFINAL')
            self.send_to_network(seg)
            self.requesting = False
            self.end_timer()
            self.allow_app_msgs()
            return
        elif seg.syn == 'FINACK':
            print('sender received FINACK, doing nothing?')
            # Do nothing?
            return
        elif seg.syn == 'FIN':
            print('sender received FIN, closing connection')
            seg = Segment('', 'receiver', syn='FINACK')
            self.send_to_network(seg)
            return

        if seg.is_corrupt() or seg.msg != '<ACK>':
            return
        self.base = seg.seqnum + 1
        if self.base == self.nextseq:
            self.end_timer()
            self.allow_app_msgs()
        else:
            self.start_timer(5)


    def on_interrupt(self):
        self.start_timer(5)
        for i in range(self.base, self.nextseq):
            msg = self.messages[i]
            seg = Segment(msg, 'receiver', seqnum=i)
            self.send_to_network(seg)



class GBNReceiver(BaseReceiver):
    def __init__(self, expected=1):
        super(GBNReceiver, self).__init__()
        self.expected = expected
        self.last_ack_num = 0

    def request_close(self):
        seg = Segment('', 'sender', syn='FIN')
        self.send_to_network(seg)

    def receive_from_client(self, seg):
        if seg.syn == 'FINACK':
            # Do nothing?
            print('receiver received FINACK, doing nothing?')
            return
        elif seg.syn == 'FIN':
            print('receiver received FIN, closing connection')
            seg = Segment('', 'sender', syn='FINACK')
            self.send_to_network(seg)
            return
        elif seg.syn == 'SYN':
            seg = Segment('', 'sender', syn='SYNACK')
            self.send_to_network(seg)
            return
        elif seg.syn == 'SYNFINAL':
            return

        if (not seg.is_corrupt()) and self.expected == seg.seqnum:
            self.send_to_app(seg.msg)
            last_ack = Segment('<ACK>', 'sender', seqnum=self.expected)
            self.send_to_network(last_ack)
            self.expected = self.expected + 1
            self.last_ack_num = self.last_ack_num + 1
        else:
            last_ack = Segment('<ACK>', 'sender', seqnum=self.last_ack_num)
            self.send_to_network(last_ack)
