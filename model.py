#
# Product Information Index
#
# MIT License
#
# Copyright (c) 2020 Marcus T. Andersson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = "Marcus T. Andersson"
__copyright__ = "Copyright 2020, Marcus T. Andersson"
__credits__ = ["Marcus T. Andersson"]
__license__ = "MIT"
__version__ = "4"
__maintainer__ = "Marcus T. Andersson"

import pii

statements = []

statements += pii.model("EntityE -- IdentityEScn1")

statements += pii.model("FileE -- PathESc11")

statements += pii.model("ConstantE -- ContentTypeEScn1")
statements += pii.model("ConstantE -- CreationTimeEScn1")
statements += pii.model("ConstantE -- ContentEBcn1")
statements += pii.model("ConstantE -- ShaEScn1")

statements += pii.model("MutableE -- ContentEEc1n -- ConstantE")

statements += pii.model("ContainerE -- SectionEEc1n -- EmbeddedE")

statements += pii.model("ArtifactE -- VersionEEc1n -- VersionE")

pii.execute(statements)
