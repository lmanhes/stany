from bitstring import BitArray
import zlib


def str2bin(message: str, encoding='utf-8') -> str:
    return BitArray(message.encode(encoding)).bin


def bytes2bin(message: bytes) -> str:
    return BitArray(message).bin


def bin2str(bin_array: str, encoding='utf-8') -> str:
    return BitArray(bin=bin_array).bytes.decode(encoding)


def bin2bytes(bin_array: str) -> str:
    return BitArray(bin=bin_array).bytes


def color2bin(color: int) -> str:
    return format(color, "08b")


def zip_message(message: str, encoding: str = 'utf-8'):
    return zlib.compress(message.encode(encoding))


def unzip_message(message: bytes, encoding: str = 'utf-8'):
    return zlib.decompress(message).decode(encoding)