# Templates for different LLM prompts

TREND_DISCOVERY_PROMPT = """
You are a trend analyst specializing in artificial intelligence. 
Your task is to identify the most current and trending topics in AI.

Please provide a list of 5 currently trending AI topics based on recent developments.

You MUST format your response as a JSON object with exactly this structure:
{
  "trendingTopics": [
    {
      "title": "Topic name",
      "description": "Brief 2-3 sentence description of the topic",
      "why_trending": "Explanation of why this topic is currently trending or important",
      "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
    },
    // Additional topics follow the same format
  ]
}

For each topic:
1. title: A concise name for the trending topic
2. description: A brief 2-3 sentence description
3. why_trending: Why this topic is currently relevant or important
4. keywords: 3-5 relevant keywords or hashtags as an array of strings

Ensure topics are varied across different AI domains (e.g., generative AI, computer vision, NLP, robotics, etc.)
Focus on cutting-edge developments that are gaining significant attention in 2025.
"""

CONTENT_GENERATION_PROMPT = """
You are an expert AI content writer. Create a comprehensive blog post about the following AI topic:

TOPIC: {topic}

KEYWORDS: {keywords}

Guidelines:
1. Write an informative, engaging, and well-structured blog post of approximately 1200 words
2. Include a compelling headline/title for the post
3. Structure the content with appropriate headings and subheadings
4. Explain complex AI concepts in an accessible way for a technical audience
5. Include relevant examples, use cases, or applications
6. Discuss current state, challenges, and future directions
7. Cite any specific research or developments that support your points

Your tone should be professional yet engaging, authoritative but conversational.
"""

SELF_CRITIQUE_PROMPT = """
You are a content editor specialized in AI topics. Review the following blog post and provide a detailed critique:

BLOG POST:
{content}

Evaluate the content based on:
1. ACCURACY: Are all technical details and explanations correct?
2. CLARITY: Is the content easy to understand for the target audience?
3. STRUCTURE: Is the post well-organized with logical flow?
4. ENGAGEMENT: Is the writing style engaging and interesting?
5. COMPLETENESS: Does it cover the important aspects of the topic?
6. ORIGINALITY: Does it offer unique insights or perspectives?

For each area, provide:
- A score from 1-10
- Specific examples of strengths
- Specific examples of weaknesses
- Concrete suggestions for improvement

Remember that constructive criticism is most helpful.
"""

CONTENT_REFINEMENT_PROMPT = """
You are an expert AI content writer. Refine the following blog post based on the provided critique:

ORIGINAL BLOG POST:
{original_content}

CRITIQUE:
{critique}

Your task:
1. Address ALL issues identified in the critique
2. Maintain the core topic and structure while improving weak areas
3. Ensure accuracy of all technical information
4. Enhance clarity and engagement
5. Keep the length approximately the same (around 1200 words)

Do not simply acknowledge the critique points - actually implement the suggested improvements.
Provide the complete refined blog post.
"""

IMAGE_PROMPT_GENERATION = """
You are a specialist in creating prompts for AI image generation models.
Based on the following blog post about an AI topic, create a detailed prompt for generating
an accompanying feature image.

BLOG POST TITLE: {title}
BLOG POST CONTENT: {content}

Your task:
1. Create a prompt for an image that visually represents the core concept of the blog post
2. The prompt should be detailed (100-150 words) to guide the image generator
3. Specify visual elements, style, mood, colors, and composition
4. The image should be professional and suitable for a technical blog
5. Do not request text or words in the image
6. Avoid requesting human faces or realistic human figures

Format your response as a JSON object with two fields:
- "image_prompt": The detailed description for the image generation model
- "image_description": A brief caption (10-15 words) for the image that would appear on the blog
"""

# HTML_TEMPLATE_PROMPT = """
# You are designing a simple HTML template for an AI blog post.
# Create clean, responsive HTML with CSS that:

# 1. Has a modern, professional look suitable for a tech blog
# 2. Includes placeholders for:
#    - Title
#    - Featured image
#    - Content sections with headings
#    - Author information
#    - Date
# 3. Has good typography and spacing
# 4. Is responsive for mobile and desktop viewing
# 5. Uses a clean color scheme (preferably with subtle blues/purples for an AI theme)
# 6. Includes minimal styling - nothing too flashy

# Provide the complete HTML template with embedded CSS.
# """
HTML_TEMPLATE_PROMPT = """
You are a professional web designer specializing in technology blogs. Create a polished HTML template for an AI-focused blog with these specific requirements:

1. VISUAL STYLING:
   - Create HIGHLIGHTED TITLES using one or more techniques: gradient backgrounds, accent borders, subtle shadows, or understated animations
   - Implement a sophisticated color scheme with primary/accent colors appropriate for AI content (deep blues, teals, purples)
   - Use professional typography with careful attention to hierarchy and readability

2. REQUIRED PLACEHOLDERS:
   - Placeholder for a HIGHLIGHTED BLOG TITLE in the header
   - Placeholder for a featured image with proper proportions and subtle frame or shadow
   - Placeholder for article title using EYE-CATCHING STYLING (larger font, special color treatment)
   - Placeholders for content sections with DISTINCTIVELY STYLED HEADINGS AND SUBHEADINGS
   - Placeholder for author information (name, bio, optional image)
   - Placeholder for publication date with elegant formatting
   - Footer with appropriate placeholders

3. TECHNICAL SPECIFICATIONS:
   - Fully responsive design using modern CSS (flexbox/grid)
   - Clean, semantic HTML5 markup with proper placeholder elements
   - Optimized typography with perfect spacing and line heights
   - Subtle hover effects for interactive elements
   - Properly structured metadata placeholders

4. PROFESSIONAL TOUCHES:
   - Incorporate subtle design accents that elevate the template (thin dividing lines, section transitions, etc.)
   - Use whitespace strategically to create a premium feel
   - Ensure heading styles have VISUAL EMPHASIS through color, size, weight, or decorative elements
   - Include a cohesive visual theme throughout all components

Provide complete HTML with embedded CSS that produces a professional, modern template with EMPHASIZED HEADINGS and clearly marked placeholders for all required content elements.
"""