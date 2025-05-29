"""
Base agent class for the Finance Assistant.
"""
import os
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    """
    
    def __init__(self, agent_id: str, agent_name: str):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name for the agent
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        logger.info(f"Initialized {agent_name} agent with ID {agent_id}")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        
        Args:
            input_data: Dictionary containing input data
            
        Returns:
            Dictionary containing output data
        """
        pass
    
    def get_agent_info(self) -> Dict[str, str]:
        """
        Get information about the agent.
        
        Returns:
            Dictionary with agent information
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.__class__.__name__
        } 