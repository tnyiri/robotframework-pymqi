# robotframework-pymqi

RobotFramework PyMQI Library
=================================

|Build Status|

Short Description
-----------------

Robot Framework library for working with IBM MQ, using pymqi.

Installation
------------

::

    pip install robotframework-pymqi (coming soon)

Documentation
-------------

See keyword documentation for robotframework-pymqi library in
folder ``docs``.

Example
-------
+-----------+------------------+
| Settings  |      Value       |
+===========+==================+
|  Library  |     PyMQI        |
+-----------+------------------+

+---------------+---------------------------------------+--------------------+--------------------------+----------+
|  Test cases   |                  Action               |      Argument      |         Argument         | Argument |
+===============+=======================================+====================+==========================+==========+
|  Simple Test  | PyMQI.Connect In Client Mode          | 'DEV.APP.SVRCONN'  | '127.0.0.1'              | '1414'   |
+---------------+---------------------------------------+--------------------+--------------------------+----------+
|               | PyMQI.Purge Queue                     | 'TEST.SVC.REQEST'  |                          |          |
+---------------+---------------------------------------+--------------------+--------------------------+----------+
|               | PyMQI.Disconnect                      |                    |                          |          |
+---------------+---------------------------------------+--------------------+--------------------------+----------+

For more complex usage see 
    src/PyMQI_test.py    - pure python test suite
    src/PyMQI_test.robot - robotframework test suite

License
-------

Apache License 2.0

.. _Robot Framework: http://www.robotframework.org
.. _PyMQI: https://github.com/dsuch/pymqi
