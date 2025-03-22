import logging
from typing import Dict, Any, List, Literal, TypedDict
from langgraph.graph import StateGraph # type: ignore
from agents.topic_discovery import TopicDiscoveryAgent
from agents.content_generator import ContentGeneratorAgent
from agents.critique_refiner import CritiqueRefinerAgent
from agents.image_generator import ImageGeneratorAgent
from utils.html_generator import HtmlGenerator

logger = logging.getLogger(__name__)

# Define state type
class WorkflowState(TypedDict):
    topics: List[Dict[str, Any]]
    selected_topic: Dict[str, Any]
    research_data: Dict[str, Any]
    content: Dict[str, Any]
    refined_content: Dict[str, Any]
    final_content: Dict[str, Any]
    html_output: str
    html_path: str

class ContentWorkflow:
    def __init__(self):
        self.topic_agent = TopicDiscoveryAgent()
        self.content_agent = ContentGeneratorAgent()
        self.critique_agent = CritiqueRefinerAgent()
        self.image_agent = ImageGeneratorAgent()
        self.html_generator = HtmlGenerator()
        
        # Initialize the LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the workflow graph for content generation.
        """
        # Create a new graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("discover_topics", self._discover_topics)
        workflow.add_node("human_topic_selection", self._human_topic_selection)
        workflow.add_node("research_topic", self._research_topic)
        workflow.add_node("generate_content", self._generate_content)
        workflow.add_node("refine_content", self._refine_content)
        workflow.add_node("generate_image", self._generate_image)
        workflow.add_node("create_html", self._create_html)
        
        # Add edges
        workflow.add_edge("discover_topics", "human_topic_selection")
        workflow.add_edge("human_topic_selection", "research_topic")
        workflow.add_edge("research_topic", "generate_content")
        workflow.add_edge("generate_content", "refine_content")
        workflow.add_edge("refine_content", "generate_image")
        workflow.add_edge("generate_image", "create_html")
        
        # Set the entry point
        workflow.set_entry_point("discover_topics")
        
        # Compile the workflow
        return workflow.compile()
    
    def _discover_topics(self, state: WorkflowState) -> WorkflowState:
        """
        Discover trending AI topics.
        """
        logger.info("Discovering trending topics...")
        topics = self.topic_agent.discover_trending_topics()
        return {"topics": topics}
    
    def _human_topic_selection(self, state: WorkflowState) -> WorkflowState:
        """
        Facilitate human selection of a topic.
        """
        logger.info("Waiting for human to select a topic...")
        selected_topic = self.topic_agent.human_topic_selection(state.get("topics", []))
        return {**state, "selected_topic": selected_topic}
    
    def _research_topic(self, state: WorkflowState) -> WorkflowState:
        """
        Research the selected topic.
        """
        logger.info(f"Researching topic: {state.get('selected_topic', {}).get('title', '')}")
        research_data = self.topic_agent.get_detailed_research(state.get("selected_topic", {}))
        return {**state, "research_data": research_data}
    
    def _generate_content(self, state: WorkflowState) -> WorkflowState:
        """
        Generate initial content.
        """
        logger.info("Generating content...")
        content = self.content_agent.generate_content(state.get("research_data", {}))
        return {**state, "content": content}
    
    def _refine_content(self, state: WorkflowState) -> WorkflowState:
        """
        Refine content through iterations.
        """
        logger.info("Refining content...")
        refined_content = self.critique_agent.iterative_refinement(state.get("content", {}))
        return {**state, "refined_content": refined_content}
    
    def _generate_image(self, state: WorkflowState) -> WorkflowState:
        """
        Generate an image for the content.
        """
        logger.info("Generating image...")
        final_content = self.image_agent.process_content_for_image(state.get("refined_content", {}))
        return {**state, "final_content": final_content}
    def _create_html(self, state: WorkflowState) -> WorkflowState:
        """
        Create the HTML output.
        """
        logger.info("Creating HTML...")
        final_data = state.get("final_content", {})
        title = final_data.get("title", "AI Technology")
        content = final_data.get("content", "")
        
        # Get the complete image path information
        image_path = final_data.get("image_path", "")
        image_filename = final_data.get("image_filename", "")
        full_image_path = final_data.get("full_path", "")
        image_description = final_data.get("image_description", "")
        
        html_content = self.html_generator.generate_html(
            title=title,
            content=content,
            image_path=image_path.split("/")[-1],
            image_alt=image_description,
            image_caption=image_description
        )
        
        html_path = self.html_generator.save_html(html_content)
        
        return {**state, "html_output": html_content, "html_path": html_path}
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete workflow.
        """
        logger.info("Starting AI content generation workflow...")
        final_state = self.workflow.invoke({})
        logger.info("Workflow completed!")
        
        # Return the results
        return {
            "title": final_state.get("final_content", {}).get("title", ""),
            "content": final_state.get("final_content", {}).get("content", ""),
            "image_path": final_state.get("final_content", {}).get("image_path", ""),
            "html_path": final_state.get("html_path", ""),
            "selected_topic": final_state.get("selected_topic", {})
        }