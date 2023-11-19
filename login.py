import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import base64

st.set_page_config(page_title="Please Login", layout="centered", initial_sidebar_state="collapsed")
st.write("# Welcome!")

# Display the background image
def set_background(image_url):
    st.markdown(f"""
        <style>
        .stApp {{
                background-image: url({image_url});
                background-attachment: fixed;
                background-size: cover;
            }}
        </style>
    """, unsafe_allow_html=True)

#set_background('https://img.uhdpaper.com/wallpaper/abstract-blue-wave-background-digital-art-486@0@f-thumb.jpg?dl')
# Call set_background() with the correct image url based on the page we're navigating to\
# https://img.uhdpaper.com/wallpaper/abstract-blue-wave-background-digital-art-486@0@f-thumb.jpg?dl
# https://images.unsplash.com/photo-1542281286-9e0a16bb7366

if 'logged-in' not in st.session_state:
    st.session_state['logged-in'] = False
else:
    st.session_state['logged-in'] = False


from yaml.loader import SafeLoader
with open('credentials.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

#link = '[GitHub](http://github.com)'
#st.markdown(link, unsafe_allow_html=True)

st.write(f'''
    <a target="_self" href="https://eox.at">
        <button>
            Please login via Google
        </button>
    </a>
    ''',
    unsafe_allow_html=True
)
name, authentication_status, username = authenticator.login('Login', 'main')

if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main', key='unique_key')
    st.write(f'Welcome *{st.session_state["name"]}*!')
    st.session_state['logged-in']= True
    st.title('Some content')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')