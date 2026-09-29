from src.agents.sentinel_agent import analyze_with_sentinel
from src.agents.enforcer_agent import enforce_legal
def run_dual_agents(user_input,groq_client=None):
    agent1=analyze_with_sentinel(user_input,groq_client)
    agent2=enforce_legal(agent1,groq_client,retry=False)
    if agent2['score']<0.35 and agent1['detected']:
        retry=enforce_legal(agent1,groq_client,retry=True)
        if retry['score']>agent2['score']:
            agent2=retry
    return {"agent1_output":agent1,"agent2_output":agent2,"final_answer":agent2['text']}
