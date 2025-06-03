from anthropic import AsyncAnthropic
from dotenv import load_dotenv
import os
import json


# Carregar variáveis do ambiente
load_dotenv()
anthropic_api = os.getenv("ANTHROPIC_API_KEY")



class Agent():

  def __init__(self,
                agent_name: str,
                agent_role: str,
                agent_goal: str,
                temperature = 0.0,
                meetings=[],
                llm_client= AsyncAnthropic(api_key=anthropic_api)
                ):
    
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.agent_goal = agent_goal
        self.temperature = temperature
        self.meetings = meetings
        self.llm_client = llm_client
        


  async def forward(self, response_format: dict, current_task_context: str, relevant_meeting_history: list) -> dict:

    #relevant_meeting_history is a list of Chat objects
    history_lines = []
    for chat_message in relevant_meeting_history:
        history_lines.append(f"{chat_message.agent.agent_name}: {chat_message.content}")

    formatted_history_string = "\n".join(history_lines)
    
    json_structure_lines = []
    num_keys = len(response_format)
    for i, (key, value_description) in enumerate(response_format.items()):
        line = f'  "{key}": "{value_description}"'
        if i < num_keys - 1:  # Add a comma if it's not the last key
            line += ","
        json_structure_lines.append(line)

    formatted_json_structure_string = "\n".join(json_structure_lines)

    prompt = f"""You are {self.agent_name}, an AI assistant.
Your defined role is: "{self.agent_role}"
Your primary goal in this interaction is: "{self.agent_goal}"

--------------------
CONTEXT:
--------------------
The current specific task or question you need to address is:
"{current_task_context}"

The relevant conversation history leading up to your turn is as follows:
[START OF CONVERSATION HISTORY]
{formatted_history_string}
[END OF CONVERSATION HISTORY]

--------------------
YOUR TASK & RESPONSE REQUIREMENTS:
--------------------
Based on your role, goal, the current task, and the conversation history, you must now generate a response.

Your response MUST be a valid JSON object (or a string that can be directly parsed into a JSON object).
This JSON object must strictly adhere to the following structure, containing these keys and only these keys:

[START OF JSON STRUCTURE DEFINITION]
{{
{formatted_json_structure_string}
}}
[END OF JSON STRUCTURE DEFINITION]

For example, if the response format is {{ "analysis": "Your detailed analysis", "recommendation": "Your specific recommendation" }}, your output should look like:
{{
  "analysis": "...",
  "recommendation": "..."
}}

Do not include any introductory phrases, concluding remarks, or any other text outside of the single, valid JSON object in your response. Your entire output must be only the JSON object itself.

Now, generate your response based on all the above instructions."""

    
    request = await self.llm_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=2048,
        temperature=self.temperature,
        system=f"You are {self.agent_name}. Your role: {self.agent_role}. Your goal: {self.agent_goal}", 
        messages=[
                  {
                  "role": "user",
                  "content": prompt 
                  }
                  ]
    )
    
    message = request.content[0].text
    json_message = json.loads(message)

    return json_message


      
class Chat():

  def __init__(self,
                agent: Agent,
                content: str
              ):
     
     self.agent = agent
     self.content = content


class Meeting():
   
   def __init__(self,
                meeting_name: str,
                ):
      
      self.meeting_name = meeting_name
      self.chats = []

