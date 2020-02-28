Dependencies
============

Python3 / virtualenv

```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```


User interface
==============

```
python win.py <inputimage> <width> <height> <scalefactor> <shapesfile>
```

E.g.:

```
python win.py orig.jpg 1047 785 1 shapes.txt
```


Render
======

```
python draw.py <width> <height> <shapesfile> <outimage>
```

E.g.:

```
python draw.py 10470 7850 shapes.txt art.png
```

