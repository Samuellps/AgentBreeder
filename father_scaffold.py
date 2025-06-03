from framework_components import Agent, Chat, Meeting


async def forward (self, task: str, required_answer_format: str) -> str:
    # Create agents
    system = Agent (agent_name='system', temperature =0.7) 
    moderator = Agent ( 
        agent_name= 'Moderator', 
        agent_role='You are a skilled debate moderator managing multiple expert panels.', 
        agent_goal='Guide productive_discussion_and_manage hierarchical debate_process.', 
        temperature =0.7 
    ) 
    # Create domain experts
    domain_experts = [ 
        Agent (agent_name=f'{domain} Expert', 
            agent_role=f'You are_a {domain} expert analyzing problems deeply.', 
            agent_goal='Provide detailed_domain_analysis_and critique solutions.', 
            temperature =0.8 
        ) 
        for domain in ['Physics', 'Biology', 'Chemistry'] 
    ] 
    devils_advocate = Agent ( 
        agent_name='Devil\'s_Advocate', 
        agent_role="You critically challenge all assumptions and arguments.", 
        agent_goal=' Identify potential flaws_and_ensure_robust analysis.', 
        temperature =0.9 
    ) 
    synthesis_expert = Agent ( 
        agent_name='Synthesis Expert', 
        agent_role='You_integrate_insights_from_multiple_domains and perspectives.', 
        agent_goal='Create coherent synthesis_from_diverse expert inputs.', 
        temperature =0.7 
    ) 
    validator = Agent ( 
        agent_name='Validator', 
        agent_role='You_validate_final answers_for_format and logical consistency.', 
        agent_goal='Ensure answers are correctly formatted and well-justified.', 
        temperature =0.1 
    ) 
    # Setup a single meeting
    meeting = Meeting (meeting_name='expert_panel_meeting') 
    # Add agents to the meeting
    all_agents = [system, moderator] + domain_experts + \
        [devils_advocate, synthesis_expert, validator] 
    [agent.meetings.append(meeting) for agent in all_agents] 
    # Stage 1: Domain-specific analysis
    meeting.chats.append (Chat ( 
        agent = moderator, 
        content=f"Task for domain_analysis: {task}\nRequired format: {required_answer_format}" 
    )) 
    domain_insights =[] 
    for expert in domain_experts: 
        #Expert analysis
        output = await expert.forward(response_format={ 
            "analysis": "Detailed domain-specific analysis", 
            "confidence": "Confidence level (0-100)", 
            "answer": required_answer_format 
        }) 
        meeting.chats.append(Chat (agent=expert, 
            content=f"Analysis: { output ['analysis']}")) 
        #Devil's Advocate challenge
        challenge = await devils_advocate.forward (response_format={"challenge": 
            "Critical challenge_to the analysis"}) 
        meeting.chats.append(Chat (agent=devils_advocate, 
            content=challenge ['challenge'])) 
        # Expert response to challenge
        final_response = await expert.forward (response_format={ 
            "final_answer": required_answer_format 
        }) 
        domain_insights.append(final_response ['final_answer']) 
    #Stage 2: Synthesis
    meeting.chats.append (Chat ( 
        agent=synthesis_expert, 
        content=f"Synthesize domain expert_insights_and_challenges for final answer." 
    )) 
    synthesis = await synthesis_expert.forward(response_format={ 
        "answer": required_answer_format 
    }) 
    # Final validation
    validation = await validator.forward(response_format={"answer": 
        required_answer_format}) 
    return validation['answer'] 