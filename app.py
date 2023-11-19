from multi import MultiApp
import streamlit as st
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from svgpathtools import parse_path
from landing import show_landing_page
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def showLanding():
    page_bg_img = '''
    <style>
    body {
    background-image: url("background.png");
    background-size: cover;
    }
    </style>
    '''

    st.markdown(page_bg_img, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.image('background.png', use_column_width=True)

    with col2:
        st.write("## Welcome to MPaint!")
        st.write("Join the community of creative minds.")
    
        join_now_button = st.button('Join Now', key='join_now_landing')
        sign_in_button = st.button('Sign In', key='sign_in_landing')
        if join_now_button:
            st.write("Join Now button clicked")
            st.session_state['page'] = 'Join Page'
        elif sign_in_button:
            st.write("Sign In button clicked")
            st.session_state['page'] = 'Join Page'

def full_app():
    st.sidebar.header("Configuration")
    st.markdown(
        """
    Draw on the canvas
    * Configure how you want it to look on the sidebar
    * In transform mode, double-click an object to remove it
    * After drawing, make sure to save your work and upload it into our AI model for a surprise!
    """
    )

    drawing_mode = st.sidebar.selectbox(
        "Drawing tool:",
        ("freedraw", "line", "rectangle", "circle", "transformation", "polygon", "point"),
    )
    stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
    if drawing_mode == "point":
        point_display_radius = st.sidebar.slider("Point display radius: ", 1, 25, 3)
    stroke_color = st.sidebar.color_picker("Stroke color hex: ")
    bg_color = st.sidebar.color_picker("Background color hex: ", "#eee")
    bg_image = st.sidebar.file_uploader("Background image:", type=["png", "jpg"])
    realtime_update = st.sidebar.checkbox("Update in realtime", True)
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        background_image=Image.open(bg_image) if bg_image else None,
        update_streamlit=realtime_update,
        height=500,
        drawing_mode=drawing_mode,
        point_display_radius=point_display_radius if drawing_mode == "point" else 0,
        display_toolbar=st.sidebar.checkbox("Display toolbar", True),
        key="full_app",
    )

    # if canvas_result.image_data is not None:
    #     st.image(canvas_result.image_data)
    if canvas_result.json_data is not None:
        objects = pd.json_normalize(canvas_result.json_data["objects"])
        for col in objects.select_dtypes(include=["object"]).columns:
            objects[col] = objects[col].astype("str")
        st.dataframe(objects)

def logging():
    st.write("# Welcome!")

    # Optionally, set a background image
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

    # Call set_background() with the correct image URL
    set_background('background.png')

    # Initialize session state for login status
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Load credentials
    with open('credentials.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config['preauthorized']
        )

    # Login form
    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.write(f'Welcome *{name}*!')
        st.session_state['logged_in'] = True
        st.title('Some content')
    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')

    # Google login button (optional, for illustration)
    st.markdown("""
        <a target="_self" href="https://eox.at">
            <button>
                Please login via Google
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

def username_taken(username, users):
    return username.lower() in users

# Function to check if the email is taken
def email_taken(email, users):
    return email.lower() in [user.get('email', '').lower() for user in users.values()]

# Function to display the join now page
def joinnow():
    with open('data.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    users = config['credentials']['usernames']
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    registration_username = st.text_input('Username:')
    registration_email = st.text_input('Email:')
    registration_name = st.text_input('Name:')
    registration_password = st.text_input('Password:', type='password')
    registration_button = st.button('Register')

    if registration_button:
        if username_taken(registration_username, users):
            st.error('Username is already taken. Please choose a different one.')
        elif email_taken(registration_email, users):
            st.error('Email is already taken. Please choose a different one.')
        else:
            hashed_password = stauth.Hasher([registration_password]).generate()
            new_user = {
                'email': registration_email,
                'name': registration_name,
                'password': hashed_password[0]
            }
            users[registration_username.lower()] = new_user

            with open('data.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)

            st.success('User registered successfully')

def output():
    pass

def navbar():
    col1, col2, col3, col4, col5 = st.columns([4, 1, 1, 1, 1])
    with col1:
        st.markdown("""
            <h1 style='font-size: 36px; font-weight: bold;'>MPaint</h1>
            """, unsafe_allow_html=True)
    with col2:
        if st.button('Home'):
            st.session_state['page'] = 'landing'
    with col3:
        if st.button('Draw'):
            st.session_state['page'] = 'draw'
    with col4:
        if st.button('Join'):
            st.session_state['page'] = 'join'
    with col5:
        if st.button('Login'):
            st.session_state['page'] = 'login'

def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'landing'

    # navbar on top poggies
    navbar()

    # render pages using session states
    if st.session_state['page'] == 'landing':
        show_landing_page()
    elif st.session_state['page'] == 'draw':
        full_app()
    elif st.session_state['page'] == 'login':
        logging()
    elif st.session_state['page'] == 'join':
        joinnow()
    elif st.session_state['page'] == 'output':
        output()
    # elif st.session_state['page'] == 'Output Page':
    #     show_sign_in_page()  # You need to define this function

    # PAGES = {
    #     "Images": full_app,
    # }
    # page = st.sidebar.selectbox("Page:", options=list(PAGES.keys()))
    # PAGES[page]()

if __name__ == "__main__":
    st.set_page_config(page_title="Streamlit Drawable Canvas", page_icon=":pencil2:")
    main()