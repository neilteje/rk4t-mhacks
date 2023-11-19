import streamlit as st
import streamlit_authenticator as stauth

import yaml

st.set_page_config(
    page_title="Join",
    page_icon="👋",
)
from yaml.loader import SafeLoader
with open('data.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

def username_taken(username):
    # Check if the provided username or email is already taken
    existing_usernames = [user.lower() for user in config['credentials']['usernames']]
    if username.lower() in existing_usernames:
        return True
    return False

def email_taken(email):
    existing_emails = [user['email'].lower() for user in config['credentials']['usernames'].values()]
    if email.lower() in existing_emails:
        return True

    return False

registration_username = st.text_input('Username:')
registration_email = st.text_input('Email:')
registration_name = st.text_input('Name:')
registration_password = st.text_input('Password:', type='password')
registration_button = st.button('Register')

if 'logged-in' not in st.session_state:
    st.session_state['logged-in'] = False
else:
    st.session_state['logged-in'] = False


if registration_button:
    try:
        # Check if the username or email is already taken
        if username_taken(registration_username):
            st.error('Username is already taken. Please choose a different one.')
        if email_taken(registration_email):
            st.error('Email is already taken. Please choose a different one.')
        else:
            # Hash the password securely
            hashed_password = stauth.Hasher([registration_password]).generate()

            # Register the new user with hashed password
            new_user = {
                'email': registration_email,
                'name': registration_name,
                'password': hashed_password[0]  # Decode the bytes to store as a string
            }
            config['credentials']['usernames'][registration_username.lower()] = new_user

            # Write the updated dictionary back to the YAML file
            with open('data.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)

            st.success('User registered successfully')
            st.session_state['logged-in'] = True

    except Exception as e:
        st.error(f'Error registering user: {e}')