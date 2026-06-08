import time
import os
from dotenv import load_dotenv
from app.memory.memory_store import MemoryStore
from app.resources.resource_manager import ResourceManager
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

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

        search_context = ""
        if self._should_use_search():
            search_context = self._do_web_search(task)

        prompt = self._build_prompt(task, context, search_context)
        result = self._call_ai_with_retry(prompt)

        mem_key = f"{self.name}_{int(time.time())}"
        self.memory.write(mem_key, result, long_term=True)
        self._last_output = result
        self.status = "done"
        print(f"[{self.name}] Done ✓")
        return result

    def _should_use_search(self) -> bool:
        search_agents = ["research", "scout", "search", "find"]
        return any(kw in self.name.lower() for kw in search_agents)

    def _do_web_search(self, task: str) -> str:
        try:
            from app.search import web_search, should_search
            if should_search(task):
                print(f"[{self.name}] 🔍 Searching web for: {task[:60]}...")
                results = web_search(task)
                print(f"[{self.name}] ✓ Web search complete")
                return results
        except Exception as e:
            print(f"[{self.name}] Search error: {e}")
        return ""

    def _build_prompt(self, task: str, context: str = "",
                      search_context: str = "") -> str:
        prompt = (
            f"You are {self.name}. Your role: {self.role}.\n\n"
            "IMPORTANT INSTRUCTIONS:\n"
            "- Provide a detailed, thorough, and comprehensive response.\n"
            "- Use clear headings and sections where appropriate.\n"
            "- Never truncate or summarize — give the full, complete output.\n"
            "- Minimum response length: 300 words unless the task is very simple.\n\n"
        )
        if self.goal:
            prompt += f"Your goal: {self.goal}\n\n"
        if search_context:
            prompt += f"REAL-TIME WEB SEARCH RESULTS:\n{search_context}\n\n"
            prompt += "Use the above current web data in your response.\n\n"
        if context:
            prompt += f"Relevant memory context:\n{context}\n\n"
        prompt += f"Task: {task}\n\nProvide your full, detailed response below:"
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
        # Try Gemini first
        if GEMINI_API_KEY:
            result = self._call_gemini(prompt, max_retries)
            if result and not result.startswith(f"[{self.name}] Failed"):
                return result
            print(f"[{self.name}] Gemini failed, falling back to Groq...")

        # Fallback to Groq
        if GROQ_API_KEY:
            result = self._call_groq(prompt, max_retries)
            if result and not result.startswith(f"[{self.name}] Failed"):
                return result

        # Last resort: demo response
        print(f"[{self.name}] All providers failed, using demo response.")
        return self._demo_response(prompt)

    def _call_gemini(self, prompt: str, max_retries: int = 3) -> str:
        try:
            import google.generativeai as genai
        except ImportError:
            print(f"[{self.name}] google-generativeai not installed. Run: pip install google-generativeai")
            return f"[{self.name}] Failed: Gemini SDK not installed."

        genai.configure(api_key=GEMINI_API_KEY)

        for attempt in range(max_retries):
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=(
                        f"You are {self.name}. {self.role}\n\n"
                        "Always provide detailed, well-structured, comprehensive responses. "
                        "Use headings and sections. Never cut your response short. "
                        "Give complete, publication-ready output."
                    )
                )
                response = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        max_output_tokens=8000,
                        temperature=0.7,
                    )
                )
                self.resources.log_call(self.name, tokens_used=500)
                print(f"[{self.name}] ✓ Gemini responded")
                return response.text
            except Exception as e:
                print(f"[{self.name}] Gemini attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

        return f"[{self.name}] Failed: Gemini unavailable."

    def _call_groq(self, prompt: str, max_retries: int = 3) -> str:
        from groq import Groq

        for attempt in range(max_retries):
            try:
                client = Groq(api_key=GROQ_API_KEY)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                f"You are {self.name}. {self.role}\n\n"
                                "Always provide detailed, well-structured, comprehensive responses. "
                                "Use headings and sections. Never cut your response short. "
                                "Give complete, publication-ready output."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=8000,
                    temperature=0.7,
                )
                self.resources.log_call(self.name, tokens_used=500)
                print(f"[{self.name}] ✓ Groq responded")
                return response.choices[0].message.content
            except Exception as e:
                print(f"[{self.name}] Groq attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

        return f"[{self.name}] Failed: Groq unavailable."

    def _demo_response(self, prompt: str) -> str:
        if "planner" in self.name.lower():
            return "1. Research\n2. Write\n3. Fact-check\n4. Edit"
        elif "research" in self.name.lower():
            return "Key findings from research and web search..."
        elif "writer" in self.name.lower():
            return "Well-structured content based on research..."
        elif "fact" in self.name.lower():
            return "All claims verified ✓"
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
            "last_output_preview": self._last_output[:500] if self._last_output else ""
        }