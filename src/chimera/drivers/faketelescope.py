#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# chimera - observatory automation system
# Copyright (C) 2006-2007  P. Henrique Silva <henrique@astro.ufsc.br>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import time
import random
import threading

from chimera.interfaces.telescopedriver import ITelescopeDriverSlew
from chimera.interfaces.telescopedriver import ITelescopeDriverSync
from chimera.interfaces.telescopedriver import ITelescopeDriverPark
from chimera.interfaces.telescopedriver import ITelescopeDriverTracking
from chimera.interfaces.telescopedriver import SlewRate

from chimera.core.chimeraobject         import ChimeraObject

from chimera.core.lock import lock

from chimera.util.coord    import Coord
from chimera.util.position import Position


class FakeTelescope (ChimeraObject,
                     ITelescopeDriverSlew,
                     ITelescopeDriverSync,
                     ITelescopeDriverPark,
                     ITelescopeDriverTracking):

    def __init__ (self):
        ChimeraObject.__init__(self)

        self.__slewing = False
        self._ra  = Coord.fromHMS("10:10:10")
        self._dec = Coord.fromDMS("20:20:20")
        self._az  = Coord.fromDMS(0)
        self._alt = Coord.fromDMS(10)

        self._slewing  = False
        self._tracking = True
        self._parked   = False
        
        self._abort = threading.Event()

    def __start__ (self):
        self.setHz(1.0/10)

    def open(self):
        pass

    def close(self):
        pass

    def ping(self):
        pass

    @lock
    def slewToRaDec(self, position):
        self.slewBegin(position)
        self._ra = position.ra
        self._dec = position.dec
        self._slewing = True
        self._abort.clear()

        t0 = time.time()
        while t0+5 < time.time():
            if self._abort.isSet(): return
            time.sleep(0.2)
            
        self.slewComplete(position)

    @lock
    def slewToAltAz(self, position):
        self.slewBegin(position)
        self._az = position.az
        self._alt = position.alt
        self._slewing = True
        time.sleep(3)
        self.slewComplete(position)

    def isSlewing (self):
        return self._slewing

    def abortSlew(self):
        self._abort.set()
        while self.isSlewing():
            time.sleep(0.1)

        self.abortComplete()

    @lock
    def moveEast(self, offset, rate=SlewRate.MAX):
        pass

    @lock
    def moveWest(self, offset, rate=SlewRate.MAX):
        pass

    @lock
    def moveNorth(self, offset, rate=SlewRate.MAX):
        pass

    @lock
    def moveSouth(self, offset, rate=SlewRate.MAX):
        pass

    def getRa(self):
        return self._ra

    def getDec(self):
        return self._dec

    def getAz(self):
        return self._az

    def getAlt(self):
        return self._alt

    def getPositionRaDec(self):
        return Position.fromRaDec(self.getRa(), self.getAz())

    def getPositionAzAlt(self):
        return Position.fromRaDec(self.getAz(), self.getAlt())

    def getTargetRaDec(self):
        return Position.fromRaDec(self.getRa(), self.getAz())

    def getTargetAzAlt(self):
        return Position.fromRaDec(self.getAz(), self.getAlt())

    def sync(self, position):
        self._ra  = position.ra
        self._dec = position.dec

    def park(self):
        self._parked = True

    def unpark(self):
        self._parked = False

    def isParked(self):
        return self._parked

    def setParkPosition (self, position):
        pass

    def startTracking (self):
        self._tracking = True
    
    def stopTracking (self):
        self._tracking = False

    def isTracking (self):
        return self._tracking