import React, { useState, useEffect } from "react";
import Sidebar from "./Sidebar";

const HistoryContainer = () => {
  const [history, setHistory] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [searchCode, setSearchCode] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/resumo_historico/")
      .then(res => res.json())
      .then(data => {
        if (data.resumo) {
          const linhas = data.resumo.split("\n");
          let alunoAtual = null;
          const parsedHistory = [];

          linhas.forEach(linha => {
            const alunoMatch = linha.match(/^(\d+)\s*-\s*(.+)$/);
            if (alunoMatch) {
              alunoAtual = alunoMatch[2].trim();
              return;
            }
            if (linha.includes("Sem histórico")) {
              alunoAtual = null;
              return;
            }
            const questaoMatch = linha.match(
              /Ano: (\d+) \| Dia: (\d+) \| Idioma: (\w+) → (\d+) \/ (\d+)/
            );
            if (questaoMatch && alunoAtual) {
              parsedHistory.push({
                aluno: alunoAtual,
                date: `${questaoMatch[1]} - Dia ${questaoMatch[2]} (${questaoMatch[3]})`,
                acertos: questaoMatch[4],
                total_questoes: questaoMatch[5],
              });
            }
          });

          setHistory(parsedHistory);
        }
      })
      .catch(err => console.error("Erro ao buscar histórico:", err));
  }, []);

  // Filtro por código/nome e data
  const filteredHistory = history.filter(item => {
    const matchesSearch = item.aluno.toLowerCase().includes(searchCode.toLowerCase());
    const matchesDate = selectedDate ? item.date === selectedDate.toLocaleDateString("pt-BR") : true;
    return matchesSearch && matchesDate;
  });

  return (
    <Sidebar
      history={filteredHistory}
      searchCode={searchCode}
      onSearch={setSearchCode}
      selectedDate={selectedDate}
      onDateChange={setSelectedDate}
      onClearSearch={() => setSearchCode("")}
    />
  );
};

export default HistoryContainer;
