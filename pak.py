from ctypes import pointer
from email import header
from fileinput import filename
from posixpath import basename
from unicodedata import name
from binary_reader import BinaryReader
import sys
from pathlib import Path
import os
from re import search
import glob

Mypath = Path(sys.argv[1])
directory = str(Mypath.resolve().parent)
Myfilename = Mypath.name
w = BinaryReader()
w.set_endian(False)


unique_id = 0
if(Mypath.is_file()):
    path = Mypath.open("rb")
    reader = BinaryReader(path.read())
    reader.set_endian(False) # little endian
    magic = reader.read_str(4)
    filecount = reader.read_uint32()
    unk = reader.read_uint32()
    padding = reader.read_uint32()
    for i in range(filecount):
        pointer = reader.read_uint32()
        size = reader.read_uint32()
        filename = reader.read_str(24)
        print(filename)
        stay = reader.pos()
        reader.seek(pointer)
        output_path = directory / Path(Myfilename + ".unpack")
        output_path.mkdir(parents=True, exist_ok=True)
        slash = "\\"
        if (slash in filename):
            embeddedfolder = os.path.dirname(filename)
            output_path2 = directory / Path(Myfilename + ".unpack" + "\\" + embeddedfolder)
            output_path2.mkdir(parents=True, exist_ok=True)
        output_file = output_path / (filename)
        fe = open(output_file, "wb")
        fe.write(reader.read_bytes(size))
        fe.close()
        reader.seek(stay)
if (Mypath.is_dir()):
    newarchivename = sys.argv[1].replace('.unpack','')
    newarchive = open(newarchivename, "wb")
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(Mypath):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    print(len(listOfFiles))
    w.write_str_fixed("PAK",4)
    w.write_uint32(len(listOfFiles))
    fileoffset = (len(listOfFiles) * 32 + 16)
    w.write_uint32(fileoffset)
    w.write_uint32(0)
    headerseek = w.pos()
    w.align(fileoffset)
    w.seek(headerseek)
    for elem in listOfFiles:
        namefornewfile = elem.replace(sys.argv[1] + "\\", '')
        print(namefornewfile)
        arc = open(elem, "rb")
        stay = w.pos()
        w.seek(0,2)
        newfilepointer = w.pos()
        w.write_bytes(arc.read())
        w.seek(stay)
        w.write_uint32(newfilepointer)
        filesize = os.path.getsize(elem)
        w.write_uint32(filesize)
        w.write_str_fixed(namefornewfile,24)
    newarchive.write(w.buffer())