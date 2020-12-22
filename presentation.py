"""
Product Information Index - Presentation

This file specifies how entity roles should be displayed. When an entity
have more than one role, the red, green and blue components for each role
are mixed together.

MIT License

Copyright (c) 2020 Marcus T. Andersson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__author__ = "Marcus T. Andersson"
__copyright__ = "Copyright 2020, Marcus T. Andersson"
__credits__ = ["Marcus T. Andersson"]
__license__ = "MIT"
__version__ = "15"
__maintainer__ = "Marcus T. Andersson"

import pii

statements = []

statements += pii.relate(["EntityE", "ShapeSS", "box"])

statements += pii.relate(["EntityE", "RedSI", 255])
statements += pii.relate(["EntityE", "GreenSI", 255])
statements += pii.relate(["EntityE", "BlueSI", 255])

statements += pii.relate(["ArtifactE", "RedSI", 128])
statements += pii.relate(["VersionE", "RedSI", 192])

statements += pii.relate(["MutableE", "BlueSI", 0])
statements += pii.relate(["ContainerE", "BlueSI", 64])
statements += pii.relate(["ConstantE", "BlueSI", 128])
statements += pii.relate(["EmbeddedE", "BlueSI", 192])

statements += pii.relate(["SpecificationE", "GreenSI", 128])
statements += pii.relate(["ImplementationE", "GreenSI", 192])

statements += pii.relate(["GitVersionE", "BlueSI", 64])

pii.execute(statements)
