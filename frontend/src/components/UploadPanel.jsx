import { useRef, useState } from "react";

export default function UploadPanel({
  selectedFile,
  onChooseFile,
  onGenerate,
  status,
  statusMessage,
}) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const isWorking = status === "working";

  function openFilePicker() {
    if (isWorking) return;
    inputRef.current?.click();
  }

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    onChooseFile(file);
  }

  function onDragOver(e) {
    e.preventDefault();
    if (isWorking) return;
    setIsDragging(true);
  }

  function onDragLeave() {
    setIsDragging(false);
  }

  function onDrop(e) {
    e.preventDefault();
    if (isWorking) return;
    setIsDragging(false);

    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    onChooseFile(file);
  }

  return (
    <section className="panel">
      <div className="panelHeader">
        <h2>Upload</h2>
        <p className="muted">Drag & drop a PDF file here or click to browse</p>
      </div>

      <div
        className={`dropzone ${isDragging ? "dropzoneActive" : ""} ${
          isWorking ? "dropzoneDisabled" : ""
        }`}
        onClick={openFilePicker}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        role="button"
        tabIndex={0}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />

        {!selectedFile ? (
          <div>
            <div className="dropTitle">Drop PDF file here</div>
            <div className="dropSub">or click to browse</div>
          </div>
        ) : (
          <div>
            <div className="dropTitle">Selected File:</div>
            <div className="fileName">{selectedFile.name}</div>
            <div className="dropSub">Click to change file</div>
          </div>
        )}
      </div>

      <button
        className="primaryBtn"
        onClick={onGenerate}
        disabled={!selectedFile || isWorking}
      >
        {isWorking ? "Generating..." : "Generate Flashcards"}
      </button>

      {(status === "working" || status === "error" || status === "done") && (
        <div className="statusStrip">
          <div
            className={`bar ${status === "working" ? "barRunning" : ""} ${
              status === "error" ? "barError" : ""
            }`}
          />
          <div className={`statusText ${status === "error" ? "errorText" : ""}`}>
            {statusMessage}
          </div>
        </div>
      )}
    </section>
  );
}

