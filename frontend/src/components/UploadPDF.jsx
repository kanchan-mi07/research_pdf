import { useRef, useState } from "react";
import api, { getErrorMessage } from "../services/api";

function UploadPDF({ onUploaded }) {
  const inputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const handleFile = async (file) => {
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      return setError("Please select a PDF file");
    }
    if (file.size > 20 * 1024 * 1024) {
      return setError("PDF is too large (max 20 MB)");
    }

    setError("");
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Don't set Content-Type manually, the browser adds it with the boundary
      const { data } = await api.post("/documents/upload", formData, {
        timeout: 300000, // indexing can take a while for big PDFs
      });

      onUploaded(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = ""; // allow re-selecting the same file
    }
  };

  return (
    <div className="upload-box">
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf,.pdf"
        hidden
        onChange={(e) => handleFile(e.target.files[0])}
      />

      <button
        className="upload-btn"
        onClick={() => inputRef.current.click()}
        disabled={uploading}
      >
        {uploading ? "Uploading and indexing..." : "+ Upload PDF"}
      </button>

      <p className="upload-hint">
        {uploading
          ? "This can take up to a minute for large files."
          : "PDF files only, up to 20 MB."}
      </p>

      {error && <div className="auth-error">{error}</div>}
    </div>
  );
}

export default UploadPDF;
