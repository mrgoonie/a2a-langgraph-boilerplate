"""
Example AI Crew Chat: Supervisor-Agent Communication Pattern

This script demonstrates how an AI crew with a supervisor and multiple specialized agents
would work together to solve complex tasks. It simulates the interaction pattern where
a supervisor agent receives input, creates a plan, delegates tasks to specialized agents,
and coordinates their interactions to accomplish a goal.

For demonstration purposes, we're using simulated agent responses instead of real API calls.
"""

import os
import sys
from typing import List, Dict, Any, Callable
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Load environment variables
load_dotenv()

class SimulatedAgent:
    """Simulates an AI agent with specific capabilities for demonstration purposes."""
    
    def __init__(self, name: str, specialty: str, capabilities: List[str]):
        self.name = name
        self.specialty = specialty
        self.capabilities = capabilities
        self.history = []
    
    def process_task(self, task: str) -> str:
        """Simulates processing a task based on the agent's specialty."""
        response = f"[Agent: {self.name}] I've processed the task regarding {task}.\n\n"
        
        if self.name == "researcher":
            response += "Based on my research capabilities, I found the following information:\n\n"
            if "machine learning" in task.lower():
                response += """
Machine learning algorithms are computational methods that allow computers to learn from data without being explicitly programmed.
Key categories include:
1. Supervised Learning: Learning from labeled data (e.g., classification, regression)
2. Unsupervised Learning: Finding patterns in unlabeled data (e.g., clustering, dimensionality reduction)
3. Reinforcement Learning: Learning through interaction with an environment
                """
            elif "decision tree" in task.lower():
                response += """
Decision trees are a popular supervised learning method that works by creating a tree-like model of decisions.
They split the data into subsets based on feature values, creating a flowchart-like structure that helps with classification or regression tasks.
Key advantages include interpretability and handling both numerical and categorical data.
                """
        
        elif self.name == "coder":
            response += "Here's the code implementation you requested:\n\n"
            if "decision tree" in task.lower():
                response += """```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load a sample dataset
iris = load_iris()
X, y = iris.data, iris.target

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Create and train the decision tree classifier
clf = DecisionTreeClassifier(max_depth=3)
clf.fit(X_train, y_train)

# Make predictions
predictions = clf.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, predictions)
print(f"Decision Tree Classifier Accuracy: {accuracy:.2f}")
```
                """
        
        elif self.name == "summarizer":
            response += "Here's a concise summary of the key points:\n\n"
            if "decision tree" in task.lower():
                response += """
Decision trees are intuitive machine learning models that:
- Split data based on feature values to make predictions
- Create a flowchart-like structure that's easy to interpret
- Work for both classification and regression problems
- Handle both numerical and categorical data
- Can be used as building blocks for more advanced ensemble methods like Random Forests
- May be prone to overfitting if not properly pruned or limited in depth
                """
        
        self.history.append({"task": task, "response": response})
        return response


