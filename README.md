# stany

 [Steganography](https://en.wikipedia.org/wiki/Steganography) library written in python

 You can use Stany to encode any text message or binary file inside an arbitrary RGB/RGBA image.
 The payload will be encrypted with [AES](https://fr.wikipedia.org/wiki/Advanced_Encryption_Standard) and embedded inside the pixels' [least significant bits](https://en.wikipedia.org/wiki/Bit_numbering).

 A Streamlit app is also provided to facilitate the use of Stany.

A possible use is to encode a book you just wrote or confidential documents inside any image. This way your documents will always stay with you and go unnoticed by everyone.


## Features

[X] Encode plain texts messages
[X] Encode compressed files
[X] Encrypt messages with AES
[X] Use dynamic number of least significant bits


## How to use

### Api
```python
from PIL import Image

from stany import encode, decode

img = Image.open("path-to-my-img.png")
message = "Hello world"

encoded_img, secret_key = encode(img, message)

decoded_message = decode(encoded_img, secret_key)
```

### App
```shell
streamlit run app/main.py
```

## To do's

[ ] Add tests
[ ] Hide message inside high entropy locations
