.. _changes:

Changes
=======

0.9.1 - 2021-07-05
------------------

- Use half-open intervals for time ranges
- Create appropriate QoS profiles for latched topics in converted bags
- Fix return value tuple order of messages() in documentation `#2`_
- Add type hints to message classes
- Remove non-default ROS2 message types
- Support multi-line comments in idl files
- Fix parsing of msg files on non-POSIX platforms `#4`_

.. _#2: https://gitlab.com/ternaris/rosbags/issues/2
.. _#4: https://gitlab.com/ternaris/rosbags/issues/4

0.9.0 - 2021-05-16
------------------

- Initial Release
