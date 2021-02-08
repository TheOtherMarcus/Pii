"""
Product Information Index - Model

An entity can be many things and take on many roles. This file defines the
roles and relationships for a realistic Product Data Model (PDM). The model
is used by the presentation layer to search for and display relationships. It
does not prevent entities to be related in other ways as well.

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
__version__ = "2"
__maintainer__ = "Marcus T. Andersson"

import core

statements = []

# Entities have Identity
statements += core.model("EntityE -- LabelEScn1")
statements += core.model("EntityE -- IdentityEScn1")

# Files have Path
statements += core.model("FileE -- PathEScn1")

# Mutables can change content but Constants remain the same
statements += core.model("MutableE -- ContentEEcnn -- ConstantE")
statements += core.model("ConstantE -- ContentTypeEScn1")
statements += core.model("ConstantE -- CreationTimeEScn1")
statements += core.model("ConstantE -- ContentEBcn1")
statements += core.model("ConstantE -- ShaEScn1")

# Embedded things are located in Containers
statements += core.model("ContainerE -- EmbeddedEEcnn -- EmbeddedE")

# An Artifact can have Versions
statements += core.model("ArtifactE -- VersionEEc1n -- VersionE")
statements += core.model("VersionE -- VersionEScn1")

# A branch is both an Artifact and a Version

# Integrated things depend on external Modules to work correctly
statements += core.model("IntegratedE -- ModuleEEcnn -- ModuleE")

# Copies have an Original
statements += core.model("OriginalE -- CopyEEc1n -- CopyE")

# Composed things are built from parts and materials
statements += core.model("ComposedE -- BoMPartEEc1n -- BoMPartE")
statements += core.model("ComposedE -- BoMMaterialEEc1n -- BoMMaterialE")

# A BoM entry for a specific Part and how many of it
statements += core.model("BoMPartE -- CountEIcn1")
statements += core.model("BoMPartE -- PartEEcn1 -- PartE")

# A BoM entry for a specific Material and how much of it
statements += core.model("BoMMaterialE -- AmountERcn1")
statements += core.model("BoMMaterialE -- UnitEScn1")
statements += core.model("BoMMaterialE -- MaterialEEcn1 -- MaterialE")

# Aggregates are built from Components (when you don't care about how many or how much)
statements += core.model("AggregateE -- ComponentEEcnn -- ComponentE")

# A Manufactured thing is built with the help of Tools
statements += core.model("ManufacturedE -- ToolEEcnn -- ToolE")

# A Work is created by following an Instruction
statements += core.model("WorkE -- InstructionEEcnn -- InstructionE")

# An Electrical thing has a Schema
statements += core.model("ElectricalE -- SchemaEEcnn -- SchemaE")

# A Mechanical thing has a Drawing
statements += core.model("MechanicalE -- DrawingEEcnn -- DrawingE")

# Compiled things (e.g. software) has Source Code
statements += core.model("CompiledE -- SourceCodeEEcnn -- SourceCodeE")

# A physical Item (e.g. my Toyota) is built using a Blueprint (e.g. Toyota Avensis 2006) 
statements += core.model("BlueprintE -- ItemEEc1n -- ItemE")

# A batch of Items is both a Blueprint and an Item

# A Produce (uncountable products) is produced using a Recipe
statements += core.model("RecipeE -- ProduceEEc1n -- ProduceE")
statements += core.model("ProduceE -- UnitEScn1")
statements += core.model("ProduceE -- AmountERcn1")

# A batch of Produce is both a Recipe and a Produce

# A Specification is realized in an Implementation and verified with a Test
statements += core.model("SpecificationE -- ImplementationEEcnn -- ImplementationE")
statements += core.model("SpecificationE -- TestEEcnn -- TestE")

# Performing a Test on an Implementation yields a TestResult
statements += core.model("TestResultE -- ImplementationEEcn1 -- ImplementationE")
statements += core.model("TestResultE -- TestEEcn1 -- TestE")

# A Guide tells you how to use an Appliance 
statements += core.model("ApplianceE -- GuideEEcnn -- GuideE")

# A version in Git have additional properties.
statements += core.model("GitVersionE -- CommitEScn1")
statements += core.model("GitVersionE -- DateETcn1")
statements += core.model("GitVersionE -- CommentEBcn1")

# Graphical Presentation
statements += core.relate(["EntityE", "ShapeSS", "box"])

statements += core.relate(["EntityE", "RedSI", 255])
statements += core.relate(["EntityE", "GreenSI", 255])
statements += core.relate(["EntityE", "BlueSI", 255])

statements += core.relate(["ArtifactE", "RedSI", 128])
statements += core.relate(["VersionE", "RedSI", 192])

statements += core.relate(["MutableE", "BlueSI", 0])
statements += core.relate(["ContainerE", "BlueSI", 64])
statements += core.relate(["ConstantE", "BlueSI", 128])
statements += core.relate(["EmbeddedE", "BlueSI", 192])

statements += core.relate(["SpecificationE", "GreenSI", 128])
statements += core.relate(["ImplementationE", "GreenSI", 192])

statements += core.relate(["GitVersionE", "BlueSI", 64])

core.execute(statements)
