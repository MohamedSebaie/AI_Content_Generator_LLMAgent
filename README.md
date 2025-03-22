# AI Content Generation Agent

An intelligent automation system that discovers trending AI topics, generates high-quality blog posts with minimal human supervision, and produces publication-ready content with custom visuals and responsive HTML formatting.

## 🚀 Overview

This project implements a sophisticated LangGraph-orchestrated workflow that:

1. Discovers current AI trends using web search and LLM analysis
2. Allows human selection of topics via a Streamlit interface
3. Researches selected topics in depth using multiple sources
4. Generates well-structured, comprehensive blog content
5. Refines that content through multiple iterations of self-critique  
6. Creates custom AI-generated images tailored to each article
7. Formats everything into responsive HTML ready for publication

## ✨ Key Features

- **AI Trend Discovery**: Automatically identifies and analyzes current AI topics using the Google Serper API and Claude's reasoning
- **Streamlit Interface**: Clean, intuitive UI for topic selection and workflow interaction
- **Research-Backed Content**: Incorporates data from multiple web sources to create comprehensive articles
- **Self-Critique & Refinement**: Implements up to 4 cycles of criticism and improvement
- **Custom Visuals**: Creates context-aware images using Stable Diffusion XL
- **Responsive HTML**: Formats content into publication-ready pages with professional styling
- **LangGraph Orchestration**: Modular, maintainable state machine architecture

## 🛠️ Technology Stack

- **Large Language Model**: AWS Bedrock with Claude 3.5 Sonnet for content generation and refinement
- **Image Generation**: Hugging Face Stable Diffusion XL for custom visuals
- **Web Research**: Google Serper API for topic discovery and research
- **Workflow Orchestration**: LangGraph for state management and component coordination
- **User Interface**: Streamlit for interactive topic selection and result display
- **Content Parsing**: BeautifulSoup for web content extraction and analysis

## 📋 Requirements

- Python 3.8+
- AWS account with Bedrock access for Claude 3 Sonnet
- API credentials:
  - AWS credentials (access key, secret key, region)
  - Google Serper API key (for web search)
  - Hugging Face API key (for image generation)
- (Optional) GPU access for faster image generation

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/MohamedSebaie/AI_Content_Generator_LLMAgent.git
cd AI_Content_Generator_LLMAgent
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
Create a `.env` file in the project root with your API keys:
```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
SERPER_API_KEY=your_serper_api_key
HF_API_TOKEN=your_huggingface_api_key
```

## 📊 Usage

### Streamlit Interface (Recommended)

Run the Streamlit application for a full GUI experience:

```bash
streamlit run streamlit_app.py
```

This provides an intuitive interface to:
- Discover trending topics
- Select your preferred topic
- Monitor the content generation process
- Review the refinement iterations
- View the final blog post with image
- Download the HTML output and images

### Command Line Interface

Alternatively, use the command line:

```bash
python main.py
```

This will:
1. Discover trending topics and show them in the console
2. Prompt you to select a topic
3. Run the complete workflow
4. Save the HTML output to the `outputs` directory

## 📂 Project Structure

```
ai_content_generator/
├── agents/                   # Specialized AI agents
│   ├── content_generator.py  # Generates initial blog content
│   ├── critique_refiner.py   # Self-critique and refinement
│   ├── image_generator.py    # Image generation and processing
│   └── topic_discovery.py    # Trending topic discovery
│
├── utils/                    # Utility functions and integrations
│   ├── bedrock_client.py     # AWS Bedrock API client
│   ├── html_generator.py     # HTML formatting and template engine
│   ├── prompt_templates.py   # Prompt engineering templates
│   ├── stable_diffusion_client.py  # Image generation client
│   └── web_scraper.py        # Web search and content extraction
│
├── workflows/                # LangGraph workflow definitions
│   └── content_workflow.py   # Main state machine orchestration
│
├── outputs/                  # Generated content storage
├── .env                      # Environment variables (create this)
├── config.py                 # Configuration settings
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
└── streamlit_app.py          # Streamlit UI entry point
```

## 🔄 Workflow Process

1. **Topic Discovery**: Searches the web for current AI trends and analyzes them
2. **Topic Selection**: User selects a topic through the Streamlit interface
3. **Research**: Gathers in-depth information from multiple web sources
4. **Content Generation**: Creates structured, informative initial content
5. **Refinement**: Multiple iterations of self-critique and improvement
6. **Image Generation**: Creates a custom visual based on content analysis
7. **HTML Generation**: Formats everything into responsive HTML

## 🎨 Customization

The system can be customized through parameters in `config.py`:

- **LLM Configuration**: Temperature, token limits, model selection
- **Content Style**: Number of refinement iterations, blog post length
- **Image Settings**: Model selection, image dimensions
- **Web Research**: Search parameters, request settings

## 🧪 Example Output

Check the `outputs/` directory for sample HTML files and images. The generated content includes:

- Well-structured blog post with title, introduction, and multiple sections
- Custom AI-generated image relevant to the topic
- Responsive HTML with professional styling
- Meta information like publication date and keywords

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

[MIT License](LICENSE)

---

## Acknowledgments

This project uses several powerful AI technologies including AWS Bedrock (Claude 3.5 Sonnet), Hugging Face Stable Diffusion, and Google's search APIs. Thanks to the developers of these technologies and the LangChain/LangGraph ecosystem.
