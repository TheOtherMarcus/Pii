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
__version__ = "7"
__maintainer__ = "Marcus T. Andersson"

import pii

statements = []

# Entities have Identity
statements += pii.model("EntityE -- IdentityEScn1")

# Files have Path
statements += pii.model("FileE -- PathEScn1")

# Mutables can change content but Constants remain the same
statements += pii.model("MutableE -- ContentEEcnn -- ConstantE")
statements += pii.model("ConstantE -- ContentTypeEScn1")
statements += pii.model("ConstantE -- CreationTimeEScn1")
statements += pii.model("ConstantE -- ContentEBcn1")
statements += pii.model("ConstantE -- ShaEScn1")

# Embedded things are located in Containers
statements += pii.model("ContainerE -- EmbeddedEEc1n -- EmbeddedE")

# An Artifact can have Versions
statements += pii.model("ArtifactE -- VersionEEc1n -- VersionE")
statements += pii.model("VersionE -- VersionEScn1")

# A branch is both an Artifact and a Version

# Integrated things depend on external Modules to work correctly
statements += pii.model("IntegratedE -- ModuleEEcnn -- ModuleE")

# Copies have an Original
statements += pii.model("OriginalE -- CopyEEc1n -- CopyE")

# Composed things are built from parts and materials
statements += pii.model("ComposedE -- BoMPartEEc1n -- BoMPartE")
statements += pii.model("ComposedE -- BoMMaterialEEc1n -- BoMMaterialE")

# A BoM entry for a specific Part and how many of it
statements += pii.model("BoMPartE -- CountEIcn1")
statements += pii.model("BoMPartE -- PartEEcn1 -- PartE")

# A BoM entry for a specific Material and how much of it
statements += pii.model("BoMMaterialE -- AmountERcn1")
statements += pii.model("BoMMaterialE -- UnitEScn1")
statements += pii.model("BoMMaterialE -- MaterialEEcn1 -- MaterialE")

# Aggregates are built from Components (when you don't care about how many or how much)
statements += pii.model("AggregateE -- ComponentEEcnn -- ComponentE")

# A Manufactured thing is built with the help of Tools
statements += pii.model("ManufacturedE -- ToolEEcnn -- ToolE")

# A Work is created by following an Instruction
statements += pii.model("WorkE -- InstructionEEcnn -- InstructionE")

# An Electrical thing has a Schema
statements += pii.model("ElectricalE -- SchemaEEcnn -- SchemaE")

# A Mechanical thing has a Drawing
statements += pii.model("MechanicalE -- DrawingEEcnn -- DrawingE")

# Compiled things (e.g. software) has Source Code
statements += pii.model("CompiledE -- SourceCodeEEcnn -- SourceCodeE")

# A physical Item (e.g. my Toyota) is built using a Blueprint (e.g. Toyota Avensis 2006) 
statements += pii.model("BlueprintE -- ItemEEc1n -- ItemE")

# A batch of Items is both a Blueprint and an Item

# A Substrance is produced using a Recipe
statements += pii.model("RecipeE -- SubstanceEEc1n -- SubstanceE")
statements += pii.model("SubstranceE -- UnitEScn1")
statements += pii.model("SubstanceE -- AmountERcn1")

# A batch of Substance is both a Recipe and a Substance

# A Specification is realized in an Implementation and verified with a Test
statements += pii.model("SpecificationE -- ImplementationEEcnn -- ImplementationE")
statements += pii.model("SpecificationE -- TestEEcnn -- TestE")

# Performing a Test on an Implementation yields a TestResult
statements += pii.model("TestResultE -- ImplementationEEcn1 -- ImplementationE")
statements += pii.model("TestResultE -- TestEEcn1 -- TestE")

# A Guide tells you how to use an Appliance 
statements += pii.model("ApplianceE -- GuideEEcnn -- GuideE")

pii.execute(statements)
