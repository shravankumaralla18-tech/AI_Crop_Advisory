import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import Alert from "../../components/Alert.jsx";
import useAuth from "../../hooks/useAuth";
import { errorMessage } from "../../utils/helpers";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(form.email, form.password);
      navigate(location.state?.from?.pathname || "/", { replace: true });
    } catch (err) {
      setError(errorMessage(err, "Could not log in."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth login-page">
      <section className="login-story" aria-label="Crop Advisory">
        <Link to="/login" className="login-brand">
          <img src="/assets/logo.png" alt="" />
          <span>Crop Advisory</span>
        </Link>
        <div className="login-story-copy">
          <span className="login-kicker">GROW WITH BETTER INSIGHT</span>
          <h1>Know your fields.<br />Shape your season.</h1>
          <p>Good decisions start with a closer look at what is growing.</p>
        </div>
        <div className="login-image-caption">
          <span className="caption-mark" aria-hidden="true" />
          <span>Rooted in the field. Ready for what comes next.</span>
        </div>
      </section>

      <section className="login-panel">
        <div className="login-panel-top">
          <span>WELCOME BACK</span>
          <p>New here? <Link to="/register">Create an account</Link></p>
        </div>
        <form className="login-form" onSubmit={submit}>
          <div className="login-heading">
            <span className="login-kicker">YOUR FARM, IN FOCUS</span>
            <h2>Sign in</h2>
            <p>Pick up where you left off.</p>
          </div>
          <Alert>{error}</Alert>
          <div className="field login-field">
            <label htmlFor="email">Email address</label>
            <input id="email" type="email" autoComplete="email" placeholder="you@example.com" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
          <div className="field login-field">
            <label htmlFor="password">Password</label>
            <input id="password" type="password" autoComplete="current-password" placeholder="Enter your password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </div>
          <button className="btn login-submit" disabled={busy}>
            {busy ? "Signing in..." : "Sign in"}
            {!busy && <span aria-hidden="true">&rarr;</span>}
          </button>
          <p className="login-security">Your growing season starts here.</p>
        </form>
        <footer className="login-footer">CROP ADVISORY <span>·</span> BUILT FOR THE FIELD</footer>
      </section>
    </main>
  );
}
