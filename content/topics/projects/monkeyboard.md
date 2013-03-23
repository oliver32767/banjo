:title MonkeyBoard
:tags monkeyboard

MonkeyBoard is being developed with the goal of being a lightweight, pluggable Android managment application.
It was inspired by an earlier prototype I built, which used some of the Android SDK
libraries to connect to Android devices and allow me to send keystrokes from my computer keyboard to a connected android device.

The current goal is to build a powerful, minimal and flexible api that will allow
other folks to write plugins for a heavily-customizable gui.
The gui is based on [Docking Frames](https://github.com/Benoker/DockingFrames),
which is essentially a lightweight version of Eclipse's SWT layout engine.

Plugins will be able to interact with ddmlib IDevice instances and ChimpChat AdbChimpDevice instances
(ChimpChat being the internal Java library that
[MonkeyRunner](http://developer.android.com/tools/help/monkeyrunner_concepts.html) is built upon).
The host application will take care of threading and scheduling tasks,
so plugin writers can focus on building neat ways to interact with devices instead of the low-level adb/device managment.

Planned Features:

* Keyboard binding, similar to the prototype.
* APK managment. Inspect installed packages, install, update, and remove packages,
as well as inspecting .apk files.
* Screenshots and crash reports
* Ability to view simultaneous logcats from different devices.
* Performance monitoring
* Process/thread managment
* Clipboard managment