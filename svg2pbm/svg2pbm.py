#
# Released under the MIT License (MIT). See LICENSE.
#

import cairosvg                # conda install cairosvg
import wx                      # conda install wxpython
import os


class SVG2pbm(wx.Frame):
    """Convert Scalable Vector Graphics (.svg) to Portable Bitmap (.pbm).

    + functions for convert ascii portable bitmap(type P1) to binary portable bitmap (type P4) or the other way round.
    """

    BINOFFSET = 6

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.inpath = '.'
        self.outpath = '.'

    def loadpbm(self, filename):
        """
        Load  ASCII/Binary Portable Bitmap into a string(=ascii)

        Parameters
        ----------
        filename : str
            path and name from the file.

        Returns
        -------
        mode, databuffer, width, height
            mode: type of data 'P1' or 'P4'
            databuffer: bytearry from the data
            width  : width form the image
            height : height form the image

        """
        with open(filename, "rb") as f:
            mode = f.readline()[:-1].decode('ascii')  # Magic number
            f.readline()                     # Creator comment   TODO: this is not really ok yet, because every line starting with # can be a comment
            dim = f.readline()[:-1]
            w, h = dim.split(' ') if type(dim) is str else dim.decode('ascii').split(' ')    # Dimensions
            data = bytearray(f.read())
        if mode == 'P1':
            data = "".join(data.decode('ascii').split('\n'))
        elif mode == 'P4':
            data = self.bin2ascii(data, int(w))
        else:
            raise Exception(f"unknown format from file {filename}")
        return mode, data, int(w), int(h)

    def bin2ascii(self, bytebuffer, width):
        """convert a Binary Portable Bitmap to ASCII Portable Bitmap"""
        buffer = ""
        refiller = 8 - (int(width) % 8)
        for index in range(0, len(bytebuffer)):
            buffer += f'{bytebuffer[index]:08b}'
        asciibuffer = ""
        for col in range(0, len(buffer), width + refiller):
            asciibuffer += buffer[col: col+width]
        return asciibuffer

    def ascii2bin(self, asciibuffer, width):
        """convert ASCII Portable Bitmap to Binary Portable Bitmap"""
        refiller = 8 - (width % 8)
        rbuffer = ""
        for col in range(0, len(asciibuffer), width):
            rbuffer += asciibuffer[col: col+width] + f'{0:0{refiller}b}'

        cnt = 0
        binbuffer = bytearray()
        while True:
            if cnt >= len(rbuffer):
                break
            byte = rbuffer[cnt:cnt+8]
            binbuffer.append(int(byte, 2))
            cnt += 8
        return binbuffer

    def img2pbm_ascii(self, imgbuffer, width):
        """
        Convert the wx image buffer to a ASCII Portable Bitmap.

        see https://de.wikipedia.org/wiki/Portable_Anymap
        """
        buffer = ""
        for index in range(0, len(imgbuffer), 3):    # each pixel has a 8bit rgb value
            bit = 0 if imgbuffer[index] > 1 else 1
            buffer += str(bit)
        return buffer

    def write_pbm(self, filenname, buffer, width, height, mode):
        """
        Write buffer to filename.

        Parameters
        ----------
        filenname : str
            path and filename without extension.
        buffer : bytearray
            the image in ascci or binary portable bitmap .
        width : int
            width from the image.
        height : int
            height from the image.
        mode : str
            "bin" or "ascii"

        Returns
        -------
        None.

        """
        if not os.path.isdir(self.outpath):
            os.mkdir(self.outpath)
        with open(f"{self.outpath}/{filenname}.pbm", 'wb') as f:
            f.write(str.encode("P1\n") if mode == "ascii" else str.encode("P4\n"))
            f.write(str.encode("# Created by svg2pbm converter\n"))
            f.write(str.encode(f"{width} {height}\n"))
            if mode == "bin":
                f.write(buffer)
            else:
                line_length = 70 if width >= 70 else width              # A line should not exceed 70 characters.
                for col in range(0, len(buffer), line_length):
                    f.write(str.encode(buffer[col:col+line_length]+'\n'))

    def convert(self, filename, width, height, mode="bin"):
        """
        convert a svg file to the pbm format ascii or binary.

        Parameters
        ----------
        filename : str
            name of the file.
        width : int
            target width in pixel.
        height : TYPE
            target height in pixel.
        mode : TYPE, optional
            'ascii' or 'bin. The default is 'bin'.

        Returns
        -------
        None.

        """
        filename_out = filename.split('.')[0]
        cairosvg.svg2png(url=f'{self.inpath}/{filename}', output_width=width, output_height=height, write_to="$$$1.png")
        img = wx.Image("$$$1.png")
        os.remove("$$$1.png")
        img = img.ConvertToMono(128, 128, 128)
        img.ConvertAlphaToMask(255, 255, 255)                # see https://docs.wxpython.org/wx.1moduleindex.html

        asciibuffer = self.img2pbm_ascii(img.GetData(), width)
        binbuffer = self.ascii2bin(asciibuffer, width)

        if mode == 'ascii':
            self.write_pbm(filename_out, asciibuffer, width, height, 'ascii')
        elif mode == 'bin':
            self.write_pbm(filename_out, binbuffer, width, height, 'bin')

    def convert_dir(self, width, height, mode="bin"):
        """
        Convert all svg-files in a directory to the pbm format ascii or binary.

        Parameters
        ----------
        width : int
            target width in pixel.
        height : TYPE
            target height in pixel.
        mode : TYPE, optional
            'ascii' or 'bin. The default is 'bin'.

        Returns
        -------
        None.

        """
        files = os.listdir(self.inpath)
        for filename in files:
            if filename.split('.')[-1] == "svg":
                self.convert(filename, width, height, mode)


if __name__ == "__main__":
    app = wx.App()
    frame = SVG2pbm(None)
    path = os.getcwd()
    frame.inpath = path + os.sep + "svg"
    frame.outpath = path + os.sep + "pbm"

    mode, image, width, heigth = frame.loadpbm(f'{path}/pbm/wb_car_.pbm')
    #binbuffer = frame.ascii2bin(image, width)
    #asciibuffer = frame.bin2ascii(image, width)
    #frame.write_pbm('wb_car_50x50t', asciibuffer, width, heigth, 'ascii')

    # frame.convert("wb_car.svg", 30, 30, "ascii"
    frame.convert("wb_car.svg", 100, 100, "ascii")
    #frame.convert_dir(50, 50)
