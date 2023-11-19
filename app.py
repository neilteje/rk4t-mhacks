from multi import MultiApp
import streamlit as st
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from svgpathtools import parse_path
from landing import show_landing_page

st.set_page_config(page_title="Streamlit Drawable Canvas", page_icon=":pencil2:")

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

def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Home'

    if st.session_state['page'] == 'Home':
        show_landing_page()
    elif st.session_state['page'] == 'Draw Away!':
        full_app()  # You need to define this function
    # elif st.session_state['page'] == 'Output Page':
    #     show_sign_in_page()  # You need to define this function

    # PAGES = {
    #     "Images": full_app,
    # }
    # page = st.sidebar.selectbox("Page:", options=list(PAGES.keys()))
    # PAGES[page]()

if __name__ == "__main__":
    main()