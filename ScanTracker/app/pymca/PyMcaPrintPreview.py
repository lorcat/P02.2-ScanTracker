#/*##########################################################################
# Copyright (C) 2004-2012 European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
#
# This toolkit is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# PyMca is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# PyMca; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# PyMca follows the dual licensing model of Riverbank's PyQt and cannot be
# used as a free plugin for a non-free program.
#
# Please contact the ESRF industrial unit (industry@esrf.fr) if this license
# is a problem for you.
#############################################################################*/
import sys
from PyMca import PyMcaQt as qt

QTVERSION = qt.qVersion()
DEBUG = 0
if QTVERSION < '4.0.0':
    from PyMca.Q3PyMcaPrintPreview import PrintPreview
else:
    from app.pymca.Q4PyMcaPrintPreview import PyMcaPrintPreview as PrintPreview

#SINGLETON
if 0:
    #It seems sip gets confused by this singleton implementation
    class PyMcaPrintPreview(PrintPreview):
        _instance = None
        def __new__(self, *var, **kw):
            if self._instance is None:
                self._instance = PrintPreview.__new__(self,*var, **kw)
            return self._instance
else:
    #but sip is happy about this one
    class PyMcaPrintPreview(PrintPreview):
        _instance = None
        def __new__(self, *var, **kw):
            if self._instance is None:
                self._instance = PrintPreview(*var, **kw)
            return self._instance