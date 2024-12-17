import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from auth import init_db, show_login_page
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse
import streamlit_scrollable_textbox as stx
import streamlit.components.v1 as components
from typing import List
import time

# Load environment variables from .env file
load_dotenv()

# Initialize the database
init_db()



def get_video_id(url):
    """Extract video ID from YouTube URL"""
    if 'embed/' in url:
        # Extract ID from embed URL
        return url.split('embed/')[-1].split('?')[0]
    elif 'youtu.be' in url:
        # Extract ID from youtu.be URL
        return url.split('/')[-1]
    else:
        # Extract ID from regular YouTube URL
        return url.split('/')[-1]

def get_transcript(video_url):
    """Get transcript of YouTube video with timestamps"""
    try:
        video_id = get_video_id(video_url)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # Keep the timestamp information
        return transcript_list
    except Exception as e:
        return f"Transcript not available: {str(e)}"

def create_video_player(video_id, height=450):
    """Create a video player with progress tracking"""
    # Add the greeting to session state messages when a new chapter is selected
    if 'messages' in st.session_state:
        current_subject = st.session_state.get('previous_subject')
        current_chapter = st.session_state.get('selected_chapter')
        previous_chapter = st.session_state.get('previous_chapter')
        
        # Only reset messages if the chapter has changed
        if previous_chapter != current_chapter:
            greeting_message = {
                "role": "assistant",
                "content": f"Welcome to the {current_chapter} lesson in {current_subject}! I'm your AI tutor, and I'm here to help you understand this topic. Feel free to ask any questions in any languages as you watch the video."
            }
            st.session_state.messages = [greeting_message]  # Reset messages and add greeting
            st.session_state.previous_chapter = current_chapter  # Update the previous chapter

    html_content = f"""
    <div id="video-container">
        <iframe id="youtube-iframe" 
                width="100%" 
                height="{height}" 
                src="https://www.youtube.com/embed/{video_id}?enablejsapi=1" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
        </iframe>
        <div id="progress-display" style="padding: 10px; background-color: #f0f2f6; border-radius: 5px; text-align: center; margin: 10px 0;">
            <span style="font-family: monospace; font-size: 24px; font-weight: bold;">Progress: 0%</span>
        </div>
    </div>
    
    <script>
        var tag = document.createElement('script');
        tag.src = "https://www.youtube.com/iframe_api";
        var firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
        
        var player;
        function onYouTubeIframeAPIReady() {{
            player = new YT.Player('youtube-iframe', {{
                events: {{
                    'onStateChange': onPlayerStateChange
                }}
            }});
        }}
        
        function onPlayerStateChange(event) {{
            if (event.data == YT.PlayerState.PLAYING) {{
                trackProgress();
            }}
        }}
        
        function trackProgress() {{
            var progressInterval = setInterval(function() {{
                if (player && player.getCurrentTime) {{
                    var currentTime = Math.ceil(player.getCurrentTime());
                    var duration = Math.ceil(player.getDuration());
                    var progressPercentage;
                    
                    // Check if we're at or very close to the end
                    if (duration - currentTime <= 0.1) {{
                        progressPercentage = 100;
                        clearInterval(progressInterval);
                    }} else {{
                        progressPercentage = (currentTime / duration * 100).toFixed(2);
                    }}
                    
                    // Update progress display
                    document.getElementById('progress-display').innerHTML = 
                        '<span style="font-family: monospace; font-size: 24px; font-weight: bold;">' +
                        'Progress: ' + progressPercentage + '% Current: '+ currentTime + 's Duration: '+ duration +'s'+'</span>';
                    
                    // Send current time and duration to Streamlit
                    window.parent.postMessage({{
                        type: 'video_time',
                        time: currentTime,
                        duration: duration,
                        progress: progressPercentage
                    }}, '*');
                }}
            }}, 1000);
        }}
    </script>
    """
    return components.html(html_content, height=height + 100)

