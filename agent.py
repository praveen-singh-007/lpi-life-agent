import json
import subprocess
import os
import requests

print("=== RUNNING FINAL AGENT ===")

# ---- Path Setup ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LPI_PATH = os.path.join(BASE_DIR, "..", "dist", "src", "index.js")

print("Using LPI path:", LPI_PATH)

if not os.path.exists(LPI_PATH):
    raise FileNotFoundError(f"LPI server not found at {LPI_PATH}")


# ---- LLM (qwen2.5) ----
def ask_llm(prompt):
    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:1.5b",
                "prompt": prompt,
                "stream": False
            }
        )

        data = res.json()

        # ---- DEBUG (optional, helps you see real issue)
        # print("LLM RAW:", data)

        if "response" in data:
            return data["response"]

        elif "error" in data:
            return f"LLM Error: {data['error']}"

        else:
            return f"Unexpected LLM response: {data}"

    except Exception as e:
        return f"LLM Error: {str(e)}"


# ---- Call LPI Tool ----
def call_lpi_tool(tool_name, query):
    try:
        process = subprocess.Popen(
            ["node", LPI_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )

        # INIT
        init_msg = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        process.stdin.write(json.dumps(init_msg) + "\n")

        # Arguments
        if tool_name == "get_case_studies":
            args = {"query": "healthcare digital twin"}
        else:
            args = {"query": query}

        # Tool call
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": args
            },
            "id": 1
        }

        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()

        stdout, stderr = process.communicate(timeout=10)

        # Parse response
        if stdout.strip():
            lines = stdout.strip().split("\n")

            for line in reversed(lines):
                try:
                    parsed = json.loads(line)

                    if "result" in parsed:
                        result = parsed["result"]

                        if isinstance(result, dict) and "content" in result:
                            content = result["content"]

                            if isinstance(content, list) and len(content) > 0:
                                text = content[0].get("text", "")

                                # Extract healthcare section
                                if tool_name == "get_case_studies":
                                    parts = text.split("## ")
                                    for part in parts:
                                        if "health" in part.lower():
                                            return "## " + part[:800]

                                return text

                        return str(result)

                except:
                    continue

        return "No output received"

    except Exception as e:
        return f"Error calling {tool_name}: {str(e)}"


# ---- Tool Selection (simple but valid) ----
def choose_tools(query):
    return "smile_overview", "get_case_studies"


# ---- Agent ----
def run_agent():
    usecase = input("Enter use case: ")
    constraints = input("Enter constraints (e.g. small team, 2 months, low budget): ")

    print("\nCalling tools...\n")

    proc = subprocess.Popen(
        ["node", LPI_PATH],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    # INIT
    init_msg = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    proc.stdin.write(json.dumps(init_msg) + "\n")

    def call_tool(name, args):
        process = subprocess.Popen(
            ["node", LPI_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )

        # INIT
        init_msg = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        process.stdin.write(json.dumps(init_msg) + "\n")

        # TOOL CALL
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": name, "arguments": args},
            "id": 1
        }

        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()

        stdout, stderr = process.communicate(timeout=10)

        # Parse response
        for line in stdout.split("\n"):
            try:
                parsed = json.loads(line)
                if "result" in parsed:
                    content = parsed["result"]["content"]
                    return content[0].get("text", "")
            except:
                continue

        return ""

    # ---- TOOL CALLS ----
    overview = call_tool("smile_overview", {})
    insights = call_tool("get_insights", {"scenario": usecase})
    cases = call_tool("get_case_studies", {"query": usecase})
    knowledge = call_tool("query_knowledge", {"query": usecase})

    print("\nGenerating deployment strategy...\n")

    # ---- DEPLOYMENT STRATEGY PROMPT ----
    prompt = f"""
    You are a digital twin deployment consultant.

    A client wants to implement the following:

    Use Case:
    {usecase}

    Constraints:
    {constraints}

    You have access to:

    SMILE Overview:
    {overview[:800]}

    Insights:
    {insights[:1200]}

    Case Studies:
    {cases[:1200]}

    Knowledge:
    {knowledge[:800]}

    ====================
    TASK
    ====================

    Provide a deployment strategy using ONLY the data above.

    Your response must be:
    - practical
    - constraint-aware
    - grounded in the provided data
    - decision-oriented (not descriptive)

    ====================
    OUTPUT STRUCTURE
    ====================

    1. Recommended Architecture
    - Describe how the system should be built (high-level)
    - MUST be feasible given constraints (team, time, infrastructure)
    - Prefer minimal viable twin (MVT) approach
    - Avoid complex or large-scale systems unless justified by data

    2. SMILE Phases to Prioritize
    - Select ONLY 2–3 phases
    - For each phase:
    - What it does
    - WHY it is the best choice for THIS use case
    - HOW constraints influence this choice
    - Reference relevant insight or case data if available

    3. Key Risks
    - Identify realistic risks specific to THIS scenario
    - Each risk must be justified using insights or case context (if available)

    4. What to Avoid
    - What should NOT be attempted early
    - Must be justified using:
    - constraints OR
    - lessons from case/insight data

    5. First 3 Actions
    - Concrete, small, realistic steps
    - Must be feasible for given constraints (2 devs, 3 months, etc.)
    - No complex setup steps

    6. Decision Reasoning (CRITICAL)
    - Explain how decisions were made using:
    - SMILE concepts
    - case studies
    - insights
    - Clearly connect:
    data → reasoning → decision
    - At least one decision MUST explicitly reference insight or case study content

    ====================
    STRICT RULES
    ====================

    - Use ONLY the provided data
    - Do NOT use general knowledge
    - Do NOT invent:
    - technologies (e.g., IoT, MQTT, frameworks)
    - tools (e.g., Figma, dashboards)
    - metrics or outcomes
    - Do NOT assume system components unless explicitly mentioned in data
    - All recommendations MUST respect constraints
    - Prefer simplest viable solution over ideal/complex system
    - Avoid generic explanations — every section must relate to THIS scenario

    ====================
    QUALITY CHECK (MANDATORY)
    ====================

    Before answering, ensure:

    - No invented technologies or tools are mentioned
    - Architecture is realistic for constraints
    - SMILE phases are justified (not generic definitions)
    - At least one decision references case study or insight data
    - Output is specific, not generic

    If any rule is violated → internally correct before answering.
    """

    final_answer = ask_llm(prompt)

    print("----- DEPLOYMENT STRATEGY -----\n")
    print(final_answer)

# ---- Run ----
if __name__ == "__main__":
    run_agent()
