#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from Framework.apps.ambient import Ambient  # Als Elternklasse für die App
from Framework.theme import theme  # Um auf Themes zuzugreifen

import time
import colorsys
import multiprocessing
import Queue # needed to match Queue.Empty exception
import pcap
import binascii
from pcapfile.protocols.linklayer import ethernet
from pcapfile.protocols.network import ip


def ip_to_int(ipv4_string):

    octets = ipv4_string.split('.')
    binary_string = '' # string depicting the ip address in binary
    
    for octet in octets:

        octet = int(octet)
        binary_string += bin(octet)[2:].rjust(8, '0')

    return int(binary_string, 2)

#IP_LIMIT = ip_to_int('10.0.3.255')
IP_LIMIT = ip_to_int('255.255.255.255')


class Color(object):

    red = None
    green = None
    blue = None

    hue = None
    saturation = None
    value = None

    alpha = None

    def __init__(self, red=None, green=None, blue=None, hue=None, saturation=None, value=None, alpha=None):

        rgb_passed = bool(red)|bool(green)|bool(blue)
        hsv_passed = bool(hue)|bool(saturation)|bool(value)

        if not alpha:
            alpha = 1.0

        if rgb_passed and hsv_passed:
            raise ValueError("Color can't be initialized with RGB and HSV at the same time.")

        elif hsv_passed:

            if not hue:
                hue = 0.0
            if not saturation:
                saturation = 0.0
            if not value:
                value = 0.0

            super(Color, self).__setattr__('hue', hue)
            super(Color, self).__setattr__('saturation', saturation)
            super(Color, self).__setattr__('value', value)
            self._update_rgb()

        else:

            if not red:
                red = 0
            if not green:
                green = 0
            if not blue:
                blue = 0

            super(Color, self).__setattr__('red', red)
            super(Color, self).__setattr__('green', green)
            super(Color, self).__setattr__('blue', blue)
            self._update_hsv()

        super(Color, self).__setattr__('alpha', alpha)


    def __setattr__(self, key, value):

        if key in ('red', 'green', 'blue'):
            if value > 255.0:
                value = value % 255.0
            super(Color, self).__setattr__(key, value)
            self._update_hsv()

        elif key in ('hue', 'saturation', 'value'):
            if key == 'hue' and (value >= 360.0 or value < 0):
                value = value % 360.0
            elif key != 'hue' and value > 1.0:
                value = 1.0
            super(Color, self).__setattr__(key, value) 
            self._update_rgb()

        else:
            if key == 'alpha' and value > 1.0: # TODO: Might this be more fitting in another place?
                value = 1.0

            super(Color, self).__setattr__(key, value)


    def __repr__(self):

        return '<%s: red %f, green %f, blue %f, hue %f, saturation %f, value %f, alpha %f>' % (
                self.__class__.__name__,
                self.red,
                self.green,
                self.blue,
                self.hue,
                self.saturation,
                self.value,
                self.alpha
            )


    def __str__(self):
        return "%d %d %d" % (
            int(round(self.red * self.alpha)),
            int(round(self.green * self.alpha)),
            int(round(self.blue * self.alpha)),
        )


    def blend(self, other, mode='normal'):

        if self.alpha != 1.0: # no clue how to blend with a translucent bottom layer
            self.red = self.red * self.alpha
            self.green = self.green * self.alpha
            self.blue = self.blue * self.alpha

            self.alpha = 1.0

        if mode == 'normal':
            own_influence = 1.0 - other.alpha
            self.red = (self.red * own_influence) + (other.red * other.alpha)
            self.green = (self.green * own_influence) + (other.green * other.alpha)
            self.blue = (self.blue * own_influence) + (other.blue * other.alpha)


    def lighten(self, other):

        if isinstance(other, int) or isinstance(other, float):
            other = Color(red=other, green=other, blue=other, alpha=1.0)

        if self.alpha != 1.0:
            self.red = self.red * self.alpha
            self.green = self.green * self.alpha
            self.blue = self.blue * self.alpha

            self.alpha = 1.0

        red = self.red + (other.red * other.alpha)
        green = self.green + (other.green * other.alpha)
        blue = self.blue + (other.blue * other.alpha)

        if red > 255.0:
            red = 255.0

        if green > 255.0:
            green = 255.0

        if blue > 255.0:
            blue = 255.0

        self.red = red
        self.green = green
        self.blue = blue


    def darken(self, other):

        if isinstance(other, int) or isinstance(other, float):
            other = Color(red=other, green=other, blue=other, alpha=1.0)

        red = self.red - other.red
        green = self.green - other.green
        blue = self.blue - other.blue

        if red < 0:
            red = 0

        if green < 0:
            green = 0

        if blue < 0:
            blue = 0

        self.red = red
        self.green = green
        self.blue = blue

    
    def hex(self):
        return "%.2X%.2X%.2X" % (self.red, self.green, self.blue)

    def _update_hsv(self):

        hue, saturation, value = colorsys.rgb_to_hsv(self.red/255.0, self.green/255.0, self.blue/255.0)
        super(Color, self).__setattr__('hue', hue * 360.0)
        super(Color, self).__setattr__('saturation', saturation)
        super(Color, self).__setattr__('value', value)


    def _update_rgb(self):

        red, green, blue = colorsys.hsv_to_rgb(self.hue / 360.0, self.saturation, self.value)
        super(Color, self).__setattr__('red', red * 255.0)
        super(Color, self).__setattr__('green', green * 255.0)
        super(Color, self).__setattr__('blue', blue * 255.0)


