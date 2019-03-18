How to generate new resources.py file from resources.qrc after adding resources in Qt Designer:

cd /home/pi/pyano-git/resources

pyrcc4 -o resources.py resources.qrc -py3

