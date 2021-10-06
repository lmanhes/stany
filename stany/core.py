from bitstring import BitArray, Error
from cryptography.fernet import Fernet
from PIL import Image
from typing import Union, List

from stany.utils import str2bin, bytes2bin, bin2str, color2bin, zip_message, unzip_message
from stany.init_logger import get_logger


logger = get_logger(__name__)


def set_n_significant_bit(img, full_message_length: int, n_lsb_max: int = 3):
    for n in range(1, n_lsb_max+1):
        capacity = 3 * img.size[0] * img.size[1] * n
        
        if capacity >= full_message_length:
            return n


def get_lsb(color: int, n_bit: int) -> bool:
    return color2bin(color)[-n_bit:]


def change_lsb(color: int, bits: Union[bool, List[bool]]) -> str:
    if isinstance(bits, bool):
        bits = [bits]
    return int(color2bin(color)[:-len(bits)] + bits, 2)

    
def encode(
    img, 
    message: Union[str, bytes], 
    delim_symbol: str = ":",
    n_lsb_max: int = 3) -> tuple:

    if isinstance(img, str):
        img = Image.open(img)
    assert img.mode in ["RGB", "RGBA"], "Image mode should be either rgb or rgba" 
    steg_img = img.copy()

    if isinstance(message, str):
        message = zip_message(message)
    logger.info(f"Message length {len(message)} bytes")

    key = Fernet.generate_key()
    f = Fernet(key)
    encrypt_message = f.encrypt(message)
    logger.info(f"Encrypted message length {len(encrypt_message)} bytes")

    message_bin = bytes2bin(encrypt_message)
    message_length = len(message_bin)
    logger.info(f"Binary message length: {message_length} bits")

    header_bin = str2bin(str(message_length) + delim_symbol) # don't forget to add n_bit

    n_bit = set_n_significant_bit(
        img=steg_img,
        n_lsb_max=n_lsb_max,
        full_message_length=len(header_bin) + len(message_bin) + 8) # n_bit is a single int

    if n_bit is None:
        raise ValueError(f"Message is too big for this image")
    capacity = 3 * steg_img.size[0] * steg_img.size[1] * n_bit

    header_bin = str2bin(str(n_bit)) + header_bin # add n_bit 
    logger.info(f"Header length: {len(header_bin)} bits")

    full_message_bin = header_bin + message_bin
    full_message_length = len(full_message_bin)
    logger.info(f"Full_message_length: {full_message_length} bits")

    logger.info(f"Capacity: {capacity}, n_bits: {n_bit}")

    completed = False
    index = 0
    for i in range(steg_img.size[0]):
        for j in range(steg_img.size[1]):

            pixel = img.getpixel((i, j))

            encoded_pixel = []
            for channel in range(3):
                color = pixel[channel]
                
                # encoding header
                if index < len(header_bin):
                    encoded_pixel.append(change_lsb(color, full_message_bin[index]))
                    index += 1

                # message complete, the rest of the channels are copied
                elif index >= full_message_length:
                    completed  = True
                    encoded_pixel.append(color)

                # encode only the bits needed to have a complete message
                elif index < (full_message_length-1) and (index + n_bit) > full_message_length:
                    n_steps = n_bit - ((index + n_bit) - full_message_length)
                    encoded_pixel.append(change_lsb(color, full_message_bin[index:index+n_steps]))
                    index += n_steps

                # encoding message
                else:
                    encoded_pixel.append(change_lsb(color, full_message_bin[index:index+n_bit]))
                    index += n_bit

            if steg_img.mode == "RGBA":
                encoded_pixel.append(pixel[3])
                
            steg_img.putpixel((i, j), tuple(encoded_pixel))

            if completed:
                return steg_img, key


def decode(img, key, utf=8, delim_symbol: str = ":"):
    try:
        f = Fernet(key)
    except:
        raise ValueError(f"Crypto key is incorrect")

    n_bit_bin = []
    n_bit = None

    reach_header = False
    header_bin = []
    header_str = ""

    message_bin = []
    
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            
            pixel = img.getpixel((i, j))

            for channel in range(3):
                color = pixel[channel]

                # decoding number of lsb per channel
                if n_bit is None:
                    lsb = get_lsb(color, n_bit=1)
                    n_bit_bin.extend(lsb)

                    if len(n_bit_bin) == utf:
                        n_bit_str = bin2str(bin_array="".join(n_bit_bin), encoding=f'utf-{utf}')
                        n_bit = int(n_bit_str)
                        logger.info(f"Decoded n_bit: {n_bit}")

                # decoding header (size of message + limitation symbol)
                elif not reach_header:
                    lsb = get_lsb(color, n_bit=1)
                    header_bin.extend(lsb)

                    if len(header_bin) % utf == 0:
                        header_str = bin2str("".join(header_bin))

                    if header_str.endswith(delim_symbol) and not reach_header:
                        header_length = len(header_bin) + len(n_bit_bin)
                        message_length = int(header_str[:-len(delim_symbol)])
                        full_message_length = header_length + message_length
                        logger.info(f"Decoded header length: {header_length}")
                        logger.info(f"Decoded message length: {message_length}")
                        logger.info(f"Decoded full message length: {full_message_length}")
                        reach_header = True

                # decode only the bits needed to complete the message
                elif len(message_bin) + n_bit > message_length:
                    n_steps = n_bit - ((len(message_bin) + n_bit) - message_length)
                    lsb = get_lsb(color, n_bit=n_steps)
                    message_bin.extend(lsb)

                    message_bytes = BitArray(bin="".join(message_bin))
                    decrypt_message = f.decrypt(message_bytes.bytes)
                    return unzip_message(decrypt_message)

                # decoding message
                else:
                    lsb = get_lsb(color, n_bit=n_bit)
                    message_bin.extend(lsb)

                    if len(message_bin) == message_length:
                        message_bytes = BitArray(bin="".join(message_bin))
                        decrypt_message = f.decrypt(message_bytes.bytes)
                        return unzip_message(decrypt_message)
    