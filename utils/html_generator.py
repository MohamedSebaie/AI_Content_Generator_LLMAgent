import os
import re
import logging
from datetime import datetime
from typing import Dict, Any
from utils.bedrock_client import BedrockClient
from config import OUTPUT_DIR

logger = logging.getLogger(__name__)

class HtmlGenerator:
    def __init__(self):
        # Initialize Bedrock client if needed
        try:
            self.claude_client = BedrockClient()
        except Exception as e:
            logger.warning(f"Could not initialize Bedrock client: {str(e)}. Using default templates only.")
            self.claude_client = None
        
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def _format_content(self, content: str) -> str:
        """
        Format the markdown-like content to HTML.
        Enhanced implementation to handle various markdown elements.
        """
        # Format headings
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2 class="section-heading">\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.+)$', r'<h3 class="sub-heading">\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
        
        # Format bold and italic text
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
        
        # Format lists
        # Unordered lists
        unordered_list_pattern = r'(?:^|\n)(?:\* .+\n)+(?:\n|$)'
        for match in re.finditer(unordered_list_pattern, content, re.MULTILINE):
            list_items = re.findall(r'\* (.+)', match.group(0))
            list_html = '<ul>\n' + '\n'.join([f'<li>{item}</li>' for item in list_items]) + '\n</ul>'
            content = content.replace(match.group(0), list_html)
        
        # Ordered lists
        ordered_list_pattern = r'(?:^|\n)(?:\d+\. .+\n)+(?:\n|$)'
        for match in re.finditer(ordered_list_pattern, content, re.MULTILINE):
            list_items = re.findall(r'\d+\. (.+)', match.group(0))
            list_html = '<ol>\n' + '\n'.join([f'<li>{item}</li>' for item in list_items]) + '\n</ol>'
            content = content.replace(match.group(0), list_html)
        
        # Format paragraphs (more robust approach)
        paragraphs = []
        current_paragraph = []
        in_html_block = False
        
        for line in content.split('\n'):
            # Skip if we're inside an HTML block (list, heading, etc.)
            if line.strip().startswith('<') and not line.strip().startswith('<p>'):
                # If we have a paragraph in progress, close it
                if current_paragraph:
                    paragraphs.append('<p>' + ' '.join(current_paragraph) + '</p>')
                    current_paragraph = []
                
                # Add the HTML line directly
                paragraphs.append(line)
                
                # Check if we're entering an HTML block
                if not line.strip().endswith('>'):
                    in_html_block = True
            
            # Check if we're exiting an HTML block
            elif in_html_block and line.strip().endswith('>'):
                paragraphs.append(line)
                in_html_block = False
            
            # If we're in an HTML block, add the line as is
            elif in_html_block:
                paragraphs.append(line)
            
            # Handle regular paragraph text
            elif line.strip():
                current_paragraph.append(line.strip())
            
            # Handle paragraph breaks
            elif current_paragraph:
                paragraphs.append('<p>' + ' '.join(current_paragraph) + '</p>')
                current_paragraph = []
        
        # Add the last paragraph if exists
        if current_paragraph:
            paragraphs.append('<p>' + ' '.join(current_paragraph) + '</p>')
        
        return '\n'.join(paragraphs)
    
    def _create_professional_template(self) -> str:
        """
        Create a professional default HTML template with modern CSS based on the template design from the screenshot.
        """
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        /* Reset and Base Styles */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Roboto', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f8f8;
        }

        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 1rem;
            color: #2c3e50;
        }

        h1 {
            font-size: 2.5rem;
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }

        h2 {
            font-size: 2rem;
            color: #3498db;
            margin-top: 2rem;
            margin-bottom: 1.2rem;
        }

        h3 {
            font-size: 1.5rem;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }

        p {
            margin-bottom: 1.2rem;
            font-size: 1.1rem;
            line-height: 1.7;
        }

        /* Layout */
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background-color: #fff;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }

        /* Header */
        .header {
            background: linear-gradient(to right, #2c3e50, #4a6fa5);
            color: #fff;
            padding: 2rem 0;
            text-align: center;
        }

        .header h1 {
            font-size: 2.2rem;
            color: #fff;
            margin: 0;
            padding: 0 2rem;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }

        /* Article Container */
        .article-container {
            padding: 2rem;
        }

        /* Article Title */
        .article-title {
            font-size: 2.5rem;
            color: #2c3e50;
            margin-bottom: 1rem;
            text-align: left;
            line-height: 1.2;
        }

        /* Article Meta */
        .article-meta {
            font-size: 0.9rem;
            color: #7f8c8d;
            margin-bottom: 2rem;
            border-bottom: 1px solid #eee;
            padding-bottom: 1rem;
        }

        /* Featured Image */
        .featured-image-container {
            margin: 2rem 0;
            text-align: center;
        }

        .featured-image {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }

        .image-caption {
            margin-top: 0.8rem;
            font-size: 0.9rem;
            color: #7f8c8d;
            text-align: center;
            font-style: italic;
        }

        /* Article Content */
        .article-content {
            margin-bottom: 3rem;
        }

        /* Section Headings with underline */
        .section-heading {
            position: relative;
            display: inline-block;
            margin-bottom: 1.5rem;
            color: #3498db;
        }

        .section-heading::after {
            content: "";
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 100%;
            height: 2px;
            background-color: #3498db;
        }

        /* Lists */
        ul, ol {
            margin-bottom: 1.5rem;
            padding-left: 2rem;
        }

        li {
            margin-bottom: 0.5rem;
        }

        /* Footer */
        .footer {
            background-color: #2c3e50;
            color: #fff;
            padding: 2rem;
            text-align: center;
        }

        .footer p {
            margin: 0;
            font-size: 0.9rem;
            opacity: 0.8;
        }

        /* Responsive Styles */
        @media (max-width: 768px) {
            .article-container {
                padding: 1.5rem;
            }

            h1, .article-title {
                font-size: 2rem;
            }

            h2 {
                font-size: 1.6rem;
            }

            h3 {
                font-size: 1.3rem;
            }

            body {
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>AI Content Generator</h1>
            <p>Exploring the frontiers of artificial intelligence</p>
        </header>

        <div class="article-container">
            <h1 class="article-title">{{TITLE}}</h1>
            
            <div class="article-meta">
                <span>By {{AUTHOR}} | Published on {{DATE}}</span>
            </div>

            <div class="featured-image-container">
                <img src="{{IMAGE_PATH}}" alt="{{IMAGE_ALT}}" class="featured-image">
                <p class="image-caption">{{IMAGE_CAPTION}}</p>
            </div>

            <div class="article-content">
                {{CONTENT}}
            </div>
        </div>

        <footer class="footer">
            <p>&copy; {{YEAR}} AI Content Generator. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>
        '''
    
    def generate_html(self, title: str, content: str, image_path: str = "", 
                     image_alt: str = "", image_caption: str = "", 
                     author: str = "AI Content Generator") -> str:
        """
        Generate HTML content using a professional template.
        """
        try:
            # Remove "Title:" prefix if present
            if title.startswith("Title:"):
                title = title[6:].strip()
                
            # Format the content for HTML
            formatted_content = self._format_content(content)
            
            # Get professional template
            template = self._create_professional_template()
            
            # Debug the image path
            logger.info(f"Original image path: {image_path}")
            
            # Fix image path issues
            if image_path:
                # Get just the filename from the path
                image_filename = os.path.basename(image_path)
                
                # Use relative path for the HTML
                corrected_image_path = f"./outputs/{image_filename}"
                logger.info(f"Corrected image path for HTML: {corrected_image_path}")
                
                # Update the image_path
                image_path = corrected_image_path
            
            # If no image alt text is provided, use a default
            if not image_alt:
                image_alt = "AI-generated image related to the article content"
            
            # If no image caption is provided, use a default
            if not image_caption:
                image_caption = "A visual representation of " + title.lower()
            
            # Replace placeholders with content
            html_content = template.replace("{{TITLE}}", title)
            html_content = html_content.replace("{{CONTENT}}", formatted_content)
            html_content = html_content.replace("{{IMAGE_PATH}}", image_path)
            html_content = html_content.replace("{{IMAGE_ALT}}", image_alt)
            html_content = html_content.replace("{{IMAGE_CAPTION}}", image_caption)
            html_content = html_content.replace("{{AUTHOR}}", author)
            html_content = html_content.replace("{{DATE}}", datetime.now().strftime('%B %d, %Y'))
            html_content = html_content.replace("{{YEAR}}", str(datetime.now().year))
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error generating HTML: {str(e)}")
            # Create a simplified fallback template
            fallback = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{title}</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #3498db; }}
                    img {{ max-width: 100%; height: auto; }}
                </style>
            </head>
            <body>
                <h1>{title}</h1>
                <p>Published on {datetime.now().strftime('%B %d, %Y')} by {author}</p>
                {f'<img src="{image_path}" alt="{image_alt}">' if image_path else ''}
                {formatted_content}
            </body>
            </html>
            """
            return fallback
    
    def save_html(self, html_content: str, filename: str = None) -> str:
        """
        Save the HTML content to a file and return the file path.
        """
        if filename is None:
            # Generate a filename based on the current timestamp
            filename = f"ai_blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Ensure .html extension
        if not filename.endswith('.html'):
            filename += '.html'
        
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"HTML file saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving HTML file: {str(e)}")
            return ""
