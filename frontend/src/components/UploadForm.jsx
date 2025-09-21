import React, { useState, useRef } from 'react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";

const UploadForm = ({ onCorrect }) => {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const [selectedDay, setSelectedDay] = useState(null);
  const [selectedYear, setSelectedYear] = useState(new Date());
  const [selectedLanguage, setSelectedLanguage] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleCorrect = async () => {
    if (!selectedDay || !selectedYear || !selectedLanguage) {
      alert("Por favor, selecione o dia, o idioma e o ano da prova.");
      return;
    }
    if (!file) {
      alert("Por favor, selecione um arquivo.");
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("day", selectedDay);
      formData.append("year", selectedYear.getFullYear());
      formData.append("language", selectedLanguage);

      const response = await fetch("http://127.0.0.1:8000/corrigir/", {
        method: "POST",
        body: formData,
      });

      
      const resultData = await response.json();

      if (!response.ok) {
        
        throw new Error(resultData.error || 'Ocorreu um erro desconhecido.');
      }
      
      
      onCorrect(resultData);

      // Limpa o formulário
      setFile(null);
      setSelectedDay(null);
      setSelectedYear(new Date());
      setSelectedLanguage(null);

    } catch (error) {
      console.error("Erro ao corrigir:", error);
      alert(`Erro ao enviar o arquivo: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  
  const handleDragEvents = (e, dragging) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(dragging);
  };

  const handleDrop = (e) => {
    handleDragEvents(e, false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
    }
  };

  return (
    <>
      <div className="form-options">
        <div className="option-group">
          <label>Selecione o dia da prova</label>
          <div className="day-selector">
            <button 
              className={`day-btn ${selectedDay === 1 ? 'active' : ''}`}
              onClick={() => setSelectedDay(1)}
            >
              Dia 1
            </button>
            <button 
              className={`day-btn ${selectedDay === 2 ? 'active' : ''}`}
              onClick={() => setSelectedDay(2)}
            >
              Dia 2
            </button>
          </div>
        </div>

        <div className="option-group">
          <label>Selecione o idioma</label>
          <div className="day-selector">
            <button 
              className={`day-btn ${selectedLanguage === 'ingles' ? 'active' : ''}`}
              onClick={() => setSelectedLanguage('ingles')}
            >
              Inglês
            </button>
            <button 
              className={`day-btn ${selectedLanguage === 'espanhol' ? 'active' : ''}`}
              onClick={() => setSelectedLanguage('espanhol')}
            >
              Espanhol
            </button>
          </div>
        </div>

        <div className="option-group">
          <label>Selecione o ano</label>
          <DatePicker
            selected={selectedYear}
            onChange={(date) => setSelectedYear(date)}
            showYearPicker
            dateFormat="yyyy"
            maxDate={new Date("2023")} 
            minDate={new Date("2009-01-01")}
            className="year-picker-input day-btn"
            yearItemNumber={12}
          />
        </div>
      </div>

      <div className="upload-and-submit">
        <div
          className={`upload-area-compact ${isDragging ? 'drag-over' : ''}`}
          onClick={() => fileInputRef.current.click()}
          onDragEnter={(e) => handleDragEvents(e, true)}
          onDragLeave={(e) => handleDragEvents(e, false)}
          onDragOver={(e) => handleDragEvents(e, true)}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="gabarito-file"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={handleFileChange}
            ref={fileInputRef}
          />
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
          <span id="file-name">
            {file ? file.name : "Arraste ou clique para enviar"}
          </span>
        </div>
        <button id="correct-button" onClick={handleCorrect} disabled={!file || !selectedDay || !selectedYear || !selectedLanguage || isLoading}>
          {isLoading ? 'Corrigindo...' : 'Corrigir'}
        </button>
      </div>
    </>
  );
};

export default UploadForm;