class Capture(multiprocessing.Process):

    queue = None
    started = None

    def __init__(self, queue):

        super(Capture, self).__init__()
        self.daemon = True
        self.queue = queue
        self.started = False


    def start(self):

        print "ACTUAL WORKER START"
        super(Capture, self).start()
        self.started = True

    
    def run(self):
            
        for time, buf in pcap.pcap(promisc=True, immediate=True):

            eth_frame = ethernet.Ethernet(buf)
            try:
                ip_packet = ip.IP(binascii.unhexlify(eth_frame.payload))
            except AssertionError:
                continue # ignore this packet

            self.queue.put({
                #'vhl': ip_packet.vhl,
                'tos': ip_packet.tos,
                'len': ip_packet.len,
                'id': ip_packet.id,
                'off': ip_packet.off,
                'ttl': ip_packet.ttl,
                'p': ip_packet.p,
                'sum': ip_packet.sum,
                'src': ip_packet.src,
                'dst': ip_packet.dst
            })


class Network(Ambient):

    queue = None
    capture = None
    min_addr = None
    max_addr = None

    src_color = Color(red=0, green=255, blue=128)
    dst_color = Color(red=255, green=0, blue=128)


    def __init__(self, matrix, parent):

        super(Network, self).__init__(matrix, parent)
        print "NETWORK INIT"
        self.queue = multiprocessing.Queue(maxsize=2)
        #self.queue = Queue.LifoQueue(maxsize=1)
        self.capture = Capture(self.queue)
        #self.max_addr = 4294967295 # uint32 maximum size
        
        if not self.capture.started:
            print "WORKER START"
            self.capture.start()

    def self_self_update(self, keys_down):
        self.last_keys_down = self.keys_down
        self.keys_down = keys_down

        self.loop()

        time.sleep(0.02)


    def loop(self):
 
        # Frame leeren:
        #self.clear()
        for x in range(0, 35):
            for y in range(0,20):

                px = self.frame[y, x]
                col = Color(red=px[0], green=px[1], blue=px[2])
                col.value = col.value * 0.95

                self.frame[y, x] = (col.red, col.green, col.blue)
        
    	# Tastenabfragen:
        # Tasten: "A", "B", "X", "Y", "START", "SELECT", "UP", "DOWN", "LEFT", "RIGHT"
        if self.is_key_down("B"): pass  # Beim drücken der Taste
        if self.is_key_pressed("B"): pass  # Bei anhaltendem Tastendruck
        if self.is_key_up("B"): pass  # Beim lösen der Taste
        
        # Zum Menu zurückkehren:
        if self.is_key_up("B"):
        	self.parent.back()

        try:
            packet_info = self.queue.get_nowait()

            if ip_to_int(packet_info['src']) <= IP_LIMIT and ip_to_int(packet_info['dst']) <= IP_LIMIT:

                if self.min_addr is None:
                    self.min_addr = ip_to_int(packet_info['src'])
                elif self.max_addr is None:
                    self.max_addr = ip_to_int(packet_info['src'])

                if ip_to_int(packet_info['src']) > self.max_addr:
                    self.max_addr = ip_to_int(packet_info['src'])

                if ip_to_int(packet_info['src']) < self.min_addr:
                    self.min_addr = ip_to_int(packet_info['src'])
               
                if ip_to_int(packet_info['dst']) > self.max_addr:
                    self.max_addr = ip_to_int(packet_info['dst'])

                if ip_to_int(packet_info['dst']) < self.min_addr:
                    self.min_addr = ip_to_int(packet_info['dst'])


                src_coord = self.coord(ip_to_int(packet_info['src']))
                dst_coord = self.coord(ip_to_int(packet_info['dst']))

                src_current = Color(red=self.frame[src_coord][0], green=self.frame[src_coord][1], blue=self.frame[src_coord][2])
                dst_current = Color(red=self.frame[dst_coord][0], green=self.frame[dst_coord][1], blue=self.frame[dst_coord][2])
                src_current.lighten(self.src_color)
                dst_current.lighten(self.dst_color)

                self.frame[src_coord] = (src_current.red, src_current.green, src_current.blue)
                self.frame[dst_coord] = (dst_current.red, dst_current.green, dst_current.blue)

        except Queue.Empty:
            pass # no packets = no updates besides fade


    def coord(self, addr):

        addr_range = self.max_addr - self.min_addr +1
        display_range = 35 * 20

        addr_offset = addr - self.min_addr

        pos = display_range * (addr_offset / float(addr_range))

        x = int(pos // 35) 
        y = int(pos % 35) 

        return x, y
