import React, { useState } from 'react';
import './App.css';
import UploadForm from './components/UploadForm';
import ReportView from './components/ReportView';
import logo from '../public/logo.png';

function App() {
  const [userCode, setUserCode] = useState('');
  const [reportData, setReportData] = useState(null);

  const handleCorrection = (data, code) => {
    setUserCode(code);
    setReportData(data);
  };

  const handleCloseReport = () => {
    setReportData(null);
    setUserCode('');
  };

  return (
    <div className="app-wrapper">
      {reportData && (
        <ReportView
          reportData={reportData}
          userCode={userCode}
          onClose={handleCloseReport}
        />
      )}

      <main className="main-content">
        <div className="container">
          <img src={logo} alt="OCR ENEM Logo" className="app-logo" />
          <h1>OCR ENEM</h1>
          <p>Envie o gabarito da sua prova ou simulado e tenha a correção instantânea.</p>
          <UploadForm onCorrect={handleCorrection} />
        </div>
      </main>

      <aside className="decorative-panel">
        <h1 className="system-name">Corretor de Gabaritos</h1>
        <h2>Precisão e Agilidade</h2>
        <p>Nossa tecnologia garante a correção rápida e confiável das suas provas e dos seus simulados, permitindo que você foque no que realmente importa: seus estudos.</p>
      </aside>
    </div>
  );
}

export default App;