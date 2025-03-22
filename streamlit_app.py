import os
import sys
import logging
import streamlit as st # type: ignore
import time
from PIL import Image
from io import BytesIO
import base64
from dotenv import load_dotenv # type: ignore

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="AI Content Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add project root to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.topic_discovery import TopicDiscoveryAgent
from agents.content_generator import ContentGeneratorAgent
from agents.critique_refiner import CritiqueRefinerAgent
from agents.image_generator import ImageGeneratorAgent
from utils.html_generator import HtmlGenerator
from config import validate_credentials, OUTPUT_DIR

# Fix encoding issues for logging on Windows
import codecs
# Try to use utf-8 encoding for sys.stdout
try:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
except AttributeError:
    # If that fails, just continue
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("streamlit_app.log", encoding='utf-8'),  # Specify UTF-8 encoding
        logging.StreamHandler()  # This will use the utf-8 encoding we set above
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check credentials
missing_credentials = validate_credentials()
if missing_credentials:
    st.error(f"Missing required credentials: {', '.join(missing_credentials)}")
    st.info("Please set these environment variables in a .env file or your environment.")
    st.stop()

# Initialize agents
@st.cache_resource
def load_agents():
    return {
        "topic_agent": TopicDiscoveryAgent(),
        "content_agent": ContentGeneratorAgent(),
        "critique_agent": CritiqueRefinerAgent(),
        "image_agent": ImageGeneratorAgent(),
        "html_generator": HtmlGenerator()
    }

