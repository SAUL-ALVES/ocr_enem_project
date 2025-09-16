import asyncio
import aiohttp

list_answers = []
    
async def fetch_questao(session, ano, index) -> dict:
    url = f"https://api.enem.dev/v1/exams/{ano}/questions/{index}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return {
                "index": data["index"],
                "title": data["title"],
                "correct": data.get("correctAlternative")
            }
        else:
            return {
                "index": index,
                "title": f"Questão {index}",
                "correct": "Anulado"
            }

async def fetch_todas_questoes(ano) -> list:
    prova_url = f"https://api.enem.dev/v1/exams/{ano}"
    async with aiohttp.ClientSession() as session:
        async with session.get(prova_url) as r:
            if r.status != 200:
                print("Erro ao buscar a prova:", r.status)
                return []
            prova = await r.json()

        tasks = [fetch_questao(session, ano, idx) for idx in range(1, 181)]
        questoes = await asyncio.gather(*tasks)

        return [q for q in questoes if q is not None]

async def compare_answers(list_answers: list, year: int, test_day: int):
    questoes = await fetch_todas_questoes(year)
    print(f"\n✅ Total de questões encontradas: {len(questoes)}\n")
    print(f"✅ Total de respostas do usuário: {len(list_answers)}\n")
    
    if test_day == 1:
        start, end = 0, 90  
    elif test_day == 2:
        start, end = 90, 180

    questoes_dia = questoes[start:end]
    min_length = min(len(questoes_dia), len(list_answers))

    corrects = sum(
        1 for i in range(min_length)
        if questoes_dia[i]['correct'] == list_answers[i] 
        or questoes_dia[i]['correct'] == "Anulado"
    )
    print(f"✅ Total de respostas corretas: {corrects}/{min_length} questões\n")
    
    for i in range(min_length):
        status = "✅" if questoes[i]['correct'] == list_answers[i] else "❌"
        print(f"{status} Questão {i+1}: Usuário={list_answers[i]}, Correto={questoes[i]['correct']}")


if __name__ == "__main__": 
    year: int = input("Digite o ano da prova do ENEM (ex: 2009): ")
    asyncio.run(compare_answers(list_answers, year))
