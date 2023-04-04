'''Exploiting color (perceptual) redundancy with the YCoCg transform.'''

import entropy_image_coding as EIC
import numpy as np
import logging
import main
import importlib
#import quantization

from color_transforms.YCrCb import from_RGB # pip install "color_transforms @ git+https://github.com/vicente-gonzalez-ruiz/color_transforms"
from color_transforms.YCrCb import to_RGB

default_QSS = 32
default_EIC = "PNG"
default_quantizer = "deadzone"

#EIC.parser_encode.add_argument("-q", "--QSS", type=EIC.int_or_str, help=f"Quantization step size (default: {default_QSS})", default=default_QSS)
#EIC.parser.add_argument("-e", "--entropy_image_codec", help=f"Entropy Image Codec (default: {default_EIC}", default=default_EIC)
EIC.parser.add_argument("-X", "--Xquantizer", help=f"Quantizer (default: {default_quantizer}", default=default_quantizer)

args = EIC.parser.parse_args()
print(args)
Q = importlib.import_module(args.Xquantizer)

class CoDec(Q.CoDec):

    def encode(self):
        img = self.encode_read()
        #img_128 = img.astype(np.int16) - 128
        YCoCg_img = from_RGB(img.astype(np.uint8))
        k = self.quantize(YCoCg_img)
        compressed_k = self.compress(k)
        self.encode_write(compressed_k)
        rate = (self.output_bytes*8)/(img.shape[0]*img.shape[1])
        return rate

    def decode(self):
        compressed_k = self.decode_read()
        k = self.decompress(compressed_k)
        #k = self.read()
        YCoCg_y = self.dequantize(k)
        #y_128 = to_RGB(YCoCg_y.astype(np.int16))
        y = to_RGB(YCoCg_y.astype(np.uint8))
        #y = (y_128.astype(np.int16) + 128)
        y = np.clip(y, 0, 255).astype(np.uint8)
        self.decode_write(y)
        rate = (self.input_bytes*8)/(k.shape[0]*k.shape[1])
        return rate

if __name__ == "__main__":
    main.main(EIC.parser, logging, CoDec)
