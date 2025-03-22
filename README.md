# AI Content Generation Agent

This project implements an automated AI agent that generates high-quality content for trending topics in artificial intelligence. The system discovers trending topics, allows human selection, generates well-structured blog posts, refines the content through self-critique, adds appropriate images, and formats everything into an HTML page.

## Features

- **Trending Topic Discovery**: Automatically searches for current AI trends
- **Human-in-the-loop Selection**: Allows users to select topics of interest
- **Content Generation**: Creates structured, informative blog posts
- **Self-Critique and Refinement**: Implements up to 4 iterations of content improvement
- **Image Generation**: Creates appropriate visuals using Stable Diffusion
- **HTML Output**: Formats the final content into a responsive HTML page

## Technologies Used

- **AWS Bedrock** with **Claude Sonnet 3.5** for content generation and refinement
- **Hugging Face Stable Diffusion** for image generation
- **LangGraph** for workflow orchestration
- **Google Serper API** for web search and topic discovery

## Requirements

- Python 3.8+
- AWS account with Bedrock access (Claude Sonnet 3.5)
- AWS credentials (access key and secret key)
- Google Serper API key (for web search)
- GPU recommended for faster image generation (though CPU will work)

## Installation

1. Clone the repository:https://github.com/MohamedSebaie/AI_Content_Generator_LLMAgent.git then cd AI_Content_Generator_LLMAgent
2. Install the required Python packages:pip install -r requirements.txt
3. Create a `.env` file in the project root with your API keys:
```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region_here
SERPER_API_KEY=your_serper_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
```
4. Run the script:python main.py

The workflow will:
1. Discover trending AI topics
2. Prompt you to select a topic
3. Research and generate content for the selected topic
4. Refine the content through multiple iterations
5. Generate an accompanying image
6. Create and save an HTML file with the final blog post

## File Structure

- `main.py`: Entry point for the application
- `config.py`: Configuration settings
- `agents/`: Contains the specialized agents for each task
- `utils/`: Utility functions and helpers
- `workflows/`: LangGraph workflow definitions
- `outputs/`: Directory where generated HTML files and images are saved

## Implementation Details

This system leverages LangGraph for orchestration, allowing each step in the content generation process to be modular and well-defined. The workflow is built on a state machine that tracks progress and data through each stage.

Key components:
- Topic discovery uses web scraping and Claude analysis to find current trends
- Content generation employs prompt engineering to create well-structured posts
- The refinement mechanism implements an AI-based review and improvement cycle
- Image generation creates relevant visuals based on the content using Stable Diffusion
- HTML generation ensures responsive, visually appealing output

## Sample Output

A sample output HTML file is included in the `outputs/` directory as a demonstration of the agent's capabilities.

## License

MIT License
