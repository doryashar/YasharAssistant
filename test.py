from src.openroute_model import OpenRouteAgent as Agent
import asyncio, logging

async def main():
    logging.basicConfig(level=logging.DEBUG)
    agent = Agent('Ronit')
    
    # question = "Name the planets in the solar system?"
    # question = "translate to hebrew: 'i would like to thank you, mister. you are pretty horrible'"
    # question = "write a happy birthday wish to my father, his name is ohad and he is 64 years old. he has 2 boys and a girl: Dor, Omri and Ofir. he loves swimming and hang with his wife, Sari"
    question1 = 'Hi! are you single?'
    question2 = 'because i dont like single people'
    
    # uid = agent.start_chat('Dor', 0)
    # logging.debug('chat started')
    res = await agent.chat('0', question1)
    logging.info(f"\nQ: {question1}\nResponse: {res}")
    # await agent.chat(uid, question2)
    
if __name__ == '__main__':
    asyncio.run(main())
    