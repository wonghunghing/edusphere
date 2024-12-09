import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from auth import init_db, show_login_page

# Load environment variables from .env file
load_dotenv()

# Initialize the database
init_db()

# Set up the page configuration
st.set_page_config(page_title="Edusphere Education", page_icon="🎓")

# Initialize OpenAI client
client = OpenAI()

# Check authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Show login page if not authenticated
if not st.session_state.authenticated:
    show_login_page()
else:
    # Add logout button in sidebar
    with st.sidebar:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.messages = []
            st.session_state.selected_subject = None
            st.session_state.username = None  # Clear username on logout
            st.rerun()
    
    # Initialize session state variables
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'selected_subject' not in st.session_state:
        st.session_state.selected_subject = None

    # Subject images dictionary
    subject_images = {
        "Mathematics": "https://img.freepik.com/free-vector/mathematical-equations-background_23-2148162823.jpg",
        "Physics": "https://img.freepik.com/free-vector/hand-drawn-physics-background_23-2148163125.jpg",
        "Chemistry": "https://img.freepik.com/free-vector/hand-drawn-chemistry-background_23-2148163136.jpg",
        "Biology": "https://img.freepik.com/free-vector/hand-drawn-biology-background_23-2148162166.jpg",
        "History": "https://img.freepik.com/free-vector/vintage-old-books-background_23-2148162160.jpg",
        "Literature": "https://img.freepik.com/free-photo/books-arrangement-with-copy-space_23-2148890922.jpg",
        "Computer Science": "https://img.freepik.com/free-vector/programming-code-background_23-2148160526.jpg"
    }

    # Subject videos dictionary (YouTube video IDs)
    subject_videos = {
        "Mathematics": "https://youtu.be/pTnEG_WGd2Q",  # Khan Academy: What is Algebra?
        "Physics": "https://youtu.be/ZM8ECpBuQYE",      # Physics Basics
        "Chemistry": "https://youtu.be/rz4Dd1I_fX0",    # The Periodic Table
        "Biology": "https://youtu.be/QnQe0xW_JY4",      # Introduction to Biology
        "History": "https://youtu.be/Yocja_N5s1I",      # Crash Course World History
        "Literature": "https://youtu.be/4ZXQQtUyJCQ",   # How to Analyze Literature
        "Computer Science": "https://youtu.be/zOjov-2OZ0E"  # Introduction to Programming
    }

    # Page title
    st.title("🎓 Edusphere Smart Education")

    # Subject selection
    subjects = [
        "Mathematics",
        "Physics",
        "Chemistry",
        "Biology",
        "History",
        "Literature",
        "Computer Science"
    ]

    # Sidebar for subject selection
    with st.sidebar:
        st.header("Select Your Subject")
        selected_subject = st.selectbox(
            "What would you like to learn about?",
            subjects,
            key="subject_selector"
        )
        
        # Display subject image
        if selected_subject:
            st.image(subject_images[selected_subject], caption=f"{selected_subject} Visual", use_container_width=True)
        
        if selected_subject != st.session_state.selected_subject:
            st.session_state.messages = []
            st.session_state.selected_subject = selected_subject
        
        st.markdown("""
        ### How to use:
        1. Select your subject from the dropdown
        2. Ask any question about the subject
        3. The bot will help you learn and understand the topic
        """)

    # Display current subject
    st.subheader(f"Currently studying: {selected_subject}")

    # Display video
    st.video(subject_videos[selected_subject])
    st.caption("Educational video related to " + selected_subject)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask your question here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Prepare the context for the AI
        context = f"You are an expert tutor in {selected_subject}. Provide clear, educational responses suitable for students. If using mathematical equations, explain them clearly."
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                full_prompt = [
                    {"role": "system", "content": context},
                    *st.session_state.messages
                ]
                
                # Create an empty placeholder
                message_placeholder = st.empty()
                # Initialize an empty string to store the full response
                full_response = ""
                
                # Stream the response
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": m["role"], "content": m["content"]} for m in full_prompt],
                    temperature=0.7,
                    stream=True,
                )
                
                # Process the stream
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                # Remove the cursor and display final response
                message_placeholder.markdown(full_response)
                
                # Add AI response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Add some styling
    st.markdown("""
    <style>
        .stChat {
            padding: 20px;
        }
        img {
            border-radius: 10px;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)