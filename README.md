# covidmap
Automatically generated SVG US county maps of COVID data

Convert SVG images to animation with Imagemagick:

`convert -loop 1 -delay 20 -resize 600x600 -density 400 *_map.svg new-cases-500pop-sm.gif`
