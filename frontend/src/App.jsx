import { useCallback, useEffect, useState } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import api, { errorText } from "./api";
import { useAuth } from "./AuthContext";
import Navbar from "./components/Navbar";
import { useToast } from "./components/Toast";
import Discover from "./pages/Discover";
import HowItWorks from "./pages/HowItWorks";
import ChatPage from "./pages/ChatPage";
import Landing from "./pages/Landing";
import Requests from "./pages/Requests";
import ResetPassword from "./pages/ResetPassword";
import Sessions from "./pages/Sessions";
import Setup from "./pages/Setup";

function AppShell({ children }) {
  const toast = useToast();
  const { pathname } = useLocation();
  const [requests, setRequests] = useState([]);
  const [unread, setUnread] = useState(0);
  const load = useCallback(() => api.get("/requests").then((r) => setRequests(r.data)).catch(() => {}), []);
  const loadUnread = useCallback(() => api.get("/sessions/unread").then((r) => setUnread(r.data.unread)).catch(() => {}), []);
  useEffect(() => { load(); loadUnread(); const t = setInterval(() => { load(); loadUnread(); }, 6000); return () => clearInterval(t); }, [load, loadUnread, pathname]);   // reload on every page change, plus simple polling
  const respond = async (id, action) => {
    try { await api.post(`/requests/${id}/respond`, { action }); toast(action === "accept" ? "Accepted. You can now chat under Sessions." : "Request rejected."); load(); }
    catch (e) { toast(errorText(e)); }
  };
  const pending = requests.filter((r) => r.direction === "in" && r.status === "pending").length;
  return (
    <>
      <Navbar pending={pending} unread={unread} />
      <main>{typeof children === "function" ? children({ requests, respond }) : children}</main>
    </>
  );
}

function Protected({ children, needsSetup = true }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="empty" style={{ textAlign: "center", marginTop: 80 }}>Loading...</p>;
  if (!user) return <Navigate to="/" replace />;
  if (needsSetup && !user.setup_done) return <Navigate to="/setup" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/setup" element={<Protected needsSetup={false}><Setup /></Protected>} />
      <Route path="/discover" element={<Protected><AppShell><Discover /></AppShell></Protected>} />
      <Route path="/requests" element={<Protected><AppShell>{({ requests, respond }) => <Requests requests={requests} onRespond={respond} />}</AppShell></Protected>} />
      <Route path="/sessions" element={<Protected><AppShell><Sessions /></AppShell></Protected>} />
      <Route path="/chat" element={<Protected><AppShell><ChatPage /></AppShell></Protected>} />
      <Route path="/how-it-works" element={<Protected><AppShell><HowItWorks /></AppShell></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
