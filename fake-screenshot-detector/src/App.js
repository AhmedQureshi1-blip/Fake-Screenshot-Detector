import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import {
  FaCheckCircle,
  FaCloudUploadAlt,
  FaDownload,
  FaEye,
  FaEyeSlash,
  FaImage,
  FaInfoCircle,
  FaMoon,
  FaShieldAlt,
  FaSpinner,
  FaSun,
  FaTimesCircle,
} from "react-icons/fa";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000";

function App() {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState("");
  const [confidence, setConfidence] = useState(0);
  const [realProbability, setRealProbability] = useState(0);
  const [fakeProbability, setFakeProbability] = useState(0);
  const [summary, setSummary] = useState("");
  const [metadata, setMetadata] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [showMetadata, setShowMetadata] = useState(false);
  const [reportUrl, setReportUrl] = useState("");

  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

  const handleFileChange = (file) => {
    if (!file) return;

    // ✅ Validate file type
    const allowedTypes = ["image/png", "image/jpeg", "image/jpg"];
    if (!allowedTypes.includes(file.type)) {
      setError("❌ Invalid file type. Only PNG, JPG, and JPEG are allowed.");
      return;
    }

    // ✅ Validate file size (Max: 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError("❌ File is too large. Max size is 5MB.");
      return;
    }

    setSelectedFile(file);
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    setPreview(URL.createObjectURL(file));
    setError("");
    setResult("");
    setConfidence(0);
    setRealProbability(0);
    setFakeProbability(0);
    setSummary("");
    setMetadata(null);
    setReportUrl("");
  };

  const clearSelection = () => {
    setSelectedFile(null);
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    setPreview(null);
    setResult("");
    setConfidence(0);
    setRealProbability(0);
    setFakeProbability(0);
    setSummary("");
    setMetadata(null);
    setError("");
    setReportUrl("");
    setShowMetadata(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("⚠️ Please select a file first!");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult(response.data.result);
      setConfidence(response.data.confidence || response.data.metadata?.confidence || 0);
      setRealProbability(Math.round((response.data.metadata?.real_probability ?? response.data.metadata?.final_probability ?? 0) * 100));
      setFakeProbability(Math.round((response.data.metadata?.fake_probability ?? (1 - (response.data.metadata?.final_probability ?? 0))) * 100));
      setSummary(response.data.summary || response.data.metadata?.analysis_summary || "");
      setMetadata(response.data.metadata);
      setError("");
      setReportUrl(response.data.report_url);
    } catch (error) {
      setError(error.response?.data?.error || "❌ Error processing image.");
      setResult("");
      setRealProbability(0);
      setFakeProbability(0);
      setMetadata(null);
      setReportUrl("");
    } finally {
      setLoading(false);
    }
  };

  const statusClass = result === "Fake" ? "danger" : result === "Real" ? "success" : result === "Needs Review" ? "warning" : "secondary";
  const statusIcon = result === "Fake" ? <FaTimesCircle /> : result === "Real" ? <FaCheckCircle /> : result === "Needs Review" ? <FaInfoCircle /> : <FaShieldAlt />;
  const evidence = metadata?.analysis_reasons || [];

  return (
    <div className={`app-shell ${darkMode ? "theme-dark" : "theme-light"}`}>
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <header className="topbar">
        <div className="brand-wrap">
          <div className="brand-mark">
            <FaShieldAlt />
          </div>
          <div>
            <div className="brand-title">Payment Screenshot Inspector</div>
            <div className="brand-subtitle">Evidence-based fraud checks with OCR, ELA, and metadata</div>
          </div>
        </div>

        <button className={`theme-toggle ${darkMode ? "on" : "off"}`} onClick={() => setDarkMode(!darkMode)}>
          {darkMode ? <FaSun /> : <FaMoon />}
          <span>{darkMode ? "Light" : "Dark"}</span>
        </button>
      </header>

      <main className="container app-main">
        <section className="hero-card">
          <div className="hero-copy">
            <div className="eyebrow">Fraud detection workspace</div>
            <h1>Upload a payment screenshot and get a clearer verdict.</h1>
            <p>
              The backend now weighs OCR text, OCR confidence, ELA variance, edge density, and screenshot metadata.
              Ambiguous uploads are marked for review instead of being forced into the wrong bucket.
            </p>
            <div className="hero-tags">
              <span className="hero-tag">Low-color UI</span>
              <span className="hero-tag">Readable evidence</span>
              <span className="hero-tag">Confidence-first output</span>
            </div>
          </div>

          <div className="hero-metrics">
            <div className="metric-card">
              <span>Detection signals</span>
              <strong>5+</strong>
            </div>
            <div className="metric-card">
              <span>Prediction confidence</span>
              <strong>{confidence || "--"}%</strong>
            </div>
            <div className="metric-card">
              <span>Review mode</span>
              <strong>{result === "Needs Review" ? "On" : "Auto"}</strong>
            </div>
          </div>
        </section>

        <section className="trust-strip" aria-label="Model notes">
          <div className="trust-item">
            <span className="trust-dot" />
            Real and fake probabilities are shown separately.
          </div>
          <div className="trust-item">
            <span className="trust-dot" />
            Ambiguous uploads are marked for review, not forced decisions.
          </div>
          <div className="trust-item">
            <span className="trust-dot" />
            Report download includes full evidence metadata.
          </div>
        </section>

        <section className="dashboard-grid">
          <article className="panel upload-panel">
            <div className="panel-header">
              <div>
                <h2>Upload screenshot</h2>
                <p>Select or drag in a PNG, JPG, JPEG, WEBP, or BMP file.</p>
              </div>
              <div className="panel-icon">
                <FaImage />
              </div>
            </div>

            <div
              className="dropzone"
              onDragOver={(event) => event.preventDefault()}
              onDrop={(event) => {
                event.preventDefault();
                handleFileChange(event.dataTransfer.files[0]);
              }}
              onClick={() => fileInputRef.current?.click()}
              role="button"
              tabIndex={0}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  fileInputRef.current?.click();
                }
              }}
            >
              <FaCloudUploadAlt className="dropzone-icon" />
              <div className="dropzone-title">Drop file here or click to browse</div>
              <div className="dropzone-copy">The app will analyze the image and generate a downloadable PDF report.</div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/jpg,image/webp,image/bmp"
                className="visually-hidden-input"
                onChange={(event) => handleFileChange(event.target.files[0])}
              />
            </div>

            {preview && (
              <div className="preview-shell">
                <img src={preview} alt="Preview" className="preview-image" />
                <div className="preview-footer">
                  <div>
                    <div className="preview-name">{selectedFile?.name}</div>
                    <div className="preview-size">{Math.round((selectedFile?.size || 0) / 1024)} KB</div>
                  </div>
                  <button className="link-button" onClick={clearSelection}>
                    Clear
                  </button>
                </div>
              </div>
            )}

            <div className="action-row">
              <button className="primary-action" onClick={handleUpload} disabled={loading || !selectedFile}>
                {loading ? <FaSpinner className="spinner" /> : <FaCloudUploadAlt />}
                <span>{loading ? "Analyzing..." : "Analyze screenshot"}</span>
              </button>

              {reportUrl && (
                <a href={reportUrl} className="secondary-action" download="report.pdf">
                  <FaDownload />
                  <span>Download report</span>
                </a>
              )}
            </div>

            {error && <div className="status-note error"><FaTimesCircle /> {error}</div>}
          </article>

          <article className="panel result-panel">
            <div className="panel-header">
              <div>
                <h2>Analysis result</h2>
                <p>Signals and summary from the backend classifier.</p>
              </div>
              <div className={`result-badge ${statusClass}`}>
                {statusIcon}
                <span>{result || "Waiting"}</span>
              </div>
            </div>

            <div className={`verdict-card ${statusClass}`}>
              <div className="verdict-top">
                <div className="verdict-label">Verdict</div>
                <div className="verdict-confidence">{confidence ? `${confidence}% confidence` : "No score yet"}</div>
              </div>
              <div className="verdict-value">{result || "Upload a screenshot to begin"}</div>
              <div className="verdict-summary">{summary || "The classifier will summarize the strongest evidence after analysis."}</div>

              {result && (
                <div className="probability-grid">
                  <div className="probability-card">
                    <span>Real probability</span>
                    <strong>{realProbability || 0}%</strong>
                  </div>
                  <div className="probability-card">
                    <span>Fake probability</span>
                    <strong>{fakeProbability || 0}%</strong>
                  </div>
                </div>
              )}

              {result && (
                <div className="probability-bar-shell" aria-label="Prediction probabilities">
                  <div className="probability-bar-labels">
                    <span>Real</span>
                    <span>Fake</span>
                  </div>
                  <div className="probability-bar">
                    <div className="probability-bar-real" style={{ width: `${realProbability || 0}%` }} />
                    <div className="probability-bar-fake" style={{ width: `${fakeProbability || 0}%` }} />
                  </div>
                  <div className="probability-bar-values">
                    <span>{realProbability || 0}%</span>
                    <span>{fakeProbability || 0}%</span>
                  </div>
                </div>
              )}
            </div>

            {loading && (
              <div className="loading-bar">
                <div className="loading-bar-fill" />
              </div>
            )}

            {evidence.length > 0 && (
              <div className="evidence-list">
                <div className="evidence-title">Why it was flagged this way</div>
                <div className="evidence-chips">
                  {evidence.map((item, index) => (
                    <span className="evidence-chip" key={`${item}-${index}`}>
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {metadata && (
              <div className="metadata-shell">
                <button className="metadata-toggle" onClick={() => setShowMetadata(!showMetadata)}>
                  {showMetadata ? <FaEyeSlash /> : <FaEye />}
                  <span>{showMetadata ? "Hide technical details" : "Show technical details"}</span>
                </button>

                {showMetadata && (
                  <pre className="metadata-block">{JSON.stringify(metadata, null, 2)}</pre>
                )}
              </div>
            )}
          </article>
        </section>
      </main>
    </div>
  );
}

export default App;









