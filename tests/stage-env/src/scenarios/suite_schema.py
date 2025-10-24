"""
Scenario suite schema - группировка сценариев с общей топологией.

Позволяет:
- Поднять сеть один раз
- Запустить несколько субсценариев в этой сети
- Переиспользовать общий setup
- Группировать тесты по функциональности
"""

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

from .schema import TestScenario


class ScenarioSuite(BaseModel):
    """
    Suite of scenarios sharing common network topology.
    
    Группа сценариев с общей топологией сети.
    Сеть поднимается один раз, затем все сценарии выполняются последовательно.
    """
    
    name: str = Field(..., description="Suite name / Название группы")
    description: str = Field(..., description="Suite description / Описание группы")
    author: Optional[str] = Field(None, description="Author / Автор")
    tags: List[str] = Field(default_factory=list, description="Tags / Теги")
    version: str = Field("1.0", description="Version / Версия")
    
    # Network topology (shared by all scenarios)
    # Общая топология для всех сценариев в группе
    network_topology: str = Field(
        "default",
        description="Topology name or path to topology JSON"
    )
    
    # Scenarios to run in this suite
    # Список сценариев для выполнения
    scenarios: List[str] = Field(
        ...,
        min_length=1,
        description="List of scenario paths (relative to scenarios root)"
    )
    
    # Common setup for all scenarios (optional)
    # Общий setup для всех сценариев (опционально)
    common_setup: Optional[str] = Field(
        None,
        description="Path to common setup YAML (executed once before all scenarios)"
    )
    
    # Common cleanup (optional)
    # Общий cleanup (опционально)
    common_cleanup: Optional[str] = Field(
        None,
        description="Path to common cleanup YAML (executed once after all scenarios)"
    )
    
    # Suite execution options
    # Опции выполнения группы
    options: "SuiteOptions" = Field(default_factory=lambda: ScenarioSuite.SuiteOptions())
    
    class SuiteOptions(BaseModel):
        """Опции выполнения группы сценариев."""
        
        stop_on_failure: bool = Field(
            False,
            description="Stop suite execution on first scenario failure"
        )
        
        rebuild_network: bool = Field(
            False,
            description="Rebuild network before suite execution"
        )
        
        cleanup_between_scenarios: bool = Field(
            True,
            description="Run cleanup between scenarios (e.g., clear wallets, reset state)"
        )
        
        parallel_execution: bool = Field(
            False,
            description="Run scenarios in parallel (experimental)"
        )
        
        timeout_per_scenario: int = Field(
            600,
            ge=1,
            description="Timeout per scenario in seconds"
        )


class ScenarioGroup(BaseModel):
    """
    Hierarchical grouping of scenario suites.
    
    Иерархическая группировка наборов сценариев.
    Позволяет организовать тесты по функциональным областям.
    """
    
    name: str = Field(..., description="Group name / Название группы")
    description: str = Field(..., description="Description / Описание")
    
    # Suites in this group
    # Наборы в этой группе
    suites: List[str] = Field(
        default_factory=list,
        description="List of suite paths in this group"
    )
    
    # Sub-groups (for hierarchical organization)
    # Подгруппы (для иерархической организации)
    groups: List[str] = Field(
        default_factory=list,
        description="List of sub-group paths"
    )
    
    # Group execution order
    # Порядок выполнения группы
    execution_order: List[str] = Field(
        default_factory=list,
        description="Explicit execution order (suite/group names)"
    )


# Example suite structure:
# 
# scenarios/
# ├── suites/
# │   ├── token_operations/
# │   │   ├── suite.yml              # ScenarioSuite
# │   │   ├── token_creation.yml     # Individual scenario
# │   │   ├── token_emission.yml     # Individual scenario
# │   │   └── token_transfer.yml     # Individual scenario
# │   ├── consensus/
# │   │   ├── suite.yml
# │   │   ├── block_validation.yml
# │   │   └── fork_resolution.yml
# │   └── network/
# │       ├── suite.yml
# │       ├── node_discovery.yml
# │       └── balancer_test.yml
# └── groups/
#     └── smoke_tests.yml            # ScenarioGroup referencing suites