def process_chat_stream(stream) -> str:
    """Process chat stream and return full response"""
    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
    return full_response




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
    if 'previous_chapter' not in st.session_state:
        st.session_state.previous_chapter = None
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = None

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
            "https://www.youtube.com/embed/NybHckSEQBI?enablejsapi=1",  # Algebra
            "https://www.youtube.com/embed/nwLEByAAqlM?enablejsapi=1",  # Geometry
            "https://www.youtube.com/embed/UukVP7Mg3TU?enablejsapi=1",  # Calculus
            "https://www.youtube.com/embed/sxQaBpKfDRk?enablejsapi=1",  # Statistics
            "https://www.youtube.com/embed/T9lt6MZKLck?enablejsapi=1"   # Trigonometry
        ],
        "Physics": [
            "https://www.youtube.com/embed/ZM8ECpBuQYE?enablejsapi=1",  # Mechanics
            "https://www.youtube.com/embed/4PkiGQEQ_Pw?enablejsapi=1",  # Thermodynamics
            "https://www.youtube.com/embed/x1-SibwIPM4?enablejsapi=1",  # Electromagnetism
            "https://www.youtube.com/embed/7BXvc9W97iU?enablejsapi=1",  # Optics
            "https://www.youtube.com/embed/Q1YqgPAtzho?enablejsapi=1"   # Quantum Physics
        ],
        "Chemistry": [
            "https://www.youtube.com/embed/bka20Q9TN6M?enablejsapi=1",  # Organic Chemistry
            "https://www.youtube.com/embed/6pUzPh_lCO8?enablejsapi=1",  # Inorganic Chemistry
            "https://www.youtube.com/embed/cyhxvQN8SQ4?enablejsapi=1",  # Physical Chemistry
            "https://www.youtube.com/embed/FSyAehMdpyI?enablejsapi=1",  # Analytical Chemistry
            "https://www.youtube.com/embed/lJKNDXXV3vE?enablejsapi=1"   # Biochemistry
        ],
        "Biology": [
            "https://www.youtube.com/embed/URUJD5NEXC8?enablejsapi=1",  # Cell Biology
            "https://www.youtube.com/embed/v8tJGlicgp8?enablejsapi=1",  # Genetics
            "https://www.youtube.com/embed/GhHOjC4oxh8?enablejsapi=1", # Evolution
            "https://www.youtube.com/embed/9dAcEBXAFoo?enablejsapi=1",  # Ecology
            "https://www.youtube.com/embed/Ae4MadKPJC0?enablejsapi=1"   # Human Anatomy
        ],
        "History": [
            "https://www.youtube.com/embed/wX6J0Gd2EC8?enablejsapi=1",  # Ancient Civilizations
            "https://www.youtube.com/embed/H5AVPmAZ8o8?enablejsapi=1",  # Middle Ages
            "https://www.youtube.com/embed/Vufba_ZcoR0?enablejsapi=1",  # Renaissance
            "https://www.youtube.com/embed/kUWEYLVooxU?enablejsapi=1",  # Modern History
            "https://www.youtube.com/embed/T5PwyuzSYcs?enablejsapi=1"  # Contemporary History
        ],
        "Literature": [
            "https://www.youtube.com/embed/drPoZMqHTAw?enablejsapi=1",  # Poetry
            "https://www.youtube.com/embed/3CvJKTChsl4?enablejsapi=1",  # Drama
            "https://www.youtube.com/embed/QrUPneyZNf0?enablejsapi=1",  # Fiction
            "https://www.youtube.com/embed/QrUPneyZNf0?enablejsapi=1",  # Non-Fiction
            "https://www.youtube.com/embed/3naf-KE0uvI?enablejsapi=1"   # Literary Criticism
        ],
        "Computer Science": [
            "https://www.youtube.com/embed/l26oaHV7D40?enablejsapi=1",  # Programming Basics
            "https://www.youtube.com/embed/DuDz6B4cqVc?enablejsapi=1",  # Data Structures
            "https://www.youtube.com/embed/rL8X2mlNHPM?enablejsapi=1",  # Algorithms
            "https://www.youtube.com/embed/ysEN5RaKOlA?enablejsapi=1",  # Web Development
            "https://www.youtube.com/embed/PeMlggyqz0Y?enablejsapi=1"  # Machine Learning
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
    st.subheader(f"EDUSPHERE: {selected_subject} - {st.session_state.selected_chapter}")
    
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
                
                video_url = chapter_videos[selected_subject][chapter_index]
                video_id = get_video_id(video_url)
                create_video_player(video_id)

                # Get transcript data
                transcript_data = get_transcript(video_url)
                
            except StopIteration:
                st.error("Selected chapter not found.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Create a scrollable container for transcript and chat
    scrollable_content = st.container()
    with scrollable_content:
        # Display transcript
        if selected_subject and st.session_state.selected_chapter:
            try:
                transcript_data = get_transcript(chapter_videos[selected_subject][chapter_index])
                if isinstance(transcript_data, list):
                    # Get current video time from session state
                    current_time = st.session_state.get('video_time_update', {}).get('time', 0)
                    
                    # Create HTML for transcript with highlighting
                    transcript_html = ""
                    for i, segment in enumerate(transcript_data):
                        # Convert timestamp to minutes:seconds format
                        minutes = int(segment['start'] // 60)
                        seconds = int(segment['start'] % 60)
                        timestamp = f"[{minutes:02d}:{seconds:02d}]"
                        
                        # Determine if this is the current segment
                        is_current = False
                        if i < len(transcript_data) - 1:
                            if segment['start'] <= current_time < transcript_data[i + 1]['start']:
                                is_current = True
                        else:
                            if segment['start'] <= current_time:
                                is_current = True
                        
                        # Add segment with appropriate styling
                        segment_class = "transcript-segment" + (" current-segment" if is_current else "")
                        transcript_html += f'<div class="{segment_class}">{timestamp} {segment["text"]}</div>'
                    
                    st.markdown("""### 📜Transcript""")
                    
                    # Display transcript using HTML
                    st.markdown(
                        f'<div style="height: 100px; overflow-y: auto; margin-bottom: 50px;">{transcript_html}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    # Handle case where transcript is an error message
                    st.error(str(transcript_data))
            except StopIteration:
                pass

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            # Add Quiz expander after the welcome message
            if message == st.session_state.messages[0]:  # If it's the first (welcome) message
                # Create quiz section in an expander
                quiz_expander = st.expander("Chapter Quiz", expanded=False)
                with quiz_expander:
                    current_subject = st.session_state.get('previous_subject')
                    current_chapter = st.session_state.selected_chapter
                    
                    # Generate quiz only if it doesn't exist for current chapter or chapter has changed
                    if (st.session_state.quiz_data is None or 
                        st.session_state.quiz_data.get('chapter') != current_chapter):
                        
                        try:
                            chapter_index = next(
                                i for i, chapter in enumerate(subject_chapters[current_subject]) 
                                if chapter["title"] == current_chapter
                            )
                            transcript_data = get_transcript(chapter_videos[current_subject][chapter_index])
                            
                            if isinstance(transcript_data, list):
                                # Combine transcript text for context
                                transcript_text = " ".join([segment["text"] for segment in transcript_data])
                                
                                # Generate quiz context for GPT
                                quiz_context = f"""You are a {current_subject} lecturer teaching about {current_chapter}.
                                Based on this lesson content:
                                {transcript_text[:1000]}
                                
                                Generate a natural-sounding multiple choice question that a lecturer would ask to test understanding of a key concept.
                                Format the response as follows:
                                QUESTION: [Your question here]
                                A: [First option]
                                B: [Second option]
                                C: [Third option]
                                D: [Fourth option]
                                
                                Make the question sound natural as if asked in a classroom setting.
                                Do not mention transcripts or videos in the question."""
                                
                                # Generate question using GPT
                                quiz_response = client.chat.completions.create(
                                    model="gpt-4o-mini",
                                    messages=[{"role": "system", "content": quiz_context}],
                                    temperature=0.7
                                ).choices[0].message.content
                                
                                # Split the response into question and options
                                response_parts = quiz_response.split('\n')
                                question = response_parts[0].replace('QUESTION: ', '')
                                options = [opt.split(': ')[1] for opt in response_parts[1:5]]
                                
                                # Generate key terms
                                key_terms_context = f"""As a {current_subject} lecturer teaching about {current_chapter},
                                based on this lesson content:
                                {transcript_text[:1000]}
                                
                                List 4 key terms or concepts that were covered in the lesson.
                                Make sure each term is a single line and clearly relevant to {current_chapter}."""
                                
                                key_terms_response = client.chat.completions.create(
                                    model="gpt-4o-mini",
                                    messages=[{"role": "system", "content": key_terms_context}],
                                    temperature=0.7
                                ).choices[0].message.content.split('\n')
                                
                                # Store quiz data in session state
                                st.session_state.quiz_data = {
                                    'chapter': current_chapter,
                                    'question': question,
                                    'options': options,
                                    'key_terms': key_terms_response
                                }
                            else:
                                st.error("Could not generate quiz: Transcript not available")
                                
                        except Exception as e:
                            st.error(f"Could not generate quiz: {str(e)}")
                    
                    # Display quiz using stored data
                    if st.session_state.quiz_data and st.session_state.quiz_data['chapter'] == current_chapter:
                        st.header(f"Quiz: {current_chapter}")
                        
                        # Question 1 - Generated from transcript
                        st.markdown("**Question 1:**")
                        st.write(st.session_state.quiz_data['question'])
                        q1 = st.radio(
                            f"Choose your answer",
                            st.session_state.quiz_data['options'],
                            key="q1"
                        )
                        
                        # Question 2 - Open-ended reflection
                        st.markdown("**Question 2:**")
                        st.write(f"What is the most important concept you learned about {current_chapter}?")
                        q2 = st.text_input(
                            "Your answer:",
                            key="q2"
                        )
                        
                        # Question 3 - Key terms from transcript
                        st.markdown("**Question 3:**")
                        st.write("Select all key terms that were covered in this lesson:")
                        q3 = st.multiselect(
                            "Select terms:",
                            st.session_state.quiz_data['key_terms'],
                            key="q3"
                        )
                        
                        if st.button("Submit Quiz", key="submit_quiz"):
                            st.success("Quiz submitted successfully!")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "Great job completing the quiz! Do you have any questions about the topics covered?"
                            })
                            st.rerun()

    # Chat input and response section
    if 'processing' not in st.session_state:
        st.session_state.processing = False

    if prompt := st.chat_input("Ask your question here...", key="chat_input"):
        # Disable the input while processing
        st.session_state.processing = True
        
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

        # Prepare the context
        context = f"""You are an expert tutor in {current_subject}, specifically teaching about {current_chapter}. 
        Chapter Description: {chapter_description}
        
        The student is currently watching a video about this topic. Here's the context from the video transcript:
        {video_transcript[:1000]}
        
        Please provide clear, educational responses suitable for students learning this specific topic."""
        
        # Generate AI response
        full_prompt = [
            {"role": "system", "content": context},
            *[msg for msg in st.session_state.messages[-5:]]
        ]
        
        with st.chat_message("assistant"):
            try:
                # Show temporary "thinking" message
                thinking_placeholder = st.empty()
                thinking_placeholder.write("Thinking...")
                
                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": m["role"], "content": m["content"]} for m in full_prompt],
                    temperature=0.7,
                    stream=True,
                )
                
                response = process_chat_stream(stream)
                
                # Clear thinking message and show response
                thinking_placeholder.empty()
                st.write(response)
                
                # Add AI response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
            
            finally:
                # Re-enable the input
                st.session_state.processing = False

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
        .transcript-segment {
            padding: 5px;
            margin: 2px 0;
            border-radius: 4px;
            transition: background-color 0.3s ease;
        }
        .current-segment {
            background-color: #ffd700;
            font-weight: bold;
        }
        /* Smooth transitions for chat messages */
        .stChatMessage {
            transition: all 0.3s ease-out;
        }
        
        /* Improve chat input visibility */
        .stChatInputContainer {
            padding: 10px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Disable chat input while processing */
        .stChatInputContainer.processing {
            opacity: 0.7;
            pointer-events: none;
        }
    </style>
    """, unsafe_allow_html=True)

