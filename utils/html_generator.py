# Updated html_generator.py to use Claude for formatting improvements
import os
import re
import logging
from datetime import datetime
from typing import Dict, Any
from utils.bedrock_client import BedrockClient
from config import OUTPUT_DIR, TEMPLATE_DIR

logger = logging.getLogger(__name__)

class HtmlGenerator:
    def __init__(self):
        # Initialize Bedrock client for HTML enhancement
        self.claude_client = BedrockClient()
        
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def _format_content(self, content: str) -> str:
        """
        Format the markdown-like content to HTML.
        This is a simple implementation; for production, consider using a proper markdown parser.
        """
        # Format headings
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        
        # Format paragraphs (simple approach)
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for p in paragraphs:
            if p.strip() and not p.strip().startswith('<h'):
                formatted_paragraphs.append(f'<p>{p.strip()}</p>')
            else:
                formatted_paragraphs.append(p.strip())
        
        return '\n'.join(formatted_paragraphs)
    
    def generate_html(self, title: str, content: str, image_path: str = "", 
                     image_alt: str = "", image_caption: str = "", 
                     author: str = "AI Content Generator") -> str:
        """
        Generate HTML content using a pre-defined template and enhance with Claude Sonnet.
        """
        try:
            # Remove "Title:" prefix if present
            if title.startswith("Title:"):
                title = title[6:].strip()
                
            # Format the content for HTML
            formatted_content = self._format_content(content)
            
            # Use a fixed professional template with placeholders
            html_template = self._get_professional_template()
            
            # # Check and fix image path if needed
            # # If image_path is just a filename, make sure it points to outputs directory
            # if image_path and not image_path.startswith(('http://', 'https://', './')):
            #     image_path = f"./outputs/{image_path}"
            
            # Replace placeholders with actual content
            final_html = html_template.replace("{{TITLE}}", title)
            final_html = final_html.replace("{{IMAGE_PATH}}", image_path)
            final_html = final_html.replace("{{IMAGE_ALT}}", image_alt)
            final_html = final_html.replace("{{IMAGE_CAPTION}}", image_caption)
            final_html = final_html.replace("{{AUTHOR}}", author)
            final_html = final_html.replace("{{DATE}}", datetime.now().strftime('%B %d, %Y'))
            final_html = final_html.replace("{{YEAR}}", str(datetime.now().year))
            final_html = final_html.replace("{{CONTENT}}", formatted_content)
            
            # Use Claude to improve formatting if needed
            if True:  # Set to False to disable Claude enhancement
                system_prompt = "You are an expert HTML/CSS developer who specializes in making blog content look professional."
                user_message = f"""
                I need you to improve the formatting of this HTML blog content.
                
                Main issues to fix:
                1. Ensure the image displays properly (check the img tag)
                2. Ensure paragraphs have proper spacing and formatting
                3. Fix any heading style inconsistencies
                4. Ensure consistent font styling
                5. Make sure responsive design works well
                
                Do NOT change the core content or structure, just fix the HTML and CSS issues.
                Return ONLY valid HTML code with no explanations.
                
                HTML to improve:
                {final_html}
                """
                
                improved_html = self.claude_client.generate_text(
                    system_prompt=system_prompt,
                    user_message=user_message
                )
                
                # Extract just the HTML from Claude's response
                final_html = self._extract_html_code(improved_html)
            
            return final_html
            
        except Exception as e:
            logger.error(f"Error generating HTML: {str(e)}")
            # Fallback to a simple HTML template if the main approach fails
            return self._generate_fallback_html(title, content, image_path, image_alt, image_caption, author)
    
    def _extract_html_code(self, response: str) -> str:
        """
        Extract HTML code from Claude's response, handling various formats.
        """
        # Try to extract code from markdown code blocks
        if "```html" in response:
            html_parts = response.split("```html")
            if len(html_parts) > 1:
                code_part = html_parts[1].split("```")[0].strip()
                return code_part
        elif "```" in response:
            html_parts = response.split("```")
            if len(html_parts) > 1:
                code_part = html_parts[1].strip()
                return code_part
        
        # If no code blocks, check for <!DOCTYPE html> or <html>
        if "<!DOCTYPE html>" in response:
            return response[response.find("<!DOCTYPE html>"):].strip()
        elif "<html" in response:
            return response[response.find("<html"):].strip()
        
        # If all extraction methods fail, return the original response
        return response.strip()
    
    def _get_professional_template(self) -> str:
        """
        Return a professional pre-defined HTML template with clear placeholders.
        """
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <style>
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f9f9f9;
            font-size: 18px;
        }

        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            line-height: 1.3;
            font-weight: 700;
            color: #4A6FE3;
        }

        h1 {
            font-size: 2.5rem;
        }

        h2 {
            font-size: 2rem;
            border-bottom: 2px solid #eee;
            padding-bottom: 0.5rem;
        }

        h3 {
            font-size: 1.75rem;
        }

        p {
            margin-bottom: 1.5rem;
            line-height: 1.8;
        }

        /* Layout */
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            background-color: #fff;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }

        /* Header */
        .site-header {
            text-align: center;
            border-bottom: 1px solid #eee;
            padding-bottom: 2rem;
            margin-bottom: 2rem;
        }

        .site-title {
            font-size: 2.5rem;
            color: #4A6FE3;
            text-decoration: none;
        }

        .site-description {
            color: #777;
            font-size: 1.1rem;
        }

        /* Article */
        .article-header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .article-title {
            font-size: 2.5rem;
            color: #4A6FE3;
            margin-bottom: 0.5rem;
        }

        .article-meta {
            color: #777;
            font-size: 0.9rem;
            margin-bottom: 2rem;
        }

        /* Images */
        .featured-image-container {
            margin: 2rem 0;
            text-align: center;
        }

        .featured-image {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
        }

        .image-caption {
            margin-top: 0.8rem;
            font-size: 0.9rem;
            color: #777;
            font-style: italic;
            text-align: center;
        }

        /* Article content */
        .article-content {
            margin-bottom: 3rem;
        }

        /* Footer */
        .site-footer {
            text-align: center;
            padding-top: 2rem;
            margin-top: 3rem;
            border-top: 1px solid #eee;
            color: #777;
            font-size: 0.9rem;
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .container {
                padding: 1.5rem;
            }
            
            h1, .article-title {
                font-size: 2.2rem;
            }
            
            h2 {
                font-size: 1.7rem;
            }
            
            h3 {
                font-size: 1.4rem;
            }
            
            body {
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="site-header">
            <h1 class="site-title">AI Content Generator</h1>
            <p class="site-description">Exploring the frontiers of artificial intelligence</p>
        </header>

        <article>
            <header class="article-header">
                <h1 class="article-title">{{TITLE}}</h1>
                <div class="article-meta">
                    <span>By {{AUTHOR}} | Published on {{DATE}}</span>
                </div>
            </header>

            <div class="featured-image-container">
                <img class="featured-image" src="{{IMAGE_PATH}}" alt="{{IMAGE_ALT}}">
                <p class="image-caption">{{IMAGE_CAPTION}}</p>
            </div>

            <div class="article-content">
                {{CONTENT}}
            </div>
        </article>

        <footer class="site-footer">
            <p>&copy; {{YEAR}} AI Content Generator. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>
        '''
    
    def _generate_fallback_html(self, title: str, content: str, image_path: str = "", 
                     image_alt: str = "", image_caption: str = "", 
                     author: str = "AI Content Generator") -> str:
        """
        Generate a simple fallback HTML template in case the main approach fails.
        """
        # Remove "Title:" prefix if present
        if title.startswith("Title:"):
            title = title[6:].strip()
            
        # Check and fix image path if needed
        if image_path and not image_path.startswith(('http://', 'https://', './')):
            image_path = f"./outputs/{image_path}"
            
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #4A6FE3; }}
                h2, h3 {{ color: #8142DB; }}
                img {{ max-width: 100%; height: auto; border-radius: 8px; }}
                .caption {{ font-style: italic; color: #666; text-align: center; margin-bottom: 20px; }}
                .meta {{ color: #666; margin-bottom: 20px; }}
                footer {{ margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px; color: #666; }}
            </style>
        </head>
        <body>
            <header>
                <h1>{title}</h1>
                <div class="meta">
                    <p>Published: {datetime.now().strftime('%B %d, %Y')} | Author: {author}</p>
                </div>
            </header>
            
            <main>
                <img src="{image_path}" alt="{image_alt}">
                <div class="caption">{image_caption}</div>
                
                <article>
                    {content}
                </article>
            </main>
            
            <footer>
                <p>&copy; {datetime.now().year} AI Content Generator. All rights reserved.</p>
            </footer>
        </body>
        </html>
        '''
    
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