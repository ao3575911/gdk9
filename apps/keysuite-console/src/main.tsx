import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { KeySuiteConsole } from "@/components/keysuite/console";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <KeySuiteConsole />
  </StrictMode>,
);
