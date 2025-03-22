import os
import logging
import argparse
from dotenv import load_dotenv # type: ignore
from workflows.content_workflow import ContentWorkflow
from config import validate_credentials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_content_generator.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if API keys are available
    missing_credentials = validate_credentials()
    if missing_credentials:
        logger.error(f"Missing required credentials: {', '.join(missing_credentials)}")
        print(f"Error: Missing required credentials: {', '.join(missing_credentials)}")
        print("Please set these environment variables in a .env file or your environment.")
        return
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AI Content Generation Agent")
    parser.add_argument("--auto", action="store_true", help="Run in automatic mode without human interaction")
    args = parser.parse_args()
    
    try:
        # Create and run the workflow
        workflow = ContentWorkflow()
        
        print("\n========== AI CONTENT GENERATION AGENT ==========\n")
        print("This agent will discover trending AI topics, generate content,")
        print("refine it through multiple iterations, and create an HTML blog post.")
        print("\nStarting the workflow...\n")
        
        # Run the workflow
        results = workflow.run()
        
        # Print the results
        print("\n========== WORKFLOW COMPLETED ==========\n")
        print(f"Generated blog post: {results.get('title', '')}")
        print(f"Selected topic: {results.get('selected_topic', {}).get('title', '')}")
        print(f"HTML output saved to: {results.get('html_path', '')}")
        print("\nThank you for using the AI Content Generation Agent!")
        
    except Exception as e:
        logger.error(f"Error in main workflow: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        print("Please check the logs for more details.")

if __name__ == "__main__":
    main()