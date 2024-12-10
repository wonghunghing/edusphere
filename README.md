# 🎓 Edusphere Educational

An interactive educational assistant built with Streamlit. This chatbot provides personalized tutoring across multiple subjects with an engaging visual interface.

## 🌟 Features

- **Multi-subject Support**: Choose from various subjects including:
  - Mathematics
  - Physics
  - Chemistry
  - Biology
  - History
  - Literature
  - Computer Science

- **Interactive Interface**:
  - Real-time chat functionality
  - Subject-specific visuals
  - Educational videos for each topic
  - Responsive design

- **Smart Tutoring**:
  - Context-aware responses
  - Educational explanations
  - Subject matter expertise

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- OpenAI API key
- Streamlit

### Installation

1. Clone the repository:

git clone https://github.com/wonghunghing/edusphere.git

2. Install required packages:


pip install -r requirements.txt


3. Create a `.env` file in the project root and add your OpenAI API key:


4. Run the application:

streamlit run main.py --server.port 8501

5. Build the Docker image:

docker build -t edusphere .

6. Run the Docker container:

docker run --name edusphere -p 8501:8501 edusphere

## 🔧 Configuration

The application uses environment variables for configuration. Make sure to set up your `.env` file with the necessary API keys and configurations.

## 💻 Usage

1. Select a subject from the sidebar dropdown
2. View the subject-specific image and educational video
3. Ask questions in the chat interface
4. Receive detailed, educational responses from the AI tutor

## 📚 Project Structure

educational-chatbot/
├── main.py # Main application file
├── .env # Environment variables
├── requirements.txt # Project dependencies
└── README.md # Project documentation



## 📋 Requirements

- streamlit
- openai
- python-dotenv

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenAI
- Streamlit for the web framework
- Freepik for the subject images
- Various educational content providers for the embedded videos

---

Made with ❤️ by unrestrictable
