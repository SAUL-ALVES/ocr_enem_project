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
                "correct": data.get("correctAlternative"),
            }
        else:
            return {"index": index, "title": f"Questão {index}", "correct": "Anulado"}


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


async def compare_answers(list_answers: list, year: int, test_day: int, language: str):
    questoes = await fetch_todas_questoes(year)
    print(f"\n✅ Total de questões encontradas na API: {len(questoes)}\n")
    print(f"✅ Total de respostas do usuário: {len(list_answers)}\n")

    if test_day == 1:
        start, end = 0, 90
    elif test_day == 2:
        start, end = 90, 180
    else:
        start, end = 0, 90

    questoes_dia = questoes[start:end]

    num_questoes_comparar = min(len(questoes_dia), len(list_answers))

    respostas_detalhadas = []
    acertos = 0

    for i in range(num_questoes_comparar):
        resposta_usuario = list_answers[i]
        resposta_correta = questoes_dia[i]["correct"]

        acertou = (resposta_usuario == resposta_correta) or (
            resposta_correta == "Anulado"
        )

        if acertou:
            acertos += 1

        respostas_detalhadas.append(
            {
                "questao_num": start + i + 1,
                "resposta_usuario": resposta_usuario,
                "resposta_correta": resposta_correta,
                "acertou": acertou,
            }
        )

    print(
        f"✅ Total de respostas corretas: {acertos}/{num_questoes_comparar} questões\n"
    )

    # ADIÇÃO CRÍTICA: Retornar os resultados
    return {
        "acertos": acertos,
        "total_questoes": num_questoes_comparar,
        "detalhes": respostas_detalhadas,
    }


if __name__ == "__main__":
    year: int = input("Digite o ano da prova do ENEM (ex: 2009): ")
    asyncio.run(compare_answers(list_answers, year))