agents = load_agents()

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4A6FE3;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #8142DB;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #eee;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4A6FE3;
        margin-bottom: 1rem;
    }
    .topic-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #eee;
        transition: transform 0.2s;
    }
    .topic-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    }
    .topic-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #8142DB;
        margin-bottom: 0.5rem;
    }
    .topic-description {
        color: #333;
        margin-bottom: 0.5rem;
    }
    .topic-trending {
        color: #666;
        font-style: italic;
        margin-bottom: 0.5rem;
    }
    .keyword-pill {
        display: inline-block;
        background-color: #E2E8F7;
        color: #4A6FE3;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.8rem;
    }
    .step-container {
        display: flex;
        margin-bottom: 1rem;
    }
    .step-number {
        background-color: #4A6FE3;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        flex-shrink: 0;
    }
    .step-content {
        flex-grow: 1;
    }
    .critique-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #8142DB;
        margin-bottom: 1rem;
    }
    .final-content {
        background-color: #fff;
        padding: 2rem;
        border-radius: 0.5rem;
        border: 1px solid #eee;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .button-container {
        display: flex;
        justify-content: center;
        margin-top: 2rem;
    }
    .log-container {
        background-color: #f0f0f0;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        max-height: 200px;
        overflow-y: auto;
        font-family: monospace;
        font-size: 0.8rem;
    }
    .log-info {
        color: #1E90FF;
    }
    .log-error {
        color: #FF4500;
    }
    .log-success {
        color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to display trending topic cards
def display_topic_card(topic, index):
    with st.container():
        col1, col2 = st.columns([1, 20])
        with col1:
            st.markdown(f"<div style='background-color: #4A6FE3; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-top: 20px;'>{index}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='topic-box'>", unsafe_allow_html=True)
            st.markdown(f"<div class='topic-title'>{topic.get('title', 'Unnamed Topic')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='topic-description'>{topic.get('description', 'No description available')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='topic-trending'><strong>Why Trending:</strong> {topic.get('why_trending', 'No information available')}</div>", unsafe_allow_html=True)
            
            keywords = topic.get('keywords', [])
            keyword_html = ""
            for keyword in keywords:
                keyword_html += f"<span class='keyword-pill'>{keyword}</span>"
            st.markdown(f"<div>{keyword_html}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# Helper function to view generated images
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logger.error(f"Error reading image {image_path}: {str(e)}")
        return ""

# Helper function to display logs in a nice format
def display_log(message, log_type="info"):
    css_class = f"log-{log_type}"
    st.markdown(f"<div class='{css_class}'>{message}</div>", unsafe_allow_html=True)

# Main app components
def main():
    # Header
    st.markdown("<h1 class='main-header'>AI Content Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Generate high-quality AI blog posts on trending topics with just a few clicks</p>", unsafe_allow_html=True)
    
    # Initialize session state
    if 'stage' not in st.session_state:
        st.session_state.stage = 'discover'
    if 'topics' not in st.session_state:
        st.session_state.topics = None
    if 'selected_topic' not in st.session_state:
        st.session_state.selected_topic = None
    if 'content' not in st.session_state:
        st.session_state.content = None
    if 'refined_content' not in st.session_state:
        st.session_state.refined_content = None
    if 'refinement_history' not in st.session_state:
        st.session_state.refinement_history = []
    if 'final_content' not in st.session_state:
        st.session_state.final_content = None
    if 'html_output' not in st.session_state:
        st.session_state.html_output = None
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    
    # Sidebar for workflow navigation and status
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=80)
        st.markdown("## Workflow Status")
        
        # Display progress based on current stage
        stages = ['discover', 'select', 'generate', 'refine', 'visualize', 'finalize']
        stage_names = ['Topic Discovery', 'Topic Selection', 'Content Generation', 'Content Refinement', 'Image Generation', 'HTML Creation']
        current_stage_idx = stages.index(st.session_state.stage)
        
        for i, (stage, name) in enumerate(zip(stages, stage_names)):
            if i < current_stage_idx:
                st.success(name)
            elif i == current_stage_idx:
                st.info(name + " (Current)")
            else:
                st.text(name)
        
        # Log display
        st.markdown("## Process Logs")
        log_container = st.container()
        with log_container:
            st.markdown("<div class='log-container'>", unsafe_allow_html=True)
            for log in st.session_state.logs[-10:]:  # Show only the last 10 logs
                display_log(log['message'], log['type'])
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Reset button
        if st.button("Start Over", key='reset'):
            st.session_state.stage = 'discover'
            st.session_state.topics = None
            st.session_state.selected_topic = None
            st.session_state.content = None
            st.session_state.refined_content = None
            st.session_state.refinement_history = []
            st.session_state.final_content = None
            st.session_state.html_output = None
            st.session_state.logs = []
            st.rerun()
    
    # Helper function to add logs - WITHOUT emojis to avoid encoding issues
    def add_log(message, log_type="info"):
        # Remove emojis from the message for logger
        clean_message = message
        # Add to session state with original message
        st.session_state.logs.append({"message": message, "type": log_type})
        # Log the clean message
        logger.info(clean_message)
    
    # Main content area - changes based on current stage
    if st.session_state.stage == 'discover':
        st.markdown("<h2 class='section-header'>Trending Topic Discovery</h2>", unsafe_allow_html=True)
        
        st.markdown("<div class='info-box'><p>The AI agent will search the web for currently trending topics in artificial intelligence.</p></div>", unsafe_allow_html=True)
        
        if st.button("Discover Trending Topics", key="discover_btn"):
            with st.spinner("Searching for trending AI topics..."):
                try:
                    add_log("Starting trending topic discovery...", "info")
                    
                    st.session_state.topics = agents["topic_agent"].discover_trending_topics()
                    
                    add_log(f"Successfully discovered {len(st.session_state.topics)} trending topics", "success")
                    st.session_state.stage = 'select'
                    st.rerun()
                except Exception as e:
                    add_log(f"Error discovering topics: {str(e)}", "error")
                    st.error(f"Error discovering topics: {str(e)}")
                    logger.error(f"Error discovering topics: {str(e)}", exc_info=True)
    
    elif st.session_state.stage == 'select':
        st.markdown("<h2 class='section-header'>Topic Selection</h2>", unsafe_allow_html=True)
        
        st.markdown("<div class='info-box'><p>Select a trending topic that you'd like to generate content for.</p></div>", unsafe_allow_html=True)
        
        if st.session_state.topics:
            for i, topic in enumerate(st.session_state.topics):
                display_topic_card(topic, i+1)
                if st.button(f"Select Topic {i+1}", key=f"select_topic_{i}"):
                    st.session_state.selected_topic = topic
                    add_log(f"Selected topic: {topic.get('title', '')}", "info")
                    st.session_state.stage = 'generate'
                    st.rerun()
        else:
            st.warning("No topics found. Please go back and try topic discovery again.")
            if st.button("Back to Topic Discovery"):
                st.session_state.stage = 'discover'
                st.rerun()
    
    elif st.session_state.stage == 'generate':
        st.markdown("<h2 class='section-header'>Content Generation</h2>", unsafe_allow_html=True)
        
        selected_topic = st.session_state.selected_topic
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>Selected Topic:</strong> {selected_topic.get('title', '')}</p>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>Description:</strong> {selected_topic.get('description', '')}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Option for full workflow or step-by-step
        generate_options = st.radio(
            "Choose generation mode:",
            ["Generate all in one go (Content, Refinement, Image)", "Step-by-step generation"]
        )
        
        if st.session_state.content is None:
            if st.button("Begin Generation", key="generate_btn"):
                if generate_options == "Generate all in one go (Content, Refinement, Image)":
                    # Run the entire workflow in one go
                    try:
                        # 1. Research and generate content
                        add_log("Researching topic details...", "info")
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        status_text.text("Researching and gathering information...")
                        research_data = agents["topic_agent"].get_detailed_research(selected_topic)
                        topic_data = {"topic": selected_topic, "research_data": research_data}
                        
                        add_log("Research completed", "success")
                        progress_bar.progress(0.15)
                        
                        # 2. Generate initial content
                        status_text.text("Generating initial blog post content...")
                        add_log("Generating initial blog content...", "info")
                        
                        content_data = agents["content_agent"].generate_content(topic_data)
                        st.session_state.content = content_data
                        
                        add_log(f"Initial content generated: '{content_data.get('title', '')}'", "success")
                        progress_bar.progress(0.30)
                        
                        # 3. Refine content through iterations
                        status_text.text("Refining content through multiple iterations...")
                        add_log("Starting content refinement process...", "info")
                        
                        # Initialize with original content
                        current_content = content_data.get("content", "")
                        title = content_data.get("title", "")
                        refinement_history = []
                        
                        # Track iterations (maximum 4)
                        for iteration in range(4):
                            status_text.text(f"Iteration {iteration+1}/4: Generating critique...")
                            add_log(f"Refinement iteration {iteration+1}/4: Generating critique...", "info")
                            
                            # Generate critique
                            critique = agents["critique_agent"].critique_content(current_content)
                            
                            # Store the critique
                            refinement_history.append({
                                "iteration": iteration + 1,
                                "critique": critique
                            })
                            
                            progress_bar.progress(0.30 + (iteration * 0.05))
                            
                            # Skip refinement on the last iteration
                            if iteration < 3:
                                status_text.text(f"Iteration {iteration+1}/4: Refining content based on critique...")
                                add_log(f"Refinement iteration {iteration+1}/4: Implementing improvements...", "info")
                                
                                # Refine content based on critique
                                refined_content = agents["critique_agent"].refine_content(current_content, critique)
                                
                                # Update current content for next iteration
                                current_content = refined_content
                                
                                # Store the refined content
                                refinement_history[-1]["refined_content"] = refined_content
                            
                            progress_bar.progress(0.30 + (iteration * 0.05) + 0.025)
                            time.sleep(0.2)  # Small delay for UI feedback
                        final_content = agents["critique_agent"].finalize_content(current_content, title)
                        # Store final refined content
                        st.session_state.refined_content = {
                            "topic": content_data.get("topic", {}),
                            "title": title,
                            "content": final_content,  # This is the final version
                            "keywords": content_data.get("keywords", []),
                            "refinement_history": refinement_history
                        }
                        
                        st.session_state.refinement_history = refinement_history
                        add_log("Content refinement completed", "success")
                        progress_bar.progress(0.60)
                        
                        # 4. Generate image
                        status_text.text("Generating image for the blog post...")
                        add_log("Generating accompanying image...", "info")
                        
                        final_content = agents["image_agent"].process_content_for_image(st.session_state.refined_content)
                        st.session_state.final_content = final_content
                        
                        add_log(f"Image generated: {final_content.get('image_filename', '')}", "success")
                        progress_bar.progress(0.85)
                        
                        # 5. Generate HTML
                        status_text.text("Creating final HTML blog post...")
                        add_log("Generating HTML for the blog post...", "info")
                        
                        title = final_content.get("title", "AI Technology")
                        content = final_content.get("content", "")
                        image_path = final_content.get("image_path", "")
                        image_description = final_content.get("image_description", "")
                        
                        add_log(f"Using image: {image_path}", "info")
                        
                        html_content = agents["html_generator"].generate_html(
                            title=title,
                            content=content,
                            image_path=image_path,
                            image_alt=image_description,
                            image_caption=image_description
                        )
                        
                        html_path = agents["html_generator"].save_html(html_content)
                        st.session_state.html_output = {
                            "content": html_content,
                            "path": html_path
                        }
                        
                        add_log(f"HTML blog post created: {html_path}", "success")
                        progress_bar.progress(1.0)
                        status_text.text("Blog post successfully generated!")
                        
                        # Go to the final stage
                        st.session_state.stage = 'finalize'
                        st.rerun()
                        
                    except Exception as e:
                        add_log(f"Error during generation: {str(e)}", "error")
                        st.error(f"Error during generation: {str(e)}")
                        logger.error(f"Error during generation: {str(e)}", exc_info=True)
                else:
                    # Just do content generation for step-by-step approach
                    with st.spinner("Researching and generating content..."):
                        try:
                            add_log("Researching topic details...", "info")
                            # First research the topic
                            research_data = agents["topic_agent"].get_detailed_research(selected_topic)
                            topic_data = {"topic": selected_topic, "research_data": research_data}
                            
                            add_log("Generating blog content...", "info")
                            # Then generate content
                            content_data = agents["content_agent"].generate_content(topic_data)
                            st.session_state.content = content_data
                            
                            add_log(f"Content generated: '{content_data.get('title', '')}'", "success")
                            st.session_state.stage = 'refine'
                            st.rerun()
                        except Exception as e:
                            add_log(f"Error generating content: {str(e)}", "error")
                            st.error(f"Error generating content: {str(e)}")
                            logger.error(f"Error generating content: {str(e)}", exc_info=True)
        else:
            st.markdown("<div class='final-content'>", unsafe_allow_html=True)
            st.markdown(f"<h2>{st.session_state.content.get('title', '')}</h2>", unsafe_allow_html=True)
            st.markdown(st.session_state.content.get('content', ''), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Back to Topic Selection", key="back_to_topics"):
                    st.session_state.content = None
                    st.session_state.stage = 'select'
                    st.rerun()
            with col2:
                if st.button("Proceed to Refinement", key="to_refinement"):
                    st.session_state.stage = 'refine'
                    st.rerun()
    
    elif st.session_state.stage == 'refine':
        st.markdown("<h2 class='section-header'>Content Refinement</h2>", unsafe_allow_html=True)
        
        if not st.session_state.refined_content:
            st.markdown("<div class='info-box'><p>The AI will now refine the content through 4 iterations of self-critique and improvement.</p></div>", unsafe_allow_html=True)
            
            if st.button("Start Refinement Process", key="refine_btn"):
                with st.spinner("Refining content through multiple iterations..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        add_log("Starting content refinement process...", "info")
                        
                        # Initialize with original content
                        content_data = st.session_state.content
                        current_content = content_data.get("content", "")
                        title = content_data.get("title", "")
                        refinement_history = []
                        
                        # Track iterations (maximum 4)
                        for iteration in range(4):
                            status_text.text(f"Iteration {iteration+1}/4: Generating critique...")
                            add_log(f"Refinement iteration {iteration+1}/4: Generating critique...", "info")
                            
                            # Generate critique
                            critique = agents["critique_agent"].critique_content(current_content)
                            
                            # Store the critique
                            refinement_history.append({
                                "iteration": iteration + 1,
                                "critique": critique
                            })
                            
                            progress_bar.progress((iteration * 2 + 1) / 8)
                            
                            # Skip refinement on the last iteration
                            if iteration < 3:
                                status_text.text(f"Iteration {iteration+1}/4: Refining content based on critique...")
                                add_log(f"Refinement iteration {iteration+1}/4: Implementing improvements...", "info")
                                
                                # Refine content based on critique
                                refined_content = agents["critique_agent"].refine_content(current_content, critique)
                                
                                # Update current content for next iteration
                                current_content = refined_content
                                
                                # Store the refined content
                                refinement_history[-1]["refined_content"] = refined_content
                            
                            progress_bar.progress((iteration * 2 + 2) / 8)
                            time.sleep(0.2)  # Small delay for UI feedback
                        # Perform final formatting before returning
                        final_content = agents["critique_agent"].finalize_content(current_content, title)
                        # Store final results
                        st.session_state.refined_content = {
                            "topic": content_data.get("topic", {}),
                            "title": title,
                            "content": final_content,  # This is the final version
                            "keywords": content_data.get("keywords", []),
                            "refinement_history": refinement_history
                        }
                        
                        st.session_state.refinement_history = refinement_history
                        add_log("Content refinement completed", "success")
                        st.session_state.stage = 'visualize'
                        st.rerun()
                        
                    except Exception as e:
                        add_log(f"Error during refinement: {str(e)}", "error")
                        st.error(f"Error during refinement: {str(e)}")
                        logger.error(f"Error during refinement: {str(e)}", exc_info=True)
        else:
            # Display refinement iterations
            st.markdown("<div class='info-box'><p>Content has been refined through multiple iterations. Review the process below.</p></div>", unsafe_allow_html=True)
            
            tabs = st.tabs(["Original"] + [f"Iteration {i+1}" for i in range(len(st.session_state.refinement_history))])
            
            # Show original content
            with tabs[0]:
                st.markdown(f"<h3>{st.session_state.content.get('title', '')}</h3>", unsafe_allow_html=True)
                st.markdown(st.session_state.content.get('content', ''), unsafe_allow_html=True)
            
            # Show each iteration
            for i, iteration in enumerate(st.session_state.refinement_history):
                with tabs[i+1]:
                    st.markdown("<div class='critique-box'>", unsafe_allow_html=True)
                    st.markdown("### Critique")
                    st.markdown(iteration.get("critique", ""))
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if "refined_content" in iteration:
                        st.markdown("### Refined Content")
                        st.markdown(iteration.get("refined_content", ""))
                    else:
                        st.info("This was the final critique iteration.")
            
            if st.button("Proceed to Image Generation", key="to_visualization"):
                st.session_state.stage = 'visualize'
                st.rerun()
    
    elif st.session_state.stage == 'visualize':
        st.markdown("<h2 class='section-header'>Image Generation</h2>", unsafe_allow_html=True)
        
        if not st.session_state.final_content:
            st.markdown("<div class='info-box'><p>The AI will now generate an appropriate image to accompany your blog post.</p></div>", unsafe_allow_html=True)
            
            if st.button("Generate Image", key="image_btn"):
                with st.spinner("Creating image for your content..."):
                    try:
                        add_log("Generating image for blog post...", "info")
                        final_content = agents["image_agent"].process_content_for_image(st.session_state.refined_content)
                        st.session_state.final_content = final_content
                        
                        add_log(f"Image generated: {final_content.get('image_filename', '')}", "success")
                        st.session_state.stage = 'finalize'
                        st.rerun()
                    except Exception as e:
                        add_log(f"Error generating image: {str(e)}", "error")
                        st.error(f"Error generating image: {str(e)}")
                        logger.error(f"Error generating image: {str(e)}", exc_info=True)
        else:
            # Should not normally reach here, but just in case
            st.info("Image already generated. Proceeding to final output.")
            st.session_state.stage = 'finalize'
            st.rerun()
    
    elif st.session_state.stage == 'finalize':
        st.markdown("<h2 class='section-header'>Final Blog Post</h2>", unsafe_allow_html=True)
        
        final_content = st.session_state.final_content
        
        # Generate HTML if not already done
        if not st.session_state.html_output:
            try:
                add_log("Generating HTML for blog post...", "info")
                
                title = final_content.get("title", "AI Technology")
                content = final_content.get("content", "")
                image_path = final_content.get("image_path", "")
                image_description = final_content.get("image_description", "")
                
                add_log(f"Using image: {image_path}", "info")
                
                # Generate HTML content
                html_content = agents["html_generator"].generate_html(
                    title=title,
                    content=content,
                    image_path=image_path.split("/")[-1],
                    image_alt=image_description,
                    image_caption=image_description
                )
                
                html_path = agents["html_generator"].save_html(html_content)
                st.session_state.html_output = {
                    "content": html_content,
                    "path": html_path
                }
                
                add_log(f"HTML blog post created: {html_path}", "success")
            except Exception as e:
                add_log(f"Error generating HTML: {str(e)}", "error")
                st.error(f"Error generating HTML: {str(e)}")
                logger.error(f"Error generating HTML: {str(e)}", exc_info=True)
        
        # Display the final content with image
        st.markdown("<div class='final-content'>", unsafe_allow_html=True)
        
        # Title
        st.markdown(f"<h1>{final_content.get('title', '')}</h1>", unsafe_allow_html=True)
        
        # Image with caption
        image_path = "E:/Work/ai_content_generator" + final_content.get("image_path", "")[1:]
        if image_path and os.path.exists(image_path):
            st.image(image_path, caption=final_content.get("image_description", ""), width=300)  
        else:
            st.warning(f"Image not found at path: {image_path}")
            add_log(f"Image not found at path: {image_path}", "error")
        
        # Content
        st.markdown(final_content.get("content", ""), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Download options
        st.markdown("<h3 class='section-header'>Download Options</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.html_output and "path" in st.session_state.html_output:
                try:
                    with open(st.session_state.html_output["path"], "rb") as file:
                        html_bytes = file.read()
                    
                    st.download_button(
                        label="Download HTML Blog Post",
                        data=html_bytes,
                        file_name=os.path.basename(st.session_state.html_output["path"]),
                        mime="text/html"
                    )
                except Exception as e:
                    st.error(f"Error preparing HTML download: {str(e)}")
                    add_log(f"Error preparing HTML download: {str(e)}", "error")
        
        with col2:
            if image_path and os.path.exists(image_path):
                try:
                    with open(image_path, "rb") as file:
                        image_bytes = file.read()
                    
                    st.download_button(
                        label="Download Featured Image",
                        data=image_bytes,
                        file_name=os.path.basename(image_path),
                        mime="image/png"
                    )
                except Exception as e:
                    st.error(f"Error preparing image download: {str(e)}")
                    add_log(f"Error preparing image download: {str(e)}", "error")
        
        # Start over
        st.markdown("<div class='button-container'>", unsafe_allow_html=True)
        if st.button("Generate Another Blog Post", key="start_over"):
            st.session_state.stage = 'discover'
            st.session_state.topics = None
            st.session_state.selected_topic = None
            st.session_state.content = None
            st.session_state.refined_content = None
            st.session_state.refinement_history = []
            st.session_state.final_content = None
            st.session_state.html_output = None
            # Keep the logs
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
