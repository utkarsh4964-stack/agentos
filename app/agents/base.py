import time
from groq import Groq
from app.config import GEMINI_API_KEY
from app.memory.memory_store import MemoryStore
from app.resources.resource_manager import ResourceManager
import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

class BaseAgent:
    def __init__(self, name: str, role: str, goal: str = ""):
        self.name = name
        self.role = role
        self.goal = goal
        self.status = "idle"
        self.memory = MemoryStore()
        self.resources = ResourceManager()
        self._last_output = ""
        print(f"[Agent] '{self.name}' online — {self.role}")

    def run(self, task: str) -> str:
        self.status = "working"
        print(f"\n[{self.name}] Starting: {task[:80]}...")
        if not self.resources.check_rate_limit(self.name):
            self.status = "idle"
            return f"[{self.name}] Rate limit hit. Try again in 60 seconds."
        context = self._get_memory_context(task)
        prompt = self._build_prompt(task, context)
        result = self._call_ai_with_retry(prompt)
        mem_key = f"{self.name}_{int(time.time())}"
        self.memory.write(mem_key, result, long_term=True)
        self._last_output = result
        self.status = "done"
        print(f"[{self.name}] Done ✓")
        return result

    def _build_prompt(self, task: str, context: str = "") -> str:
        prompt = f"You are {self.name}. Your role: {self.role}.\n\n"
        if self.goal:
            prompt += f"Your goal: {self.goal}\n\n"
        if context:
            prompt += f"Relevant context:\n{context}\n\n"
        prompt += f"Task: {task}\n\nRespond clearly and completely."
        return prompt

    def _get_memory_context(self, task: str) -> str:
        try:
            results = self.memory.search(task, top_k=2)
            if results:
                return "\n".join(results[:2])
        except Exception:
            pass
        return ""

    def _call_ai_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                if not GROQ_API_KEY:
                    return self._demo_response(prompt)
                client = Groq(api_key=GROQ_API_KEY)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"You are {self.name}. {self.role}"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                )
                self.resources.log_call(self.name, tokens_used=500)
                return response.choices[0].message.content
            except Exception as e:
                print(f"[{self.name}] Attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    self.status = "failed"
                    return f"[{self.name}] Failed after {max_retries} attempts: {str(e)}"

    def _demo_response(self, prompt: str) -> str:
        if "planner" in self.name.lower():
            return "1. Research the topic\n2. Write a draft\n3. Fact-check\n4. Edit and polish"
        elif "research" in self.name.lower():
            return "Key findings:\n- Major facts about the topic\n- Important statistics\n- Recent developments"
        elif "writer" in self.name.lower():
            return "Here is a well-structured report based on the research findings..."
        elif "fact" in self.name.lower():
            return "All claims verified. ✓"
        else:
            return "Content polished and ready."

    def save_to_memory(self, key: str, value: str, long_term: bool = False):
        self.memory.write(key, value, long_term)

    def recall_from_memory(self, query: str) -> list:
        return self.memory.search(query)

    def send_message(self, to_agent: str, content: str, msg_type: str = "TASK"):
        from app.comms.message_bus import MessageBus, MessageType
        bus = MessageBus()
        return bus.send(self.name, to_agent, content, MessageType(msg_type))

    def receive_messages(self):
        from app.comms.message_bus import MessageBus
        bus = MessageBus()
        return bus.receive(self.name)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "status": self.status,
            "last_output_preview": self._last_output[:100] if self._last_output else ""
        }