class SupervisorAgent:
    """Simulates a supervisor agent that coordinates multiple specialized agents."""
    
    def __init__(self, name: str, agents: List[SimulatedAgent]):
        self.name = name
        self.agents = {agent.name: agent for agent in agents}
        self.history = []
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Processes a complex query by:
        1. Analyzing the query
        2. Creating a plan with tasks for different agents
        3. Routing tasks to appropriate agents
        4. Synthesizing results
        """
        # Record the query
        self.history.append({"query": query, "steps": []})
        
        # Step 1: Analyze the query and create a plan
        plan = self._create_plan(query)
        self.history[-1]["steps"].append({"action": "create_plan", "plan": plan})
        
        # Step 2: Execute the plan by routing tasks to agents
        agent_responses = {}
        for task in plan["tasks"]:
            agent_name = task["agent"]
            if agent_name in self.agents:
                response = self.agents[agent_name].process_task(task["description"])
                agent_responses[agent_name] = response
                self.history[-1]["steps"].append({
                    "action": "delegate_task",
                    "agent": agent_name, 
                    "task": task["description"],
                    "response": response
                })
        
        # Step 3: Synthesize results
        final_response = self._synthesize_results(query, plan, agent_responses)
        self.history[-1]["steps"].append({
            "action": "synthesize_results",
            "final_response": final_response
        })
        
        return {
            "query": query,
            "plan": plan,
            "agent_responses": agent_responses,
            "final_response": final_response
        }
    
    def _create_plan(self, query: str) -> Dict[str, Any]:
        """Creates a plan based on the query and available agents."""
        plan = {
            "summary": f"Plan for handling query: {query}",
            "tasks": []
        }
        
        # For this example, we'll create a predetermined plan based on the query
        if "machine learning" in query.lower() and "decision tree" in query.lower():
            plan["tasks"] = [
                {
                    "id": 1,
                    "agent": "researcher",
                    "description": "Research the basics of machine learning algorithms"
                },
                {
                    "id": 2,
                    "agent": "coder",
                    "description": "Create a Python example of a decision tree classifier"
                },
                {
                    "id": 3,
                    "agent": "summarizer",
                    "description": "Provide a simple explanation of how decision trees work"
                }
            ]
        else:
            # Default plan for other queries
            plan["tasks"] = [
                {
                    "id": 1,
                    "agent": "researcher",
                    "description": f"Research information about: {query}"
                },
                {
                    "id": 2,
                    "agent": "summarizer",
                    "description": f"Summarize key points about: {query}"
                }
            ]
        
        return plan
    
    def _synthesize_results(self, query: str, plan: Dict[str, Any], agent_responses: Dict[str, str]) -> str:
        """Synthesizes results from multiple agents into a cohesive response."""
        response = f"[Supervisor] I've analyzed your query about '{query}' and coordinated with our specialized agents.\n\n"
        
        response += "Here's what our team found:\n\n"
        
        # Include relevant information from each agent based on the plan
        for task in plan["tasks"]:
            agent_name = task["agent"]
            if agent_name in agent_responses:
                response += f"## From our {agent_name.title()} Agent\n"
                # Extract just the content part, not the agent identifier
                content = agent_responses[agent_name].split("\n\n", 1)[1] if "\n\n" in agent_responses[agent_name] else agent_responses[agent_name]
                response += f"{content}\n\n"
        
        # Add a conclusion
        response += "## Conclusion\n"
        if "machine learning" in query.lower() and "decision tree" in query.lower():
            response += """
I've coordinated our team to provide you with a comprehensive overview of decision trees in machine learning.
Our Researcher provided the foundational concepts, the Coder created a practical implementation example,
and our Summarizer distilled the key points into an easy-to-understand format.

This demonstrates how our AI crew works together: we break down complex tasks, assign them to specialized
agents with different capabilities, and then synthesize the results into a cohesive response that addresses
all aspects of your query.
            """
        else:
            response += f"I've coordinated our team to provide you with information about {query}."
        
        return response


def run_ai_crew_chat_demo():
    """Runs a demonstration of the AI crew chat workflow."""
    # Create specialized agents
    researcher = SimulatedAgent(
        name="researcher",
        specialty="information retrieval",
        capabilities=["web search", "data analysis", "knowledge base access"]
    )
    
    coder = SimulatedAgent(
        name="coder",
        specialty="software development",
        capabilities=["code generation", "code analysis", "debugging"]
    )
    
    summarizer = SimulatedAgent(
        name="summarizer",
        specialty="content summarization",
        capabilities=["text analysis", "key point extraction", "simplification"]
    )
    
    # Create the supervisor
    supervisor = SupervisorAgent(
        name="supervisor",
        agents=[researcher, coder, summarizer]
    )
    
    # Example complex query that requires multiple agents
    query = """
    I need help understanding the basics of machine learning algorithms, 
    then I want to see a simple Python example of a decision tree classifier,
    and finally give me a summary of how decision trees work in simple terms.
    """
    
    print("\n" + "="*80)
    print("AI CREW CHAT DEMONSTRATION")
    print("="*80)
    print(f"\nUser Query: {query.strip()}\n")
    print("="*80 + "\n")
    
    # Process the query through the supervisor
    result = supervisor.process_query(query)
    
    # Display the workflow step by step
    print("STEP 1: SUPERVISOR CREATES A PLAN")
    print("-"*50)
    print(f"Query: {result['query'].strip()}")
    print("\nPlan:")
    for task in result['plan']['tasks']:
        print(f"- Task {task['id']}: Assign to {task['agent']} - {task['description']}")
    print("\n" + "-"*50 + "\n")
    
    # Show each agent's response
    print("STEP 2: AGENTS PROCESS THEIR ASSIGNED TASKS")
    print("-"*50)
    for agent_name, response in result['agent_responses'].items():
        print(f"\n### {agent_name.upper()} RESPONSE:")
        print(response)
        print("-"*30)
    print("\n" + "-"*50 + "\n")
    
    # Show the final synthesized response
    print("STEP 3: SUPERVISOR SYNTHESIZES FINAL RESPONSE")
    print("-"*50)
    print(result['final_response'])
    print("\n" + "-"*50)
    
    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80 + "\n")
    
    return result


if __name__ == "__main__":
    run_ai_crew_chat_demo()
