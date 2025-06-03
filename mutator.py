from anthropic import AsyncAnthropic
from dotenv import load_dotenv
import os
import json

# Carregar variáveis do ambiente
load_dotenv()
anthropic_api = os.getenv("ANTHROPIC_API_KEY")

def get_scaffold_information(filepath: str):
    
    base_name = os.path.basename(filepath)
    system_name, _ = os.path.splitext(base_name)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            system_code = f.read()
        return system_code, system_name
    except FileNotFoundError:
        print(f"File not found: {filepath}") 
        return None
    

async def mutate(
    system_name: str,
    system_thought_process: str,
    system_code: str,  # This is the string of the scaffold's Python code
    sampled_mutation_operator: str,
    meta_agent_llm_client= AsyncAnthropic(api_key=anthropic_api), # The initialized LLM client
    meta_agent_model_name: str = "claude-3-5-sonnet-20240620" # Default Meta Agent model
):
    
    mutator_system_prompt = """You are an expert AI programmer and system analyst. Your task is to take the provided Python scaffold (its current name, thought process, code) and a specific mutation operator. You must perform the following actions and structure your entire response as a single JSON object:

1.  **Mutate the Code:** Apply the mutation operator to the provided 'SYSTEM CODE' to generate new, valid Python code for the 'async def forward' function.
2.  **Generate New Thought Process:** Create a concise, updated 'SYSTEM THOUGHT PROCESS' that accurately describes the new, mutated system's architecture, logic, and how it addresses its task, reflecting the changes made by the mutation.
3.  **Suggest New System Name:** Propose a new 'SYSTEM NAME' for this mutated scaffold. This could be based on the original name with a suffix (e.g., "-v2", "-mutated") or a more descriptive name if the mutation is significant.
4.  **Echo Operator:** Include the exact 'SAMPLED MUTATION OPERATOR' that was provided as input.

Your entire response MUST be a single, valid JSON object with the following exact keys:
"SYSTEM NAME": "The new suggested name for the mutated scaffold (string)",
"SYSTEM THOUGHT PROCESS": "The new, updated thought process describing the mutated scaffold (string)",
"SYSTEM CODE": "The complete Python code for the mutated 'async def forward' function (string, properly escaped for JSON if necessary)",
"SAMPLED MUTATION OPERATOR": "The exact mutation operator string that was provided as input (string)"

Ensure no other text or explanations are outside of this JSON object."""

    mutator_prompt = f"""Here is the multi-agent system I would like you to mutate:

{system_name}

{system_thought_process}

{system_code}

The mutation I would like to apply is:

{sampled_mutation_operator}

IMPORTANT:

In general, the new system will perform better with more detailed prompts for the agents,
more planning steps, encouringing them to think longer and harder. It may be worth adding a
final agent to the system to help transform the output of the final agent into the desired output
format for the task as the system will be scored very lowley if the output is not in the correct
format, even if the thinking was sound.
Ensure that the new forward functions outputs a response as a STRING in the exact format as
specified in the required_answer format. This could be either a single letter (e.g. A, B, C, D)
or a word or phrase, or a short piece of code.
"""

    response = await meta_agent_llm_client.messages.create(
        model=meta_agent_model_name,
        max_tokens=4096, 
        temperature=0.5, 
        system=mutator_system_prompt, 
        messages=[{"role": "user", "content": mutator_prompt}]
        )
    
    # Assuming response.content[0].text gives the JSON string from the LLM
    llm_response_text = response.content[0].text 

    # Transform the text from the LLM response to a valid dictionary
    parsed_json_output = json.loads(llm_response_text)

    return parsed_json_output
            