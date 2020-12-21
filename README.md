# Pii - Product Information Index

Read the introduction at https://formallanguage.blogspot.com/2020/11/product-information-index-pii.html

Pii is a PDM (Product Data Management) system. The killer feature of Pii is its method to automatically collect product information from primary sources (documents, files, databases, source control) and make it searchable/browseable. This makes Pii easy to integrate with your existing tools and processes. Search reports are presented as interactive graphs that can be further explored. Traditional PDM systems typically acts as the master record keeper and manual data entry is the norm. It is common that such systems quickly get out of sync with reality.

Even though the focus of this repo is product data modeling, the core pii.py/pii.js implementation does not depend on any particular data model. You can choose to model any type of data by changing model.py, presentation.py and tracker.py.

To integrate Pii with your product development you need to change tracker.py. The example implementation of tracker.py found here extracts information about the Pii product itself found in the files in this repo. The queries q_files.py, q_spec.py and q_no_implementation.py are starting points for the graphical browser.

For a quick start, run the following commands.

```bash
$ python model.py
$ python presentation.py
$ python tracker.py
$ python q_files.py
```

In the graph that opens in your browser, double click on a node to expand or contract it. Double click on an edge to remove all edges with that name. ALT-Click will open content in nodes with dashed border. Remove all selected nodes and edges with the trash can.
