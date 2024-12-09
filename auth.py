import streamlit as st
import sqlite3
import hashlib
from typing import Tuple, Optional

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def sign_up(username: str, password: str) -> Tuple[bool, str]:
    if not username or not password:
        return False, "Please provide both username and password"
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Check if username already exists
    c.execute('SELECT username FROM users WHERE username = ?', (username,))
    if c.fetchone() is not None:
        conn.close()
        return False, "Username already exists"
    
    # Insert new user
    hashed_password = hash_password(password)
    c.execute('INSERT INTO users VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()
    return True, "Sign up successful!"

def sign_in(username: str, password: str) -> Tuple[bool, str]:
    if not username or not password:
        return False, "Please provide both username and password"
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Check credentials
    hashed_password = hash_password(password)
    c.execute('SELECT username FROM users WHERE username = ? AND password = ?', 
              (username, hashed_password))
    
    result = c.fetchone()
    conn.close()
    
    if result is not None:
        return True, "Sign in successful!"
    return False, "Invalid username or password"

def show_login_page() -> None:
    st.title("🎓 Edusphere Login")
    
    # Initialize session state for authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        st.subheader("Sign In")
        signin_username = st.text_input("Username", key="signin_username")
        signin_password = st.text_input("Password", type="password", key="signin_password")
        
        if st.button("Sign In"):
            success, message = sign_in(signin_username, signin_password)
            if success:
                st.session_state.authenticated = True
                st.session_state.username = signin_username  # Store username
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    with tab2:
        st.subheader("Sign Up")
        signup_username = st.text_input("Username", key="signup_username")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        
        if st.button("Sign Up"):
            success, message = sign_up(signup_username, signup_password)
            if success:
                st.success(message)
            else:
                st.error(message) 