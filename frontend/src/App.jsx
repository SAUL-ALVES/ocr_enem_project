// App.js
import React, { useState, useEffect } from 'react';
import './App.css';
import UploadForm from './components/UploadForm';
import ReportView from './components/ReportView';
import Sidebar from './components/Sidebar';
import logo from '../public/logo.png';

function App() {
  const [correctionResult, setCorrectionResult] = useState(null);
  const [searchCode, setSearchCode] = useState('');
  const [selectedDate, setSelectedDate] = useState(null);
  const [filteredHistory, setFilteredHistory] = useState([]);

  // 🔹 Função para buscar histórico do backend
  const fetchHistory = () => {
    fetch("http://127.0.0.1:8000/resumo_historico/")
      .then(res => {
        if (!res.ok) throw new Error("Erro ao buscar histórico do aluno");
        return res.json();
      })
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

          // 🔹 Aplica filtro por data, se selecionada
          const finalHistory = selectedDate
            ? parsedHistory.filter(
                item => item.date === selectedDate.toLocaleDateString('pt-BR')
              )
            : parsedHistory;

          setFilteredHistory(finalHistory);
        } else {
          setFilteredHistory([]);
        }
      })
      .catch(err => {
        console.error(err);
        setFilteredHistory([]);
      });
  };

  // 🔹 Carrega histórico ao montar o componente
  useEffect(() => {
    fetchHistory();
  }, [selectedDate]); // re-executa se a data mudar

  // 🔹 Atualiza histórico sempre que um gabarito é corrigido
  const handleCorrection = (data) => {
    setCorrectionResult(data);
    fetchHistory();
  };

  const handleCloseReport = () => {
    setCorrectionResult(null);
  };

  const handleClearSearch = () => {
    setSearchCode('');
    setSelectedDate(null);
    fetchHistory(); // recarrega todos os históricos
  };

  return (
    <>
      {correctionResult && (
        <ReportView 
          result={correctionResult} 
          onClose={handleCloseReport} 
        />
      )}

      <div className="app-panel">
        <Sidebar
          history={filteredHistory}
          searchCode={searchCode}
          onSearch={setSearchCode}
          selectedDate={selectedDate}
          onDateChange={setSelectedDate}
          onClearSearch={handleClearSearch}
        />

        <main className="main-content">
          <div className="container">
            <div className="container-header">
              <img src={logo} alt="OCR ENEM Logo" className="app-logo" />
              <h1>OCR ENEM</h1>
              <p>Envie o gabarito da sua prova ou simulado e tenha a correção instantânea.</p>
            </div>
            <UploadForm onCorrect={handleCorrection} />
          </div>
        </main>

        <aside className="decorative-panel">
          <h1 className="system-name">Corretor de Gabaritos</h1>
          <h2>Precisão e Agilidade</h2>
          <p>
            Nossa tecnologia garante a correção rápida e confiável das suas provas e dos
            seus simulados, permitindo que você foque no que realmente importa: seus estudos.
          </p>
        </aside>
      </div>
    </>
  );
}

export default App;
