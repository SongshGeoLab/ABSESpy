"""
Interactive visualization for Schelling Segregation Model using Solara.

This demonstrates ABSESpy's compatibility with Mesa's visualization tools.
Uses Mesa's latest visualization API (SpaceRenderer).
"""

import solara
from mesa.visualization import (
    Slider,
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle

from examples.schelling.model import Schelling


def get_happy_agents(model):
    """
    Display a text count of how many happy agents there are.
    
    Args:
        model: The Schelling model instance.
        
    Returns:
        Solara Markdown component showing happy agent count.
    """
    return solara.Markdown(
        "# Schelling Segregation Model\n" 
        f"**Happy agents: {model.happy} / {len(model.agents)}**\n"
        f"**Satisfaction: {model.happy / len(model.agents) * 100:.1f}%**" 
        if len(model.agents) > 0 else "**No agents**",
        style={"width": "100%", "height": "200px"},
    )


def agent_portrayal(agent):
    """
    Define how agents are displayed on the grid.
    
    Uses Mesa's AgentPortrayalStyle for consistent visualization.
    
    Args:
        agent: The agent to portray.
        
    Returns:
        AgentPortrayalStyle defining visual representation.
    """
    return AgentPortrayalStyle(
        color="tab:orange" if agent.type == 0 else "tab:blue",
        size=50,
    )


# Default parameters for initial model
# ABSESpy MainModel expects parameters under "model" key
default_params = {
    "model": {
        "height": 20,
        "width": 20,
        "density": 0.8,
        "minority_pc": 0.5,
        "homophily": 0.4,
        "radius": 1,
    }
}

# Interactive parameter controls for the UI
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "density": Slider("Agent density", 0.8, 0.1, 1.0, 0.1),
    "minority_pc": Slider("Fraction minority", 0.5, 0.0, 1.0, 0.05),
    "homophily": Slider("Homophily", 0.4, 0.0, 1.0, 0.125),
    "width": {
        "type": "InputText",
        "value": 20,
        "label": "Width",
    },
    "height": {
        "type": "InputText",
        "value": 20,
        "label": "Height",
    },
    "radius": {
        "type": "InputText",
        "value": 1,
        "label": "Search Radius",
    },
}

# Create initial model instance
model1 = Schelling(parameters=default_params)

# Create space renderer using latest Mesa API
renderer = SpaceRenderer(
    model=model1,
    backend="matplotlib"  # Can also use "altair"
).render(
    agent_portrayal=agent_portrayal
)

# Create plot components
HappyPlot = make_plot_component("happy", page=1)
PctHappyPlot = make_plot_component("pct_happy", page=1)

# Assemble the visualization page
page = SolaraViz(
    model1,
    renderer,
    components=[
        HappyPlot,
        PctHappyPlot,
        get_happy_agents,
    ],
    model_params=model_params,
    name="Schelling Segregation Model",
)
page  # noqa
