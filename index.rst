NUVE Violence Detection Documentation
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api_reference
   methodology
   ethics

Installation
------------
pip install -r requirements.txt

Quick Start
-----------
.. code-block:: python

   from src.detector import ViolenceDetector

   detector = ViolenceDetector()
   result = detector.analyze(text)

API Reference
-------------
.. automodule:: src.detector
   :members: