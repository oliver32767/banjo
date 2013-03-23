:title Banjo
:tags banjo, python

Banjo is the software running this site.
It's written in Python and is a heavily-modified fork of Andrew Nelder's [Hobo](https://github.com/andrewnelder/hobo).
I chose Hobo as a starting point because it's a great little lightweight blog platform built on top of the excellent [Bottle.py](http://bottlepy.org) micro-http framework.
All of the content is stored in markdown in the filesystem, so it can easily be managed with git, making [Heroku](http://www.heroku.com) deployment a snap.
Some of the features I've added include:

* Support for syntax-highlighting in markdown's fenced code blocks
* Support for tags  
* A new Topic concept that gives me the ability to define sets of tags and an accompanying index page for each Topic.
Topics are arranged hierarchically, and defined similarly to how Hobo defines post content.

The source is available in [my GitHub repo](http://github.com/oliver32767/banjo).

