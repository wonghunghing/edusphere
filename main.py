import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from auth import init_db, show_login_page
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse
import streamlit_scrollable_textbox as stx

# Load environment variables from .env file
load_dotenv()

# Initialize the database
init_db()



def get_video_id(url):
    """Extract video ID from YouTube URL"""
    if 'youtu.be' in url:
        return url.split('/')[-1]
    query = urlparse(url)
    if query.hostname == 'www.youtube.com':
        return query.query[2:]
    return url.split('/')[-1]

def get_transcript(video_url):
    """Get transcript of YouTube video"""
    try:
        video_id = get_video_id(video_url)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ''
        for segment in transcript_list:
            transcript_text += segment['text'] + ' '
        return transcript_text
    except Exception as e:
        return f"Transcript not available: {str(e)}"




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
    # Initialize session state variables
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'selected_subject' not in st.session_state:
        st.session_state.selected_subject = None
    if 'selected_chapter' not in st.session_state:
        st.session_state.selected_chapter = None

    # Subject images dictionary
    subject_images = {
        "Mathematics": "images/maths.jpg",
        "Physics": "images/physics.jpg",
        "Chemistry": "images/chemistry.jpg",
        "Biology": "images/biology.jpg",
        "History": "images/history.jpg",
        "Literature": "images/literature.jpg",
        "Computer Science": "images/computer.jpg"
    }

    # Subject chapters dictionary
    subject_chapters = {
        "Mathematics": [
            {"title": "Algebra", "description": "Study of mathematical symbols and rules for manipulating these symbols."},
            {"title": "Geometry", "description": "Study of shapes, sizes, and properties of space."},
            {"title": "Calculus", "description": "Study of change and motion, using derivatives and integrals."},
            {"title": "Statistics", "description": "Study of data collection, analysis, interpretation, and presentation."},
            {"title": "Trigonometry", "description": "Study of relationships between the angles and sides of triangles."}
        ],
        "Physics": [
            {"title": "Mechanics", "description": "Study of motion and forces."},
            {"title": "Thermodynamics", "description": "Study of heat and temperature and their relation to energy and work."},
            {"title": "Electromagnetism", "description": "Study of electric charges, electric and magnetic fields."},
            {"title": "Optics", "description": "Study of light and its interactions with matter."},
            {"title": "Quantum Physics", "description": "Study of the behavior of matter and energy at the atomic and subatomic levels."}
        ],
        "Chemistry": [
            {"title": "Organic Chemistry", "description": "Study of the structure, properties, and reactions of organic compounds."},
            {"title": "Inorganic Chemistry", "description": "Study of inorganic compounds, typically those that do not contain carbon."},
            {"title": "Physical Chemistry", "description": "Study of how matter behaves on a molecular and atomic level."},
            {"title": "Analytical Chemistry", "description": "Study of the composition of materials."},
            {"title": "Biochemistry", "description": "Study of chemical processes within and relating to living organisms."}
        ],
        "Biology": [
            {"title": "Cell Biology", "description": "Study of the structure and function of cells."},
            {"title": "Genetics", "description": "Study of heredity and the variation of inherited characteristics."},
            {"title": "Evolution", "description": "Study of the processes that have led to the diversity of life."},
            {"title": "Ecology", "description": "Study of interactions between organisms and their environment."},
            {"title": "Human Anatomy", "description": "Study of the structure of the human body."}
        ],
        "History": [
            {"title": "Ancient Civilizations", "description": "Study of early human societies and their cultures."},
            {"title": "Middle Ages", "description": "Study of the period in European history from the 5th to the late 15th century."},
            {"title": "Renaissance", "description": "Study of the revival of art and literature under the influence of classical models."},
            {"title": "Modern History", "description": "Study of the history of the world from the late 15th century to the present."},
            {"title": "Contemporary History", "description": "Study of recent history, typically from the end of World War II to the present."}
        ],
        "Literature": [
            {"title": "Poetry", "description": "Study of literary work in which the expression of feelings and ideas is given intensity by the use of distinctive style and rhythm."},
            {"title": "Drama", "description": "Study of plays and the performance of plays."},
            {"title": "Fiction", "description": "Study of literature created from the imagination."},
            {"title": "Non-Fiction", "description": "Study of factual accounts and real events."},
            {"title": "Literary Criticism", "description": "Study of the analysis, interpretation, and evaluation of literature."}
        ],
        "Computer Science": [
            {"title": "Programming Basics", "description": "Study of fundamental programming concepts and techniques."},
            {"title": "Data Structures", "description": "Study of data organization, management, and storage formats."},
            {"title": "Algorithms", "description": "Study of step-by-step procedures for calculations."},
            {"title": "Web Development", "description": "Study of building and maintaining websites."},
            {"title": "Machine Learning", "description": "Study of algorithms that improve automatically through experience."}
        ]
    }

    # Chapter videos dictionary
    chapter_videos = {
        "Mathematics": [
            "https://youtu.be/NybHckSEQBI",  # Algebra
            "https://youtu.be/nwLEByAAqlM",  # Geometry
            "https://youtu.be/UukVP7Mg3TU",  # Calculus
            "https://youtu.be/sxQaBpKfDRk",  # Statistics
            "https://youtu.be/T9lt6MZKLck"   # Trigonometry
        ],
        "Physics": [
            "https://youtu.be/Q-EAgsiOLcA",  # Mechanics
            "https://youtu.be/4i1MUWJoI0U",  # Thermodynamics
            "https://youtu.be/79_SF5AZtzo",  # Electromagnetism
            "https://youtu.be/Oh4m8Ees-3Q",  # Optics
            "https://youtu.be/Usu9xZfabPM"   # Quantum Physics
        ],
        "Chemistry": [
            "https://youtu.be/PmvLB5dIEp8",  # Organic Chemistry
            "https://youtu.be/cYAcrSIFvco",  # Inorganic Chemistry
            "https://youtu.be/B9DuTNaPm4M",  # Physical Chemistry
            "https://youtu.be/MPqCzsntjAE",  # Analytical Chemistry
            "https://youtu.be/CHJsaq2lNjU"   # Biochemistry
        ],
        "Biology": [
            "https://youtu.be/URUJD5NEXC8",  # Cell Biology
            "https://youtu.be/v8tJGlicgp8",  # Genetics
            "https://youtu.be/GhHOjC4oxh8",  # Evolution
            "https://youtu.be/9dAcEBXAFoo",  # Ecology
            "https://youtu.be/Ae4MadKPJC0"   # Human Anatomy
        ],
        "History": [
            "https://youtu.be/wX6J0Gd2EC8",  # Ancient Civilizations
            "https://youtu.be/H5AVPmAZ8o8",  # Middle Ages
            "https://youtu.be/Vufba_ZcoR0",  # Renaissance
            "https://youtu.be/kUWEYLVooxU",  # Modern History
            "https://youtu.be/T5PwyuzSYcs"   # Contemporary History
        ],
        "Literature": [
            "https://youtu.be/drPoZMqHTAw",  # Poetry
            "https://youtu.be/3CvJKTChsl4",  # Drama
            "https://youtu.be/QrUPneyZNf0",  # Fiction
            "https://youtu.be/QrUPneyZNf0",  # Non-Fiction
            "https://youtu.be/3naf-KE0uvI"   # Literary Criticism
        ],
        "Computer Science": [
            "https://youtu.be/l26oaHV7D40",  # Programming Basics
            "https://youtu.be/DuDz6B4cqVc",  # Data Structures
            "https://youtu.be/rL8X2mlNHPM",  # Algorithms
            "https://youtu.be/ysEN5RaKOlA",  # Web Development
            "https://youtu.be/PeMlggyqz0Y"   # Machine Learning
        ]
    }

    # Subject selection
    subjects = list(subject_images.keys())
    
    # Sidebar for subject selection
    with st.sidebar:
        #st.header("Management Science University")
        st.image("images/msu.webp")
        st.markdown("""""")
        
        
        st.markdown("""
                    <h2>Select Subjects</h2>
                    """, unsafe_allow_html=True)
        selected_subject = st.selectbox(
            "What would you like to learn about?",
            subjects,
            key="subject_selector"
        )
        
        
        
         # Display subject image
        if selected_subject:
            st.image(subject_images[selected_subject], caption=f"{selected_subject} Subject", use_container_width=True)

        
        # When subject changes, set the first chapter as default
        if selected_subject != st.session_state.get('previous_subject'):
            st.session_state.selected_chapter = subject_chapters[selected_subject][0]["title"]
            st.session_state.previous_subject = selected_subject
        
       
        # Display chapters for the selected subject in an accordion format
        if selected_subject:
            st.header("Select Chapters")
            for chapter in subject_chapters[selected_subject]:
                with st.expander(chapter["title"], expanded=False):
                    st.write(chapter["description"])
                    if st.button(f"Select {chapter['title']}", key=chapter["title"]):
                        st.session_state.selected_chapter = chapter["title"]  # Store selected chapter
                        
        st.markdown(
        """
        <div style="border: 2px solid #cccccc; border-radius: 10px; padding: 15px;">
            <h3>How to use:</h3>
            <ol>
                <li>Select your subject from the dropdown.</li>
                <li>Select a chapter to study.</li>
                <li>Ask any question about the chapter.</li>
                <li>The bot will help you learn and understand the topic.</li>
            </ol>
        </div>
        """, 
        unsafe_allow_html=True)
        
        st.markdown("""""")
                        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.messages = []
            st.session_state.selected_subject = None
            st.session_state.username = None  # Clear username on logout
            st.rerun()

    # Display current subject and chapter
    st.subheader(f"Currently studying: {selected_subject} - {st.session_state.selected_chapter}")
    
    # Add CSS to create a fixed video container
    st.markdown("""
        <style>
            .fixed-video {
                position: sticky;
                top: 0;
                z-index: 999;
                background-color: white;
                padding: 10px 0;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Create two main sections using columns
    video_col, spacer = st.columns([20, 1])
    
    # Display video in the fixed section
    with video_col:
        st.markdown('<div class="fixed-video">', unsafe_allow_html=True)
        if selected_subject and st.session_state.selected_chapter:
            try:
                chapter_index = next(
                    i for i, chapter in enumerate(subject_chapters[selected_subject]) 
                    if chapter["title"] == st.session_state.selected_chapter
                )
                st.video(chapter_videos[selected_subject][chapter_index])
                
            except StopIteration:
                st.error("Selected chapter not found.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Create a scrollable container for transcript and chat
    scrollable_content = st.container()
    with scrollable_content:
        # Display transcript
        if selected_subject and st.session_state.selected_chapter:
            try:
                transcript = get_transcript(chapter_videos[selected_subject][chapter_index])
                stx.scrollableTextbox(transcript, height=200)
            except StopIteration:
                pass

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input and response section
    if prompt := st.chat_input("Ask your question here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Get current context (subject, chapter, and transcript)
        current_subject = selected_subject
        current_chapter = st.session_state.selected_chapter
        
        try:
            chapter_index = next(
                i for i, chapter in enumerate(subject_chapters[current_subject]) 
                if chapter["title"] == current_chapter
            )
            chapter_description = subject_chapters[current_subject][chapter_index]["description"]
            video_transcript = get_transcript(chapter_videos[current_subject][chapter_index])
        except:
            chapter_description = ""
            video_transcript = ""

        # Prepare the context for the AI with specific subject and chapter information
        context = f"""You are an expert tutor in {current_subject}, specifically teaching about {current_chapter}. 
        Chapter Description: {chapter_description}
        
        The student is currently watching a video about this topic. Here's the context from the video transcript:
        {video_transcript[:1000]}  # Using first 1000 characters of transcript for context
        
        Please provide clear, educational responses suitable for students learning this specific topic. 
        If using mathematical equations or technical terms, explain them clearly.
        Base your response on the specific chapter content and video material being discussed."""
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Include previous conversation context along with current context
                full_prompt = [
                    {"role": "system", "content": context},
                    *[msg for msg in st.session_state.messages[-5:]]  # Include last 5 messages for context
                ]
                
                # Create an empty placeholder
                message_placeholder = st.empty()
                # Initialize an empty string to store the full response
                full_response = ""
                
                # Stream the response
                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
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

