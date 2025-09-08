import asyncio
import aiohttp
import json

list_answers = []
with open('backend/provas.json', 'r', encoding='utf-8') as f:
    provas = json.load(f)
    for questoes in provas["2009"]["azul"].values():
        list_answers.append(questoes)

# Função auxiliar para buscar uma questão específica de forma assíncrona    
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

# Função para buscar todas as questões de um ano específico
async def fetch_todas_questoes(ano) -> list:
    # Primeiro, pega a prova completa para saber quantas questões existem
    prova_url = f"https://api.enem.dev/v1/exams/{ano}"
    async with aiohttp.ClientSession() as session:
        async with session.get(prova_url) as r:
            if r.status != 200:
                print("Erro ao buscar a prova:", r.status)
                return []
            prova = await r.json()
            indices = [q["index"] for q in prova["questions"]]

        # Cria tasks assíncronas para cada questão
        tasks = [fetch_questao(session, ano, idx) for idx in range(1, 181)]
        questoes = await asyncio.gather(*tasks)

        # Remove questões que falharam
        return [q for q in questoes if q is not None]

# Função principal para comparar as respostas do usuário com as respostas corretas
async def compare_answers(list_answers: list, year: int, test_day: int):
    questoes = await fetch_todas_questoes(year)
    print(f"\n✅ Total de questões encontradas: {len(questoes)}\n")
    print(f"✅ Total de respostas do usuário: {len(list_answers)}\n")
    
    if test_day == 1:
        start, end = 0, 90   # Questões 1 a 90
    elif test_day == 2:
        start, end = 90, 180 # Questões 91 a 180

    questoes_dia = questoes[start:end]
    min_length = min(len(questoes_dia), len(list_answers))

    corrects = sum( 1 for i in range(min_length) 
                    if questoes_dia[i]['correct'] == list_answers[i]
                )
    print(f"✅ Total de respostas corretas: {corrects}/{min_length} questões\n")
    
    for i in range(min_length):
        status = "✅" if questoes[i]['correct'] == list_answers[i] else "❌"
        print(f"{status} Questão {i+1}: Usuário={list_answers[i]}, Correto={questoes[i]['correct']}")


if __name__ == "__main__": 
    year: int = input("Digite o ano da prova do ENEM (ex: 2009): ")
    asyncio.run(compare_answers(list_answers, year))
