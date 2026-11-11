import { useEffect, useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import api from "../services/api";

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Reload the list whenever the page changes (for example, after an upload
  // navigates to /chat/<new id>), so new PDFs appear right away.
  useEffect(() => {
    api
      .get("/documents/")
      .then((res) => {
        setDocuments(res.data);
        setError("");
      })
      .catch(() => setError("Could not load documents"))
      .finally(() => setLoading(false));
  }, [location.pathname]);

  const handleDelete = async (e, doc) => {
    e.preventDefault(); // don't follow the link
    e.stopPropagation();

    if (!window.confirm(`Delete "${doc.filename}" and its chat history?`))
      return;

    try {
      await api.delete(`/documents/${doc.id}`);
      setDocuments((docs) => docs.filter((d) => d.id !== doc.id));

      if (location.pathname === `/chat/${doc.id}`) navigate("/dashboard");
    } catch {
      setError("Could not delete the document");
    }
  };

  return (
    <aside className="sidebar">
      <button className="sidebar-new" onClick={() => navigate("/dashboard")}>
        + New PDF
      </button>

      <h3 className="sidebar-title">Your PDFs</h3>

      {error && <p className="sidebar-msg error">{error}</p>}

      {loading ? (
        <p className="sidebar-msg">Loading...</p>
      ) : documents.length === 0 ? (
        <p className="sidebar-msg">No PDFs yet</p>
      ) : (
        <ul className="sidebar-list">
          {documents.map((doc) => (
            <li key={doc.id}>
              <NavLink
                to={`/chat/${doc.id}`}
                className={({ isActive }) =>
                  `sidebar-item ${isActive ? "active" : ""}`
                }
                title={doc.filename}
              >
                <span className="sidebar-name">{doc.filename}</span>
                <button
                  className="sidebar-delete"
                  onClick={(e) => handleDelete(e, doc)}
                  aria-label={`Delete ${doc.filename}`}
                >
                  ×
                </button>
              </NavLink>
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}

export default Sidebar;
