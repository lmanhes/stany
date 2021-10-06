import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import io
from PIL import Image
import streamlit as st

from stany.core import encode, decode


st.set_page_config(
    page_title="Steganography application",
    layout="wide",
    initial_sidebar_state="expanded")


def html_validation_error(text):
    st.markdown(f'<p style="color:#e60000">{text}</p>', unsafe_allow_html=True)


def html_validation_success(text):
    st.markdown(f'<p style="color:#33cc33">{text}</p>', unsafe_allow_html=True)


@st.cache
def encode_message(img, message):
    steg_img, key = encode(img=img, message=message)
    return steg_img, key


@st.cache
def decode_message(img, key):
    return decode(enc_img, key)


if "has_encode_inputs" not in st.session_state:
    st.session_state["has_encode_inputs"] = False

if "has_decode_inputs" not in st.session_state:
    st.session_state["has_decode_inputs"] = False


st.title("Stany")
st.header("Image based steganography")

st.markdown("---")


action = st.sidebar.selectbox("Choose action", options=("encode", "decode"))

if action == "encode":

    st.session_state["has_encode_inputs"] = False

    col1, _, col2 = st.columns((3, 1, 3))

    img_file = col1.file_uploader("Upload a colored image", type=['png'])
    if img_file:
        img = Image.open(img_file)
        col1.image(img)


        media_options = col2.selectbox(
            "Choose the type of message to send", 
            options=("raw text", "text file"))

        if media_options == "raw text":
            message = col2.text_area("", height=200)
            if message:
                st.session_state["has_encode_inputs"] = True
        elif media_options == "text file":
            message_file = col2.file_uploader("Upload a file to send", type=['txt'])
            if message_file:
                stringio = io.StringIO(message_file.getvalue().decode("utf-8"))
                message = stringio.read()
                st.session_state["has_encode_inputs"] = True

    st.markdown("---")

    if st.session_state["has_encode_inputs"] == True: 
        
        steg_img, key = encode_message(img, message)

        st.write("")
        st.markdown("#### This is your secret key to de-cypher your message")
        st.text_input(label="", value=key.decode('utf-8'))
        st.write("")
        st.download_button("Download your secret key", file_name="txt", data=key)
        st.write("")

        st.markdown("#### Your message is now embedded inside the image")
        st.write("")
        st.image(steg_img, width=365)

        buffered = io.BytesIO()
        steg_img.save(buffered, format="png")
        st.write("")
        st.download_button("Download your encoded image", file_name="secret_image.png", data=buffered)
        
    else:
        html_validation_error("You must provide an image and a message")


else:
    col1, _, col2 = st.columns((3, 1, 3))

    img_file = col1.file_uploader("Upload the encoded image", type=['png'])
    if img_file:
        enc_img = Image.open(img_file)
        col1.image(enc_img)

        key = col2.text_input("Enter your secret key")
        if key:
            st.session_state["has_decode_inputs"] = True

    st.markdown("---")

    if st.session_state["has_decode_inputs"] == True: 
        
        decoded_message = decode(enc_img, key)

        st.write("")
        st.text_area(label="", height=300, value=decoded_message)