"""
Base classes for the modular pipeline step system

PROVIDES: Abstract base classes and data structures for pipeline steps
DEPENDS: Standard library (abc, dataclasses, enum, typing, datetime)
CONSUMED BY: All pipeline step implementations (collection, scraping, transformation, etc.)
CONTRACT: Defines interface and common functionality for pipeline execution with dependency checking
TECH CHOICE: ABC with dataclasses and enums for clean, type-safe design
RISK: Low - base classes provide stable foundation
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime


class StepStatus(Enum):
    """Status of a pipeline step execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepResult:
    """Result of a pipeline step execution"""
    step_name: str
    status: StepStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get execution duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def is_success(self) -> bool:
        """Check if step completed successfully"""
        return self.status == StepStatus.COMPLETED
    
    @property
    def is_failure(self) -> bool:
        """Check if step failed"""
        return self.status == StepStatus.FAILED


class BasePipelineStep(ABC):
    """Abstract base class for individual pipeline steps"""
    
    def __init__(self):
        self.step_name = self.get_step_name()
        self.description = self.get_description()
        self.dependencies = self.get_dependencies()
        self.required_config = self.get_required_config()
    
    @abstractmethod
    def get_step_name(self) -> str:
        """Return the name of this pipeline step"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a description of what this step does"""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Return list of step names this step depends on"""
        pass
    
    @abstractmethod
    def get_required_config(self) -> List[str]:
        """Return list of required configuration keys"""
        pass
    
    def can_run(self, config: Dict[str, Any], previous_results: Dict[str, StepResult]) -> bool:
        """Check if this step can run given the current state"""
        # Check if all dependencies are completed
        for dep in self.dependencies:
            if dep not in previous_results:
                return False
            if not previous_results[dep].is_success:
                return False
        
        # Check if required config is present
        for config_key in self.required_config:
            if config_key not in config:
                return False
        
        return True
    
    def can_run_single_step(self, config: Dict[str, Any]) -> bool:
        """Check if this step can run as a single step (ignoring dependencies)"""
        # Check if required config is present
        for config_key in self.required_config:
            if config_key not in config:
                return False
        
        return True
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate that required configuration is present and valid"""
        for config_key in self.required_config:
            if config_key not in config:
                return False
            if config[config_key] is None:
                return False
        return True
    
    def execute(self, config: Dict[str, Any], previous_results: Dict[str, StepResult], **kwargs) -> StepResult:
        """Execute this pipeline step"""
        start_time = datetime.now()
        
        # Create initial result
        result = StepResult(
            step_name=self.step_name,
            status=StepStatus.RUNNING,
            start_time=start_time,
            metadata={"description": self.description}
        )
        
        try:
            # Validate configuration
            if not self.validate_config(config):
                result.status = StepStatus.FAILED
                result.error = f"Missing or invalid configuration: {self.required_config}"
                return result
            
            # Check if step can run
            # For single step execution, skip dependency checks if previous_results is empty
            if previous_results and not self.can_run(config, previous_results):
                result.status = StepStatus.SKIPPED
                result.error = f"Step dependencies not met or configuration invalid"
                return result
            
            # Execute the step
            step_data = self.run_step(config, previous_results, **kwargs)
            
            # Mark as completed
            result.status = StepStatus.COMPLETED
            result.data = step_data
            result.metadata["output_type"] = type(step_data).__name__
            
        except Exception as e:
            result.status = StepStatus.FAILED
            result.error = str(e)
            result.metadata["exception_type"] = type(e).__name__
        
        finally:
            result.end_time = datetime.now()
        
        return result
    
    @abstractmethod
    def run_step(self, config: Dict[str, Any], previous_results: Dict[str, StepResult], **kwargs) -> Any:
        """Execute the actual step logic - override in subclasses"""
        pass
    
    def get_step_info(self) -> Dict[str, Any]:
        """Get information about this step"""
        return {
            "name": self.step_name,
            "description": self.description,
            "dependencies": self.dependencies,
            "required_config": self.required_config
        }
