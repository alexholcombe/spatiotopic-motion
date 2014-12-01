[Szinte & Cavanagh 2011](http://www.journalofvision.org/content/11/2/4.short) E2, apparent motion, implemented with [Psychopy](https://github.com/psychopy/psychopy)
============================
Licensing: MIT license, which is like CC-BY for code.

Jedi- ~~Jr.~~ Master Chris Fajou programmed initial version in October 2014. Thank you Chris!

**dots.py** - Szinte & Cavanagh E2

**dotLocalize.py** - control experiment. Localize individual dot presentation before and after saccade. Or if you happen to have palinopsia, localize the afterimage.

##Szinte & Cavanagh E2 stimulus details
"gray background", luminance not specified.

First, target dot left->right->left->right (or the opposite direction) so participant gets their eye movements in the swing of things. 600ms each location.

1. 100 ms target and foil dot alone.
2. Black dot added, on for 400 ms
3. Black dot disappears, target and foil dot alone for 100 ms
4. Target and foil dot exchange places, 100 ms
5. Black dot appears in second location, 400 ms
6. Target and foil dot alone, for 100 ms

Only 100 ms after the saccade target moves, the probe appears. This provides little margin of error in saccade timing! In fact according to their eyetracker, participants were only on time in about 68% of trials (usually early rather than late). So I want to lengthen to 200ms, effect is still strong in me.

They had no jitter of any locations, and tested only 3, which was probably not a good idea because it means seeing the second location is enough to know the right answer. So I  add jitter to the first location (and apply the same jitter value to the second location).
