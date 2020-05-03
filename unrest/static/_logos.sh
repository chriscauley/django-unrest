convert logo-white-iris.png favicon.ico
convert logo-red-iris.png ur-f00.png
convert logo-red-iris.png -modulate 100,100,16.666 ur-08f.png
convert logo-red-iris.png -modulate 100,100,33.333 ur-00f.png
convert logo-red-iris.png -modulate 100,100,50.000 ur-80f.png
convert logo-red-iris.png -modulate 100,100,66.666 ur-f0f.png
convert logo-red-iris.png -modulate 100,100,83.333 ur-f08.png

convert logo-cyan-iris.png ur-0ff.png
convert logo-cyan-iris.png -modulate 100,100,16.666 ur-f80.png
convert logo-cyan-iris.png -modulate 100,100,33.333 ur-ff0.png
convert logo-cyan-iris.png -modulate 100,100,50.000 ur-8f0.png
convert logo-cyan-iris.png -modulate 100,100,66.666 ur-0f0.png
convert logo-cyan-iris.png -modulate 100,100,83.333 ur-0f8.png

for i in favicon.ico `ls ur-*.png`;
do
    convert $i \( +clone  -background white  -shadow 80x1+0+0 \) \
            +swap -background none -layers merge  +repage $i
done