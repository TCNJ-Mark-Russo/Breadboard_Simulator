# Breadboard_Simulator
**TCNJ Engineering Breadboard Simulator**

Download all files.

Entire simulator is implemented in one file. To run simulator:

<pre>python board.py</pre>

Component proxies are designed to be drop-in replacements for MicroPython modules. Import as needed.

* `machine.py`
* `ssd1306.py`
* `lsm6dsox.py`

Standard Python does not have `sleep_ms()` and `ticks_ms()` functions. `time2.py` contains replacements. Import and use as necessary.
