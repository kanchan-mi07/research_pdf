import { useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "null");

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login", { replace: true });
  };

  return (
    <nav className="navbar">
      <span className="navbar-brand">ResearchAI</span>

      <div className="navbar-right">
        {user && <span>{user.name}</span>}
        <button onClick={handleLogout}>Log out</button>
      </div>
    </nav>
  );
}

export default Navbar;
