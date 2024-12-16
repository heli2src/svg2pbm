# svg2pbm

Python class for converting Scalable Vector Graphics (.svg) to Portable Bitmap (.pbm).

+ functions for convert ascii portable bitmap(type P1) to binary portable bitmap (type P4) or the other way round.

The portable bitmap format is the ideal format to write directly into a frambuffer(MONO_HLSB coding) in Micropython
for the display of a graphic on an black-white Epaper.
