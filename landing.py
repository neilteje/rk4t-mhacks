import streamlit as st

def show_landing_page():
    st.set_page_config(page_title="Welcome to the Drawable Canvas App!", page_icon="🎨")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.title("Welcome to the Drawable Canvas App!")
        st.subheader("Unleash Your Creativity")
        st.write("""
            The Drawable Canvas App is a place where you can express your artistic ideas 
            and bring your visions to life. Draw, sketch, and create with our intuitive 
            tools and share your artwork with the world.
        """)
        st.write("Ready to start creating? Click on 'Draw away!' to begin.")

    with col2:
        st.image("path_to_your_landing_page_image.jpg", use_column_width=True)

    if st.button("Draw away!"):
        st.session_state['page'] = 'Draw away!'
        st.experimental_rerun()

if __name__ == "__main__":
    show_landing_page()
