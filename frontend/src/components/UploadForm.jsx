import React, { useState, useRef } from 'react';

const UploadForm = ({ onCorrect }) => {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleCorrect = async () => {
    if (!file) {
      alert("Por favor, selecione um arquivo.");
      return;
    }
    setIsLoading(true);
    const mockResult = { acertos: 168, total_questoes: 180 };
    const mockUserCode = `ALUNO-${Math.floor(100000 + Math.random() * 900000)}`;
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setIsLoading(false);
    onCorrect(mockResult, mockUserCode);
    setFile(null);
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
    <div>
      <div
        className={`upload-box ${isDragging ? 'drag-over' : ''}`}
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
        <div className="upload-icon-area">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
        </div>
        <div className="upload-text-area">
          <label htmlFor="gabarito-file">
            Clique para selecionar ou arraste o arquivo
          </label>
          <span id="file-name">
            {file ? file.name : "Nenhum arquivo selecionado."}
          </span>
        </div>
      </div>

      <button id="correct-button" onClick={handleCorrect} disabled={!file || isLoading}>
        {isLoading ? 'Corrigindo...' : 'Corrigir Gabarito'}
      </button>
    </div>
  );
};

export default UploadForm;