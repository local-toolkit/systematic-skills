import os
import json
import logging
import requests
from multiprocessing import Pool
from typing import List, Dict, Any

# ==========================================
# 1. Configuration & Constants
# ==========================================
API_URL = os.getenv("LMSTUDIO_API_URL", "http://localhost:1234/v1/chat/completions")
NUM_AGENTS = int(os.getenv("NUM_AGENTS", "3"))
NUM_ROUNDS = int(os.getenv("NUM_ROUNDS", "2"))
MODEL_PATH = os.getenv("MODEL_PATH", "default_model")
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | [%(name)s] | %(levelname)s | %(message)s'
)
logger = logging.getLogger("Dist-MultiAgent")

# ==========================================
# 2. Agent Class Definition
# ==========================================
class Agent:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.name = f"Agent_{agent_id}"
        self.history = []
        self.system_prompt = (
            f"You are {self.name}, a participant in a multi-agent debate. "
            "Your goal is to provide deep insights and critique other agents' points fairly. "
            "Be concise but thorough."
        )

    def generate_response(self, round_num: int, context: str) -> str:
        """
        Calls the LMStudio API to generate a response based on the current context.
        """
        if MOCK_MODE:
            return f"[{self.name}] Mock response for round {round_num} discussing: {context[:30]}..."

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Round {round_num} Context:\n{context}\n\nYour response:"}
        ]
        
        payload = {
            "model": MODEL_PATH,
            "messages": messages,
            "temperature": 0.7,
            "stream": False
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=1200)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            return content.strip()
        except Exception as e:
            logger.error(f"{self.name} failed to generate response: {e}")
            return f"Error: Could not reach model for {self.name}."

# ==========================================
# 3. Discussion Helper (Process-safe)
# ==========================================
def agent_task(args):
    """Function to be executed by multiprocessing Pool."""
    agent_id, round_num, context = args
    agent = Agent(agent_id)
    # Note: In a real system, you might want to maintain persistent histories.
    # Here we recreate the agent instance per round for simplicity in multiprocessing.
    return agent.generate_response(round_num, context)

# ==========================================
# 4. Multi-Agent Logic & Orchestration
# ==========================================
class DiscussionManager:
    def __init__(self, topic: str):
        self.topic = topic
        self.rounds_data = [] # List of round outputs

    def run_discussion(self):
        current_context = f"Topic: {self.topic}"
        
        for r in range(1, NUM_ROUNDS + 1):
            logger.info(f"--- Starting Round {r} ---")
            
            # Prepare arguments for multiprocessing
            tasks = [(i, r, current_context) for i in range(NUM_AGENTS)]
            
            with Pool(processes=NUM_AGENTS) as pool:
                round_responses = pool.map(agent_task, tasks)
            
            self.rounds_data.append(round_responses)
            
            # Update context for next round: include everyone's thoughts
            round_summary = "\n".join([f"Agent {i} says: {resp}" for i, resp in enumerate(round_responses)])
            current_context = f"Topic: {self.topic}\n\nPrevious Discussion Summary:\n{round_summary}"
            
            for i, resp in enumerate(round_responses):
                logger.debug(f"Agent {i} response: {resp[:50]}...")

        return self.synthesize_final_answer()

    def synthesize_final_answer(self):
        """
        Aggregates all agent outputs to produce a final 'consensus' answer.
        Using a separate 'Main Controller' call logic.
        """
        logger.info("Synthesizing final answer...")
        if MOCK_MODE:
            return "Consensus: Both Mars colonization and Earth climate change are critical, but Earth must be stabilized to support Mars efforts."

        all_content = json.dumps(self.rounds_data, ensure_ascii=False)
        
        summary_prompt = (
            "Summarize the following discussion between multiple agents and provide a definitive "
            "consolidated final answer based on the consensus or the best arguments presented.\n\n"
            f"Topic: {self.topic}\n\n"
            f"Discussion Data: {all_content}"
        )
        
        payload = {
            "model": MODEL_PATH,
            "messages": [{"role": "system", "content": "You are a master synthesizer."}, {"role": "user", "content": summary_prompt}],
            "temperature": 0.3
        }
        
        try:
            resp = requests.post(API_URL, json=payload, timeout=90)
            return resp.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error during synthesis: {e}"

# ==========================================
# 5. Execution Entry Point
# ==========================================
if __name__ == "__main__":
    test_topic = "小王计划周末开车从东京到大阪，全程约500公里。他预计每小时行驶80公里，每天最多驾驶6小时。沿途计划休息两次，每次休息30分钟。他希望在周六早上8点出发，最晚在周六晚上8点到达。请问：1. 小王能在周六晚上8点前到达吗？  2. 如果不能，请说明他至少需要多长时间才能到达。  3. 请给出完整的计算步骤，包括驾驶时间、休息时间和可能的延迟。"
    
    manager = DiscussionManager(test_topic)
    logger.info(f"Starting Multi-Agent Discussion on: '{test_topic}'")
    
    final_result = manager.run_discussion()
    
    print("\n" + "="*50)
    print("FINAL CONSOLIDATED ANSWER")
    print("="*50)
    print(final_result)
    print("="*50)
