import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Upload, FileText, File as FileIcon, CheckCircle2, ChevronRight, X, Download } from 'lucide-react';
import './index.css';

function App() {
  const [template, setTemplate] = useState(null);
  const [cv, setCv] = useState(null);
  const [apiKey, setApiKey] = useState('');
  
  const [status, setStatus] = useState('idle'); // idle, uploading, processing, success, error
  const [errorMsg, setErrorMsg] = useState('');
  
  const [startTime, setStartTime] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [filename, setFilename] = useState('');

  const [currentStep, setCurrentStep] = useState(0);
  const steps = [
    "Subiendo archivos al servidor...",
    "Leyendo contenido del currículum (PDF)...",
    "Analizando perfil profesional con Gemini IA...",
    "Extrayendo experiencia y habilidades técnicas...",
    "Calculando autoevaluación y años de experiencia...",
    "Mapeando datos en la plantilla Word...",
    "Generando documento final..."
  ];

  const templateInput = useRef(null);
  const cvInput = useRef(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    let interval;
    if (['uploading', 'processing', 'generating'].includes(status)) {
      interval = setInterval(() => {
        if (startTime) {
          const s = Math.floor((Date.now() - startTime) / 1000);
          setElapsed(s);
          
          // Simulate steps progress over time
          if (s < 2) setCurrentStep(0);
          else if (s < 4) setCurrentStep(1);
          else if (s < 10) setCurrentStep(2);
          else if (s < 15) setCurrentStep(3);
          else if (s < 20) setCurrentStep(4);
          else if (s < 25) setCurrentStep(5);
          else setCurrentStep(6);
        }
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [status, startTime]);

  const handleGenerate = async () => {
    if (!template || !cv) {
      setErrorMsg("Sube la plantilla y el CV.");
      return;
    }
    
    setErrorMsg('');
    setStatus('uploading');
    setStartTime(Date.now());
    setElapsed(0);
    setCurrentStep(0);

    abortControllerRef.current = new AbortController();

    try {
      const formData = new FormData();
      formData.append('template', template);
      formData.append('cv', cv);
      if (apiKey) formData.append('api_key', apiKey);

      const response = await axios.post('/api/generate', formData, {
        responseType: 'blob',
        signal: abortControllerRef.current.signal
      });

      setCurrentStep(6);
      setTimeout(() => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        setDownloadUrl(url);
        
        const contentDisposition = response.headers['content-disposition'];
        let fn = 'SOLICITUD_GENERADA.docx';
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?([^"]+)"?/);
            if (match && match[1]) fn = match[1];
        }
        setFilename(fn);
        setStatus('success');
      }, 1000);

    } catch (error) {
      if (axios.isCancel(error)) {
        console.log('Request canceled');
        return;
      }
      console.error(error);
      let msg = "Error de red o servidor.";
      if (error.response && error.response.data instanceof Blob) {
        const text = await error.response.data.text();
        try {
          const json = JSON.parse(text);
          msg = json.detail || msg;
        } catch(e) { msg = text || msg; }
      } else if (error.response && error.response.data && error.response.data.detail) {
        msg = error.response.data.detail;
      }
      setErrorMsg(msg);
      setStatus('error');
    }
  };

  const handleCancel = () => {
    if (window.confirm("¿Estás seguro de que deseas cancelar el proceso? Se perderá el progreso actual.")) {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      resetAll();
    }
  };

  const resetAll = () => {
    setStatus('idle');
    setTemplate(null);
    setCv(null);
    setElapsed(0);
    setStartTime(null);
    setDownloadUrl(null);
    setErrorMsg('');
    setCurrentStep(0);
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>SIPECOM S.A</h1>
        <p>Generador Automatizado de Solicitudes de Empleo con IA</p>
      </header>

      <main className="glass-panel">
        
        {errorMsg && (
          <div className="error-badge fade-in">
            <X size={18} style={{marginRight: '0.5rem'}}/> {errorMsg}
          </div>
        )}

        {status === 'idle' || status === 'error' ? (
          <div className="setup-view fade-in">
            
            <div className="uploaders">
              <div className={`upload-box ${template ? 'active' : ''}`} onClick={() => templateInput.current?.click()}>
                <input 
                  type="file" 
                  ref={templateInput} 
                  style={{display: 'none'}} 
                  accept=".docx"
                  onChange={(e) => setTemplate(e.target.files[0])}
                />
                
                {template ? (
                  <>
                    <FileText className="icon" size={48} />
                    <h3>{template.name}</h3>
                    <p style={{fontSize: '0.8rem', marginTop: '0.5rem'}}>Plantilla Word Lista</p>
                  </>
                ) : (
                  <>
                    <Upload className="icon" size={48} />
                    <h3>Plantilla Word</h3>
                    <p style={{fontSize: '0.8rem', marginTop: '0.5rem'}}>Archivo SDE_Project_Manager.docx</p>
                  </>
                )}
              </div>

              <div className={`upload-box ${cv ? 'active' : ''}`} onClick={() => cvInput.current?.click()}>
                <input 
                  type="file" 
                  ref={cvInput} 
                  style={{display: 'none'}} 
                  accept=".pdf,.docx,.doc"
                  onChange={(e) => setCv(e.target.files[0])}
                />
                
                {cv ? (
                  <>
                    <FileIcon className="icon" size={48} />
                    <h3>{cv.name}</h3>
                    <p style={{fontSize: '0.8rem', marginTop: '0.5rem'}}>CV del Candidato Listo</p>
                  </>
                ) : (
                  <>
                    <Upload className="icon" size={48} />
                    <h3>Currículum</h3>
                    <p style={{fontSize: '0.8rem', marginTop: '0.5rem'}}>Sube el PDF o Word del postulante</p>
                  </>
                )}
              </div>
            </div>

            <div className="action-buttons">
              <button 
                className="btn-secondary" 
                style={{flex: '1', padding: '1rem'}}
                onClick={resetAll}
              >
                Limpiar
              </button>
              <button 
                className="btn-primary" 
                style={{flex: '2'}}
                onClick={handleGenerate}
                disabled={!template || !cv}
              >
                Generar CV <ChevronRight style={{verticalAlign: 'middle'}}/>
              </button>
            </div>
          </div>
        ) : status === 'success' ? (
          <div className="result-container fade-in">
            <CheckCircle2 className="success-icon" size={80} />
            <h2>¡Solicitud Generada!</h2>
            <p style={{color: 'var(--text-secondary)', marginTop: '1rem'}}>
              El análisis de IA ha completado todas las tablas del documento.
              Tiempo total: <strong>{formatTime(elapsed)}</strong>
            </p>
            
            <div className="action-buttons">
              <button className="btn-secondary" onClick={resetAll}>
                <X size={18} style={{marginRight: '0.5rem', verticalAlign: 'middle'}}/> Nuevo
              </button>
              <a href={downloadUrl} download={filename} style={{textDecoration: 'none'}}>
                <button className="btn-primary" style={{padding: '0.8rem 1.5rem', width: 'auto'}}>
                  <Download size={18} style={{marginRight: '0.5rem', verticalAlign: 'middle'}}/> Descargar {filename}
                </button>
              </a>
            </div>
          </div>
        ) : (
          <div className="status-container fade-in">
            <div className="spinner"></div>
            <div className="timer">{formatTime(elapsed)}</div>
            
            <div className="steps-container">
              {steps.map((step, index) => (
                <div key={index} className={`step-item ${index === currentStep ? 'active' : index < currentStep ? 'completed' : ''}`}>
                  <div className="step-dot"></div>
                  <span>{step}</span>
                </div>
              ))}
            </div>

            <button 
              className="btn-secondary" 
              style={{marginTop: '2rem', width: 'auto', padding: '0.8rem 2rem', borderColor: '#ff4d4d', color: '#ff4d4d'}}
              onClick={handleCancel}
            >
              Cancelar Proceso
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
