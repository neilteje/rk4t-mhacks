import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import pandas as pd

# Define a function to create the top navigation bar
def create_top_nav(selected_page):
    st.markdown("""<style>.btn-outline-secondary { border: none; }</style>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    pages = ['Home', 'Draw away!', 'About']
    if col1.button('Home'):
        st.session_state['page'] = 'Home'
    if col2.button('Draw away!'):
        st.session_state['page'] = 'Draw away!'
    if col3.button('About'):
        st.session_state['page'] = 'About'

    # Highlight the selected page
    for i, page in enumerate(pages):
        if page == selected_page:
            st.session_state[f'col{i+1}'].button_style = {'background-color': 'grey'}

def main():
    # Top navigation bar
    st.set_page_config(page_title="Streamlit Drawable Canvas", page_icon=":pencil2:")

    # Use session state to store the current page
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Home'
    
    # Create the top navigation bar and pass the current page
    create_top_nav(st.session_state['page'])

    # Render the selected page
    if st.session_state['page'] == 'Home':
        st.header("Home")
        st.write("This is the Home page.")
    elif st.session_state['page'] == 'Draw away!':
        full_app()
    elif st.session_state['page'] == 'About':
        st.header("About")
        st.write("This is the About page.")

def full_app():
    # Create a two-column layout, the drawing canvas on the left and the tools on the right
    canvas_col, tools_col = st.columns([3, 1], gap="small")
    
    with canvas_col:
        # This will be your main canvas area
        canvas_result = create_canvas()

    with tools_col:
        # Put all the configurations for drawing tools here
        create_tools_sidebar(canvas_result)
def create_canvas():
    # Set up the canvas with the drawing parameters
    stroke_width = st.session_state.get('stroke_width', 3)
    stroke_color = st.session_state.get('stroke_color', '#000000')
    bg_color = st.session_state.get('bg_color', '#eeeeee')
    bg_image = st.session_state.get('bg_image', None)
    drawing_mode = st.session_state.get('drawing_mode', 'freedraw')
    realtime_update = st.session_state.get('realtime_update', True)
    display_toolbar = st.session_state.get('display_toolbar', True)

    # Create the canvas component
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        background_image=Image.open(bg_image) if bg_image else None,
        update_streamlit=realtime_update,
        height=500,
        drawing_mode=drawing_mode,
        display_toolbar=display_toolbar,
        key="canvas",
    )
    return canvas_result


def create_tools_sidebar(canvas_result):
    # Configuration for drawing tools
    st.header("Tools")
    st.session_state['drawing_mode'] = st.selectbox(
        "Drawing tool:",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
        key='drawing_mode'
    )
    st.session_state['stroke_width'] = st.slider("Stroke width: ", 1, 25, 3, key='stroke_width')
    if st.session_state['drawing_mode'] == "point":
        # Only show point display radius if the point tool is selected
        st.session_state['point_display_radius'] = st.slider("Point display radius: ", 1, 25, 3, key='point_display_radius')
    st.session_state['stroke_color'] = st.color_picker("Stroke color hex: ", key='stroke_color')
    st.session_state['bg_color'] = st.color_picker("Background color hex: ", "#eee", key='bg_color')
    st.session_state['bg_image'] = st.file_uploader("Background image:", type=["png", "jpg"], key='bg_image')
    st.session_state['realtime_update'] = st.checkbox("Update in realtime", True, key='realtime_update')
    st.session_state['display_toolbar'] = st.checkbox("Display toolbar", True, key='display_toolbar')

    # Show the image data and paths if available
    if canvas_result.image_data is not None:
        st.image(canvas_result.image_data)
    if canvas_result.json_data is not None:
        objects = pd.json_normalize(canvas_result.json_data["objects"])
        for col in objects.select_dtypes(include=["object"]).columns:
            objects[col] = objects[col].astype("str")
        st.dataframe(objects)


if __name__ == "__main__":
    main()
