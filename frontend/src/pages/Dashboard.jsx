import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";


import UploadPDF from "../components/UploadPDF";
import api, { getErrorMessage } from "../services/api";

function Dashboard() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDocuments = async () => {
    try {
      const { data } = await api.get("/documents/");
      setDocuments(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  // After a successful upload, go straight to the chat for that document
  const handleUploaded = (data) => {
    navigate(`/chat/${data.document_id}`);
  };

  const handleDelete = async (id, filename) => {
    if (!window.confirm(`Delete "${filename}" and its chat history?`)) return;

    try {
      await api.delete(`/documents/${id}`);
      setDocuments((docs) => docs.filter((d) => d.id !== id));
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="page">
     

      <main className="dashboard">
        <h1>Your documents</h1>
        <p className="muted">Upload a PDF and ask questions about it.</p>

        <UploadPDF onUploaded={handleUploaded} />

        {error && <div className="auth-error">{error}</div>}

        {loading ? (
          <p className="muted">Loading...</p>
        ) : documents.length === 0 ? (
          <p className="muted">
            No documents yet. Upload your first PDF above.
          </p>
        ) : (
          <ul className="doc-list">
            {documents.map((doc) => (
              <li key={doc.id} className="doc-item">
                <div
                  className="doc-info"
                  onClick={() => navigate(`/chat/${doc.id}`)}
                >
                  <span className="doc-name">{doc.filename}</span>
                  <span className="doc-date">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </span>
                </div>

                <button
                  className="doc-delete"
                  onClick={() => handleDelete(doc.id, doc.filename)}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
