import React, { useState, useEffect } from 'react';
import './App.css';
import UploadForm from './components/UploadForm';
import ReportView from './components/ReportView';
import Sidebar from './components/Sidebar';
import logo from '../public/logo.png';

// DADOS MOCK (SIMULAÇÃO DO BACKEND)
const mockDatabase = {
  "ALUNO-583271": {
    code: "ALUNO-583271",
    history: [
      { date: "10/05/2024", acertos: 120, total_questoes: 180 },
      { date: "24/06/2024", acertos: 135, total_questoes: 180 },
      { date: "05/08/2024", acertos: 152, total_questoes: 180 },
      { date: "15/08/2024", acertos: 168, total_questoes: 180 },
    ]
  },
  "ALUNO-123456": {
    code: "ALUNO-123456",
    history: [
      { date: "10/05/2024", acertos: 95, total_questoes: 180 },
      { date: "15/08/2024", acertos: 110, total_questoes: 180 },
    ]
  }
};

function App() {
  const [reportData, setReportData] = useState(null);
  const [userCode, setUserCode] = useState('');
  
  const [searchCode, setSearchCode] = useState('');
  const [selectedDate, setSelectedDate] = useState(null);
  const [filteredHistory, setFilteredHistory] = useState([]);

  useEffect(() => {
    const codeToSearch = searchCode.trim().toUpperCase();
    
    if (!codeToSearch) {
      setFilteredHistory([]);
      return;
    }

    const studentData = mockDatabase[codeToSearch];
    if (studentData) {
      let history = studentData.history;
      if (selectedDate) {
        const formattedDate = selectedDate.toLocaleDateString('pt-BR');
        history = history.filter(item => item.date === formattedDate);
      }
      setFilteredHistory(history);
    } else {
      setFilteredHistory([]);
    }
  }, [searchCode, selectedDate]);

  const handleCorrection = (data, code) => {
    setUserCode(code);
    setReportData(data);
  };

  const handleCloseReport = () => {
    setReportData(null);
  };

  const handleClearSearch = () => {
    setSearchCode('');
    setSelectedDate(null);
  };

  return (
    <>
      {reportData && (
        <ReportView
          reportData={reportData}
          userCode={userCode}
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
            {/* O UploadForm agora está diretamente aqui para melhor alinhamento */}
            <UploadForm onCorrect={handleCorrection} />
          </div>
        </main>

        <aside className="decorative-panel">
          <h1 className="system-name">Corretor de Gabaritos</h1>
          <h2>Precisão e Agilidade</h2>
          <p>Nossa tecnologia garante a correção rápida e confiável das suas provas e dos seus simulados, permitindo que você foque no que realmente importa: seus estudos.</p>
        </aside>
      </div>
    </>
  );
}

export default App;