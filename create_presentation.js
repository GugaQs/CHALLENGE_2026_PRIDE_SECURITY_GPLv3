/*
 * Copyright (C) 2026 Equipe ASPM IA FIAP - Challenge 2026
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See LICENSE.md
 * for the full GNU General Public License.
 */

const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "ASPM IA FIAP - Turma 1TDCPV";
pres.title = "ASPM IA FIAP - Challenge 2026 Pride Security";

// ============================================================
// COLOR PALETTE
// ============================================================
const C = {
  dark:      "0A0E1A",
  darkMid:   "111827",
  slate:     "1E293B",
  slateLight:"2D3B55",
  cyan:      "00C8FF",
  cyanDim:   "0EA5E9",
  purple:    "7C3AED",
  purpleLight:"A78BFA",
  amdRed:    "ED1C24",
  nvidiaGreen:"76B900",
  white:     "F8FAFC",
  muted:     "94A3B8",
  mutedLight:"CBD5E1",
  gold:      "F59E0B",
  green:     "10B981",
  orange:    "F97316",
  yellow:    "FBBF24",
};

const makeShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.3 });

// ============================================================
// SLIDE 1 — CAPA
// ============================================================
{
  let s = pres.addSlide();
  s.background = { color: C.dark };

  // Top accent bar
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.08, fill: { color: C.cyan }, line: { color: C.cyan } });

  // Large background circle (decorative)
  s.addShape(pres.shapes.OVAL, { x: 5.5, y: -1, w: 6, h: 6, fill: { color: C.slateLight, transparency: 80 }, line: { color: C.cyan, transparency: 85, width: 1 } });

  // FIAP Badge
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.35, w: 1.1, h: 0.38, fill: { color: C.purple }, line: { color: C.purple }, rectRadius: 0.05 });
  s.addText("FIAP", { x: 0.5, y: 0.35, w: 1.1, h: 0.38, fontSize: 13, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });

  // Challenge badge
  s.addShape(pres.shapes.RECTANGLE, { x: 1.72, y: 0.35, w: 2.0, h: 0.38, fill: { color: C.slate }, line: { color: C.slateLight }, rectRadius: 0.05 });
  s.addText("CHALLENGE 2026", { x: 1.72, y: 0.35, w: 2.0, h: 0.38, fontSize: 11, bold: false, color: C.muted, align: "center", valign: "middle", margin: 0 });

  // Main Title
  s.addText("ASPM IA FIAP", {
    x: 0.5, y: 1.15, w: 8.5, h: 1.2,
    fontSize: 56, bold: true, color: C.white, align: "left",
    fontFace: "Calibri", margin: 0,
  });

  // Subtitle line
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.4, w: 0.06, h: 0.72, fill: { color: C.cyan }, line: { color: C.cyan } });
  s.addText("Application Security Posture Management\ncom IA Local via GPU AMD & NVIDIA", {
    x: 0.72, y: 2.4, w: 8.0, h: 0.72,
    fontSize: 17, bold: false, color: C.mutedLight, align: "left",
    fontFace: "Calibri", margin: 0,
  });

  // Pride Security + FIAP
  s.addText("Pride Security × FIAP  |  Turma 1TDCPV  |  2026", {
    x: 0.5, y: 3.4, w: 7, h: 0.35,
    fontSize: 12, color: C.muted, align: "left", margin: 0,
  });

  // GPU badges bottom-right
  // AMD
  s.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 4.7, w: 1.5, h: 0.55, fill: { color: C.amdRed }, line: { color: C.amdRed }, shadow: makeShadow() });
  s.addText("AMD Radeon", { x: 6.5, y: 4.7, w: 1.5, h: 0.55, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
  // NVIDIA
  s.addShape(pres.shapes.RECTANGLE, { x: 8.2, y: 4.7, w: 1.5, h: 0.55, fill: { color: C.nvidiaGreen }, line: { color: C.nvidiaGreen }, shadow: makeShadow() });
  s.addText("NVIDIA RTX", { x: 8.2, y: 4.7, w: 1.5, h: 0.55, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });

  // Bottom bar
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.45, w: 10, h: 0.175, fill: { color: C.slate }, line: { color: C.slate } });
  s.addText("github.com/carmipa/CHALLENGE_2026_PRIDE_SECURITY", {
    x: 0.5, y: 5.45, w: 9, h: 0.175,
    fontSize: 9, color: C.muted, align: "left", valign: "middle", margin: 0,
  });
}

// ============================================================
// SLIDE 2 — O PROJETO
// ============================================================
{
  let s = pres.addSlide();
  s.background = { color: C.darkMid };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });

  s.addText("O Projeto", {
    x: 0.5, y: 0.18, w: 9, h: 0.55,
    fontSize: 28, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.72, w: 9, h: 0.02, fill: { color: C.slateLight }, line: { color: C.slateLight } });

  // Left column — description
  const items = [
    { title: "O que é?", body: "CLI em Python para Application Security\nPosture Management (ASPM), desenvolvida no\nChallenge FIAP × Pride Security 2026." },
    { title: "Problema que resolve", body: "Centraliza análise de vulnerabilidades em\ncódigo-fonte com suporte a IA local, sem\nexposição de dados para nuvem." },
    { title: "Público-alvo", body: "Equipes técnicas, estudantes de segurança e\nprofissionais que precisam de ASPM leve,\neducativo e extensível." },
  ];

  items.forEach((item, i) => {
    const y = 0.9 + i * 1.45;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y, w: 0.05, h: 1.1, fill: { color: C.cyan }, line: { color: C.cyan } });
    s.addText(item.title, { x: 0.6, y: y + 0.05, w: 4.0, h: 0.35, fontSize: 14, bold: true, color: C.cyan, margin: 0 });
    s.addText(item.body, { x: 0.6, y: y + 0.38, w: 4.1, h: 0.72, fontSize: 12, color: C.mutedLight, margin: 0 });
  });

  // Right column — feature cards
  const features = [
    { icon: "🔍", label: "Scan por Assinaturas", desc: "14 tipos de vulnerabilidade detectados" },
    { icon: "🤖", label: "IA Local (LLM)", desc: "Análise cognitiva via LM Studio + GPU" },
    { icon: "📊", label: "Relatórios Ricos", desc: "JSON + Markdown + TXT por GPU" },
    { icon: "🔒", label: "Privacidade Total", desc: "Dados 100% locais, sem nuvem" },
  ];

  features.forEach((f, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 5.3 + col * 2.3;
    const y = 0.9 + row * 2.1;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 2.1, h: 1.75, fill: { color: C.slate }, line: { color: C.slateLight }, shadow: makeShadow() });
    s.addText(f.icon, { x, y: y + 0.2, w: 2.1, h: 0.5, fontSize: 24, align: "center", margin: 0 });
    s.addText(f.label, { x, y: y + 0.7, w: 2.1, h: 0.4, fontSize: 12, bold: true, color: C.white, align: "center", margin: 0 });
    s.addText(f.desc, { x, y: y + 1.1, w: 2.1, h: 0.5, fontSize: 10, color: C.muted, align: "center", margin: 0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.45, w: 10, h: 0.175, fill: { color: C.slate }, line: { color: C.slate } });
  s.addText("ASPM IA FIAP — Challenge 2026 Pride Security", { x: 0.5, y: 5.45, w: 9, h: 0.175, fontSize: 9, color: C.muted, align: "left", valign: "middle", margin: 0 });
}

// ============================================================
// SLIDE 3 — ARQUITETURA TÉCNICA
// ============================================================
{
  let s = pres.addSlide();
  s.background = { color: C.dark };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.purple }, line: { color: C.purple } });

  s.addText("Arquitetura Técnica", {
    x: 0.5, y: 0.18, w: 9, h: 0.55,
    fontSize: 28, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.72, w: 9, h: 0.02, fill: { color: C.slateLight }, line: { color: C.slateLight } });

  // Architecture boxes
  const layers = [
    { label: "CLI Python (main.py)", color: C.cyan, x: 3.5, y: 0.9, w: 3, h: 0.6 },
    { label: "menu_ia_local.py\nDetecção nvidia-smi", color: C.purpleLight, x: 0.3, y: 1.85, w: 2.8, h: 0.7 },
    { label: "scan_amd/\nexecutar_scan.py", color: C.amdRed, x: 0.3, y: 2.95, w: 2.8, h: 0.7 },
    { label: "scan_nvidia/\nexecutar_scan.py", color: C.nvidiaGreen, x: 3.4, y: 2.95, w: 2.8, h: 0.7 },
    { label: "executar_scan_ia.py\nHTTP → LM Studio :1234", color: C.gold, x: 6.5, y: 2.95, w: 3.0, h: 0.7 },
    { label: "logs/amd/reports/\namd_report_*.json + _AI_*", color: C.amdRed, x: 0.3, y: 4.05, w: 2.8, h: 0.65 },
    { label: "logs/nvidia/reports/\nnvidia_report_*.json + _AI_*", color: C.nvidiaGreen, x: 3.4, y: 4.05, w: 2.8, h: 0.65 },
    { label: "LM Studio Server\n(GPU local)", color: C.gold, x: 6.5, y: 4.05, w: 3.0, h: 0.65 },
  ];

  layers.forEach(l => {
    s.addShape(pres.shapes.RECTANGLE, { x: l.x, y: l.y, w: l.w, h: l.h, fill: { color: l.color, transparency: 75 }, line: { color: l.color, width: 1.5 }, shadow: makeShadow() });
    s.addText(l.label, { x: l.x, y: l.y, w: l.w, h: l.h, fontSize: 10, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
  });

  // Arrows (simplified as lines)
  const arrows = [
    [5, 1.5, 5, 1.85],    // CLI → menu
    [1.7, 2.55, 1.7, 2.95], // menu → amd
    [4.8, 2.55, 4.8, 2.95], // menu → nvidia
    [1.7, 3.65, 1.7, 4.05], // amd → logs/amd
    [4.8, 3.65, 4.8, 4.05], // nvidia → logs/nvidia
    [8.0, 3.65, 8.0, 4.05], // lm → GPU logs
    [6.5, 3.30, 6.5, 2.95], // executar → lm area
  ];

  arrows.forEach(([x1, y1, x2, y2]) => {
    const w = Math.abs(x2 - x1) || 0.01;
    const h = Math.abs(y2 - y1) || 0.01;
    s.addShape(pres.shapes.LINE, {
      x: Math.min(x1, x2), y: Math.min(y1, y2), w, h,
      line: { color: C.muted, width: 1.2, dashType: "sysDot" },
    });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.45, w: 10, h: 0.175, fill: { color: C.slate }, line: { color: C.slate } });
  s.addText("ASPM IA FIAP — Challenge 2026 Pride Security", { x: 0.5, y: 5.45, w: 9, h: 0.175, fontSize: 9, color: C.muted, align: "left", valign: "middle", margin: 0 });
}

// ============================================================
// SLIDE 4 — IA LOCAL: AMD VS NVIDIA
// ============================================================
{
  let s = pres.addSlide();
  s.background = { color: C.darkMid };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.gold }, line: { color: C.gold } });

  s.addText("IA Local: AMD Radeon vs NVIDIA GeForce", {
    x: 0.5, y: 0.18, w: 9, h: 0.55,
    fontSize: 26, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.72, w: 9, h: 0.02, fill: { color: C.slateLight }, line: { color: C.slateLight } });

  // Divider center
  s.addShape(pres.shapes.LINE, { x: 5.0, y: 0.85, w: 0, h: 4.5, line: { color: C.slateLight, width: 1.5 } });

  // AMD Column
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 0.9, w: 4.4, h: 0.58, fill: { color: C.amdRed }, line: { color: C.amdRed }, shadow: makeShadow() });
  s.addText("🔴  AMD Radeon — Desktop Mode", { x: 0.3, y: 0.9, w: 4.4, h: 0.58, fontSize: 14, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });

  const amdPoints = [
    "Motor: scan_amd/executar_scan.py",
    "Relat.: amd_report_<timestamp>.json",
    "Logs:  logs/amd/system/sistema_amd.log",
    "Metadado hardware: AMD Radeon RX 7800",
    "Ativado por padrão (sem nvidia-smi)",
    "LM Studio usa GPU AMD disponível",
  ];
  amdPoints.forEach((p, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x: 0.35, y: 1.62 + i * 0.56, w: 0.22, h: 0.34, fill: { color: C.amdRed, transparency: 40 }, line: { color: C.amdRed } });
    s.addText("", { x: 0.35, y: 1.62 + i * 0.56, w: 0.22, h: 0.34, margin: 0 });
    s.addText(p, { x: 0.65, y: 1.62 + i * 0.56, w: 4.1, h: 0.36, fontSize: 11, color: C.mutedLight, valign: "middle", margin: 0 });
  });

  // NVIDIA Column
  s.addShape(pres.shapes.RECTANGLE, { x: 5.3, y: 0.9, w: 4.4, h: 0.58, fill: { color: C.nvidiaGreen }, line: { color: C.nvidiaGreen }, shadow: makeShadow() });
  s.addText("🟢  NVIDIA GeForce — Notebook Mode", { x: 5.3, y: 0.9, w: 4.4, h: 0.58, fontSize: 14, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });

  const nvidiaPoints = [
    "Motor: scan_nvidia/executar_scan.py",
    "Relat.: nvidia_report_<timestamp>.json",
    "Logs:  logs/nvidia/system/sistema_nvidia.log",
    "Metadado hardware: NVIDIA GeForce RTX",
    "Ativado automaticamente com nvidia-smi",
    "LM Studio usa CUDA + GPU NVIDIA",
  ];
  nvidiaPoints.forEach((p, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x: 5.35, y: 1.62 + i * 0.56, w: 0.22, h: 0.34, fill: { color: C.nvidiaGreen, transparency: 40 }, line: { color: C.nvidiaGreen } });
    s.addText(p, { x: 5.65, y: 1.62 + i * 0.56, w: 4.1, h: 0.36, fontSize: 11, color: C.mutedLight, valign: "middle", margin: 0 });
  });

  // Bottom note
  s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y: 5.1, w: 9.2, h: 0.28, fill: { color: C.slate }, line: { color: C.slateLight } });
  s.addText("A separação AMD/NVIDIA serve à organização de artefatos de auditoria. A GPU usada na inferência é controlada pelo LM Studio na máquina local.", {
    x: 0.4, y: 5.1, w: 9.2, h: 0.28, fontSize: 9, color: C.muted, align: "center", valign: "middle", margin: 0,
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.45, w: 10, h: 0.175, fill: { color: C.slate }, line: { color: C.slate } });
  s.addText("ASPM IA FIAP — Challenge 2026 Pride Security", { x: 0.5, y: 5.45, w: 9, h: 0.175, fontSize: 9, color: C.muted, align: "left", valign: "middle", margin: 0 });
}

// ============================================================
// SLIDE 5 — MOTOR DE ASSINATURAS: VULNERABILIDADES DETECTADAS
// ============================================================
{
  let s = pres.addSlide();
  s.background = { color: C.dark };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });
  s.addText("Motor de Assinaturas — Vulnerabilidades Detectadas", {
    x: 0.5, y: 0.18, w: 9, h: 0.5,
    fontSize: 24, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.66, w: 9, h: 0.02, fill: { color: C.slateLight }, line: { color: C.slateLight } });

  const vulns = [
    { name: "SQL Injection Provável",       sev: "CRÍTICO", color: "EF4444", cwe: "CWE-89"  },
    { name: "Execução de Risco (RCE)",       sev: "CRÍTICO", color: "EF4444", cwe: "CWE-78/94" },
    { name: "Desserialização Insegura",      sev: "CRÍTICO", color: "EF4444", cwe: "CWE-502" },
    { name: "Credenciais Hardcoded",         sev: "ALTO",    color: "F97316", cwe: "CWE-798" },
    { name: "XSS (Cross-Site Scripting)",    sev: "ALTO",    color: "F97316", cwe: "CWE-79"  },
    { name: "Path Traversal / LFI",          sev: "ALTO",    color: "F97316", cwe: "CWE-22"  },
    { name: "SSRF",                          sev: "ALTO",    color: "F97316", cwe: "CWE-918" },
    { name: "TLS/SSL Inseguro",              sev: "ALTO",    color: "F97316", cwe: "CWE-295" },
    { name: "JWT Inseguro",                  sev: "ALTO",    color: "F97316", cwe: "CWE-347" },
    { name: "XXE (XML External Entity)",     sev: "ALTO",    color: "F97316", cwe: "CWE-611" },
    { name: "Logging de Dados Sensíveis",    sev: "MÉDIO",   color: "FBBF24", cwe: "CWE-532" },
    { name: "Configuração Insegura / CORS",  sev: "BAIXO",   color: "10B981", cwe: "CWE-16"  },
    { name: "Entrada Externa p/ Revisão",    sev: "BAIXO",   color: "10B981", cwe: "CWE-20"  },
    { name: "Regex Vulnerável (ReDoS)",      sev: "BAIXO",   color: "10B981", cwe: "CWE-1333"},
  ];

  const cols = 2;
  const perCol = Math.ceil(vulns.length / cols);

  vulns.forEach((v, i) => {
    const col = Math.floor(i / perCol);
    const row = i % perCol;
    const x = 0.35 + col * 4.9;
    const y = 0.8 + row * 0.65;

    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.6, h: 0.52, fill: { color: C.slate }, line: { color: C.slateLight } });
    // Severity badge
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.9, h: 0.52, fill: { color: v.color, transparency: 30 }, line: { color: v.color } });
    s.addText(v.sev, { x, y, w: 0.9, h: 0.52, fontSize: 8, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    s.addText(v.name, { x: x + 0.95, y, w: 2.7, h: 0.52, fontSize: 10, color: C.white, valign: "middle", margin: 0 });
    s.addText(v.cwe, { x: x + 3.65, y, w: 0.95, h: 0.52, fontSize: 9, color: C.muted, align: "right", valign: "middle", margin: 0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.45, w: 10, h: 0.175, fill: { color: C.slate }, line: { color: C.slate } });
  s.addText("14 tipos de vulnerabilidade — baseados em OWASP Top 10 e CWEs", { x: 0.5, y: 5.45, w: 9, h: 0.175, fontSize: 9, color: C.muted, align: "left", valign: "middle", margin: 0 });
}

// ============================================================
// SLIDE 6 — INTEGRAÇÃO COM LLM LOCAL (LM Studio)
// ============================================================
{
  let s = pres.addSlide();
  s.background = { color: C.darkMid };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.gold }, line: { color: C.gold } });
  s.addText("Integração com LLM Local — LM Studio", {
    x: 0.5, y: 0.18, w: 9, h: 0.5,
    fontSize: 26, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.66, w: 9, h: 0.02, fill: { color: C.slateLight }, line: { color: C.slateLight } });

  // Flow diagram: 5 steps
  const steps = [
    { n: "1", label: "Usuário executa\nscan do projeto", color: C.cyan },
    { n: "2", label: "Motor gera\nJSON de achados", color: C.purpleLight },
    { n: "3", label: "CLI envia prompt\nPOST /v1/chat/completions", color: C.gold },
    { n: "4", label: "LM Studio processa\ncom GPU local", color: C.nvidiaGreen },
    { n: "5", label: "Parecer salvo como\n.md e .txt", color: C.cyan },
  ];

  steps.forEach((st, i) => {
    const x = 0.25 + i * 1.9;
    // Box
    s.addShape(pres.shapes.RECTANGLE, { x, y: 0.85, w: 1.65, h: 1.3, fill: { color: C.slate }, line: { color: st.color, width: 2 }, shadow: makeShadow() });
    // Number circle
    s.addShape(pres.shapes.OVAL, { x: x + 0.57, y: 0.72, w: 0.5, h: 0.5, fill: { color: st.color }, line: { color: st.color } });
    s.addText(st.n, { x: x + 0.57, y: 0.72, w: 0.5, h: 0.5, fontSize: 14, bold: true, color: C.dark, align: "center", valign: "middle", margin: 0 });
    s.addText(st.label, { x, y: 0.85, w: 1.65, h: 1.3, fontSize: 10, color: C.white, align: "center", valign: "middle", margin: 0 });
    // Arrow
    if (i < steps.length - 1) {
      s.addShape(pres.shapes.LINE, { x: x + 1.65, y: 1.5, w: 0.25, h: 0, line: { color: C.muted, width: 2 } });
    }
  });

  // Prompt architecture
  s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y: 2.5, w: 9.2, h: 2.7, fill: { color: C.slate }, line: { color: C.slateLight } });
  s.addText("Como funciona a análise cognitiva", { x: 0.55, y: 2.58, w: 8.8, h: 0.38, fontSize: 14, bold: true, color: C.gold, margin: 0 });

  const details = [
    { icon: "🧠", text: "System prompt: CSO Sênior — gera relatório Markdown com tabela de priorização, riscos, falsos positivos e próximos passos" },
    { icon: "📤", text: "User prompt: contexto ASPM + amostra de até 20 achados do JSON (índice, severidade, tipo, arquivo, linha, trecho de código)" },
    { icon: "🌡️", text: "Temperature: 0.1 — resposta determinística e técnica, adequada para relatórios de segurança" },
    { icon: "⏱️", text: "Timeout: 120s — compatível com modelos grandes em GPU (ex.: Llama 3, Gemma, Mistral)" },
    { icon: "🔗", text: "API compatível com OpenAI: GET /v1/models (heartbeat) + POST /v1/chat/completions — funciona com qualquer servidor LM Studio" },
  ];

  details.forEach((d, i) => {
    s.addText(d.icon + "  " + d.text, {
      x: 0.6, y: 3.03 + i * 0.4, w: 8.8, h: 0.36,
      fontSize: 11, color: C.mutedLight, margin: 0,
    });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.45, w: 10, h: 0.175, fill: { color: C.slate }, line: { color: C.slate } });
  s.addText("ASPM IA FIAP — Challenge 2026 Pride Security", { x: 0.5, y: 5.45, w: 9, h: 0.175, fontSize: 9, color: C.muted, align: "left", valign: "middle", margin: 0 });
}

// ============================================================
// SLIDE 7 — FLUXO DETALHADO DE ANÁLISE
// ============================================================
{
  let s = pres.addSlide();
  s.background = { color: C.dark };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });
  s.addText("Fluxo Detalhado — Scan + Parecer IA", {
    x: 0.5, y: 0.18, w: 9, h: 0.5,
    fontSize: 26, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.66, w: 9, h: 0.02, fill: { color: C.slateLight }, line: { color: C.slateLight } });

  // Swimlane headers
  const lanes = [
    { label: "Usuário", color: C.purple, x: 0.3 },
    { label: "CLI Python", color: C.cyan, x: 2.8 },
    { label: "Arquivo JSON", color: C.gold, x: 5.3 },
    { label: "LM Studio :1234", color: C.nvidiaGreen, x: 7.6 },
  ];

  lanes.forEach(l => {
    s.addShape(pres.shapes.RECTANGLE, { x: l.x, y: 0.78, w: 2.1, h: 0.42, fill: { color: l.color, transparency: 20 }, line: { color: l.color } });
    s.addText(l.label, { x: l.x, y: 0.78, w: 2.1, h: 0.42, fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    // Vertical lane line
    s.addShape(pres.shapes.LINE, { x: l.x + 1.05, y: 1.2, w: 0, h: 3.85, line: { color: l.color, width: 0.8, dashType: "sysDot", transparency: 60 } });
  });

  // Sequence steps
  const seqSteps = [
    { from: 0, to: 1, label: "Informa caminho do projeto",          y: 1.38 },
    { from: 1, to: 1, label: "Motor de assinaturas (scan_amd / scan_nvidia)", y: 1.85, self: true },
    { from: 1, to: 2, label: "Grava relatório JSON",                 y: 2.32 },
    { from: 0, to: 1, label: "Solicita análise com IA",             y: 2.78 },
    { from: 1, to: 2, label: "Lê vulnerabilidades do JSON",         y: 3.25 },
    { from: 1, to: 3, label: "POST /v1/chat/completions",           y: 3.72 },
    { from: 3, to: 1, label: "Texto do parecer (LLM)",              y: 4.18, back: true },
    { from: 1, to: 0, label: "Exibe parecer + salva .md/.txt",      y: 4.65, back: true },
  ];

  const laneX = [0.3 + 1.05, 2.8 + 1.05, 5.3 + 1.05, 7.6 + 1.05];

  seqSteps.forEach(step => {
    const x1 = laneX[step.from];
    const x2 = laneX[step.to];
    const y = step.y;
    const minX = Math.min(x1, x2);
    const w = Math.abs(x2 - x1) || 0.5;

    s.addShape(pres.shapes.LINE, { x: minX, y, w, h: 0, line: { color: step.back ? C.muted : C.cyan, width: 1.5, dashType: step.self ? "dash" : "solid" } });
    s.addText(step.label, {
      x: minX + 0.05, y: y - 0.23, w: w - 0.1, h: 0.22,
      fontSize: 9, color: C.mutedLight, align: "center", margin: 0,
    });
    // Dot at target end
    s.addShape(pres.shapes.OVAL, { x: x2 - 0.06, y: y - 0.06, w: 0.12, h: 0.12, fill: { color: step.back ? C.muted : C.cyan }, line: { color: step.back ? C.muted : C.cyan } });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.45, w: 10, h: 0.175, fill: { color: C.slate }, line: { color: C.slate } });
  s.addText("ASPM IA FIAP — Challenge 2026 Pride Security", { x: 0.5, y: 5.45, w: 9, h: 0.175, fontSize: 9, color: C.muted, align: "left", valign: "middle", margin: 0 });
}

// ============================================================
// SLIDE 8 — RELATÓRIOS GERADOS
// ============================================================
{
  let s = pres.addSlide();
  s.background = { color: C.darkMid };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.purple }, line: { color: C.purple } });
  s.addText("Relatórios Gerados pelo Sistema", {
    x: 0.5, y: 0.18, w: 9, h: 0.5,
    fontSize: 26, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.66, w: 9, h: 0.02, fill: { color: C.slateLight }, line: { color: C.slateLight } });

  // File tree
  const tree = [
    { indent: 0, text: "api_python/logs/", color: C.gold, bold: true },
    { indent: 1, text: "erro_sistema.log           — Logger raiz ASPM (todos os módulos)", color: C.muted, bold: false },
    { indent: 1, text: "amd/", color: C.amdRed, bold: true },
    { indent: 2, text: "system/sistema_amd.log     — Eventos do motor AMD", color: C.muted, bold: false },
    { indent: 2, text: "reports/", color: C.amdRed, bold: false },
    { indent: 3, text: "amd_report_YYYYMMDD_HHMMSS.json   — Scan de assinaturas", color: C.white, bold: false },
    { indent: 3, text: "..._AI_PREMIUM.md                 — Parecer IA em Markdown", color: C.cyan, bold: false },
    { indent: 3, text: "..._AI_LEITURA.txt                — Parecer IA p/ impressão", color: C.cyan, bold: false },
    { indent: 1, text: "nvidia/", color: C.nvidiaGreen, bold: true },
    { indent: 2, text: "system/sistema_nvidia.log  — Eventos do motor NVIDIA", color: C.muted, bold: false },
    { indent: 2, text: "reports/", color: C.nvidiaGreen, bold: false },
    { indent: 3, text: "nvidia_report_YYYYMMDD_HHMMSS.json — Scan de assinaturas", color: C.white, bold: false },
    { indent: 3, text: "..._AI_PREMIUM.md                  — Parecer IA em Markdown", color: C.cyan, bold: false },
    { indent: 3, text: "..._AI_LEITURA.txt                 — Parecer IA p/ impressão", color: C.cyan, bold: false },
  ];

  s.addShape(pres.shapes.RECTANGLE, { x: 0.35, y: 0.78, w: 9.3, h: 4.58, fill: { color: C.dark }, line: { color: C.slateLight } });

  tree.forEach((t, i) => {
    const x = 0.5 + t.indent * 0.28;
    const y = 0.88 + i * 0.3;
    if (t.indent === 0 || t.indent === 1) {
      s.addText((t.indent > 0 ? "├─ " : "") + t.text, {
        x, y, w: 9.0 - t.indent * 0.28, h: 0.28,
        fontSize: 10.5, bold: t.bold, color: t.color, fontFace: "Consolas", margin: 0,
      });
    } else {
      const prefix = t.indent === 2 ? "│  ├─ " : "│  │  ├─ ";
      s.addText(prefix + t.text, {
        x, y, w: 9.0 - t.indent * 0.28, h: 0.28,
        fontSize: 10.5, bold: t.bold, color: t.color, fontFace: "Consolas", margin: 0,
      });
    }
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.45, w: 10, h: 0.175, fill: { color: C.slate }, line: { color: C.slate } });
  s.addText("ASPM IA FIAP — Challenge 2026 Pride Security", { x: 0.5, y: 5.45, w: 9, h: 0.175, fontSize: 9, color: C.muted, align: "left", valign: "middle", margin: 0 });
}

// ============================================================
// SLIDE 9 — RESULTADOS REAIS (SCAN NVIDIA)
// ============================================================
{
  let s = pres.addSlide();
  s.background = { color: C.dark };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.nvidiaGreen }, line: { color: C.nvidiaGreen } });
  s.addText("Resultados Reais — Scan NVIDIA GeForce RTX", {
    x: 0.5, y: 0.18, w: 9, h: 0.5,
    fontSize: 24, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.66, w: 9, h: 0.02, fill: { color: C.slateLight }, line: { color: C.slateLight } });

  // Big stat cards
  const stats = [
    { value: "3.628", label: "Arquivos\nAnalisados", color: C.nvidiaGreen },
    { value: "1.548", label: "Achados\nDetectados", color: C.gold },
    { value: "1 min", label: "Tempo de\nGeração IA", color: C.cyan },
    { value: "20",    label: "Achados no\nPrompt (amostra)", color: C.purpleLight },
  ];

  stats.forEach((st, i) => {
    const x = 0.35 + i * 2.35;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 0.85, w: 2.1, h: 1.5, fill: { color: C.slate }, line: { color: st.color, width: 2 }, shadow: makeShadow() });
    s.addText(st.value, { x, y: 0.92, w: 2.1, h: 0.8, fontSize: 36, bold: true, color: st.color, align: "center", valign: "middle", margin: 0 });
    s.addText(st.label, { x, y: 1.65, w: 2.1, h: 0.65, fontSize: 11, color: C.mutedLight, align: "center", valign: "top", margin: 0 });
  });

  // Chart — vulnerability distribution
  s.addChart(pres.charts.BAR, [
    {
      name: "Achados por Severidade",
      labels: ["CRÍTICO", "ALTO", "MÉDIO", "BAIXO"],
      values: [312, 580, 290, 366],
    }
  ], {
    x: 0.35, y: 2.6, w: 5.5, h: 2.7,
    barDir: "col",
    chartColors: ["EF4444", "F97316", "FBBF24", "10B981"],
    chartArea: { fill: { color: C.slate }, roundedCorners: false },
    catAxisLabelColor: C.mutedLight,
    valAxisLabelColor: C.mutedLight,
    valGridLine: { color: "2D3B55", size: 0.5 },
    catGridLine: { style: "none" },
    showValue: true,
    dataLabelPosition: "outEnd",
    dataLabelColor: C.white,
    showLegend: false,
    showTitle: true,
    title: "Distribuição por Severidade",
    titleColor: C.white,
    titleFontSize: 12,
  });

  // Top risks
  s.addShape(pres.shapes.RECTANGLE, { x: 6.1, y: 2.6, w: 3.55, h: 2.7, fill: { color: C.slate }, line: { color: C.slateLight } });
  s.addText("Principais Achados CRÍTICOS", { x: 6.1, y: 2.65, w: 3.55, h: 0.38, fontSize: 12, bold: true, color: C.gold, align: "center", margin: 0 });

  const topRisks = [
    { label: "shell=True (RCE)",          pct: "41%" },
    { label: "subprocess.run( )",         pct: "28%" },
    { label: "SQL dinâmico (f-string)",   pct: "18%" },
    { label: "pickle.loads( )",           pct: "13%" },
  ];

  topRisks.forEach((r, i) => {
    const y = 3.12 + i * 0.52;
    s.addText(r.label, { x: 6.25, y, w: 2.5, h: 0.38, fontSize: 10, color: C.white, valign: "middle", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 8.8, y: y + 0.08, w: 0.72, h: 0.28, fill: { color: "EF4444" }, line: { color: "EF4444" } });
    s.addText(r.pct, { x: 8.8, y: y + 0.08, w: 0.72, h: 0.28, fontSize: 10, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.45, w: 10, h: 0.175, fill: { color: C.slate }, line: { color: C.slate } });
  s.addText("Fonte: nvidia_report_20260511_171723_AI_PREMIUM.md", { x: 0.5, y: 5.45, w: 9, h: 0.175, fontSize: 9, color: C.muted, align: "left", valign: "middle", margin: 0 });
}

// ============================================================
// SLIDE 10 — SEGURANÇA E PRIVACIDADE
// ============================================================
{
  let s = pres.addSlide();
  s.background = { color: C.darkMid };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });
  s.addText("Segurança e Privacidade por Design", {
    x: 0.5, y: 0.18, w: 9, h: 0.5,
    fontSize: 26, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.66, w: 9, h: 0.02, fill: { color: C.slateLight }, line: { color: C.slateLight } });

  const privItems = [
    {
      icon: "🔒",
      title: "100% Local — Sem Nuvem",
      body: "Todo tráfego entre a CLI e o LM Studio passa apenas pelo loopback (localhost:1234). Nenhum dado do projeto é enviado para servidores externos.",
      color: C.cyan,
    },
    {
      icon: "🏠",
      title: "Inferência na Própria GPU",
      body: "O LLM roda na GPU da máquina local (AMD via drivers nativos ou NVIDIA via CUDA). A chave privada do projeto nunca sai do ambiente corporativo.",
      color: C.nvidiaGreen,
    },
    {
      icon: "🧠",
      title: "Análise Heurística — Validação Humana",
      body: "O parecer da IA prioriza revisão humana. O scan é por assinaturas (ASPM educativo) — não substitui pentest ou pipeline CI/CD de segurança.",
      color: C.gold,
    },
    {
      icon: "📋",
      title: "Trilha de Auditoria por GPU",
      body: "Logs separados por fabricante (AMD/NVIDIA) com timestamps UTC, UTC-03 e sistema. Rastreabilidade total de cada scan realizado.",
      color: C.purpleLight,
    },
  ];

  privItems.forEach((item, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.4 + col * 4.9;
    const y = 0.88 + row * 2.15;

    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.55, h: 1.9, fill: { color: C.slate }, line: { color: item.color, width: 1.5 }, shadow: makeShadow() });
    s.addText(item.icon, { x, y: y + 0.12, w: 0.9, h: 0.9, fontSize: 28, align: "center", valign: "middle", margin: 0 });
    s.addText(item.title, { x: x + 0.9, y: y + 0.12, w: 3.5, h: 0.42, fontSize: 13, bold: true, color: item.color, margin: 0 });
    s.addText(item.body, { x: x + 0.9, y: y + 0.54, w: 3.5, h: 1.22, fontSize: 10.5, color: C.mutedLight, margin: 0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.45, w: 10, h: 0.175, fill: { color: C.slate }, line: { color: C.slate } });
  s.addText("ASPM IA FIAP — Challenge 2026 Pride Security", { x: 0.5, y: 5.45, w: 9, h: 0.175, fontSize: 9, color: C.muted, align: "left", valign: "middle", margin: 0 });
}

// ============================================================
// SLIDE 11 — EQUIPE
// ============================================================
{
  let s = pres.addSlide();
  s.background = { color: C.dark };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.purple }, line: { color: C.purple } });
  s.addText("Nossa Equipe", {
    x: 0.5, y: 0.18, w: 9, h: 0.5,
    fontSize: 28, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });

  s.addText("Turma 1TDCPV — FIAP Challenge 2026 Pride Security", {
    x: 0.5, y: 0.68, w: 9, h: 0.32,
    fontSize: 13, color: C.muted, margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.97, w: 9, h: 0.02, fill: { color: C.slateLight }, line: { color: C.slateLight } });

  const members = [
    { name: "Paulo André Carminati",               rm: "RM570877", role: "Arquitetura & Backend" },
    { name: "Gustav Quental Scorsi",               rm: "RM569862", role: "Segurança & Testes"    },
    { name: "André Archanjo dos Santos Torres",     rm: "RM570458", role: "Motor de Scan"         },
    { name: "Luiz Carlos da Paixão dos Santos",     rm: "RM573009", role: "IA Local & GPU"        },
    { name: "Victor Henrique de Barros Oliveira",   rm: "RM570012", role: "Relatórios & CLI"      },
  ];

  const colors = [C.cyan, C.purpleLight, C.gold, C.nvidiaGreen, C.amdRed];

  members.forEach((m, i) => {
    const col = i < 3 ? i : i - 3;
    const row = i < 3 ? 0 : 1;
    const w = i < 3 ? 2.9 : 4.35;
    const startX = i < 3 ? 0.35 : 0.35 + (i - 3) * 4.65;
    const x = i < 3 ? startX + col * 3.1 : startX;
    const y = 1.15 + row * 2.2;
    const cardW = i < 3 ? 2.9 : 4.35;

    s.addShape(pres.shapes.RECTANGLE, { x, y, w: cardW, h: 1.85, fill: { color: C.slate }, line: { color: colors[i], width: 1.5 }, shadow: makeShadow() });
    // Initial circle
    s.addShape(pres.shapes.OVAL, { x: x + 0.15, y: y + 0.2, w: 0.7, h: 0.7, fill: { color: colors[i] }, line: { color: colors[i] } });
    s.addText(m.name.charAt(0), { x: x + 0.15, y: y + 0.2, w: 0.7, h: 0.7, fontSize: 18, bold: true, color: C.dark, align: "center", valign: "middle", margin: 0 });

    s.addText(m.name, { x: x + 0.98, y: y + 0.18, w: cardW - 1.1, h: 0.45, fontSize: 11, bold: true, color: C.white, margin: 0 });
    s.addText(m.rm, { x: x + 0.98, y: y + 0.62, w: cardW - 1.1, h: 0.3, fontSize: 10, color: C.muted, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.15, y: y + 1.08, w: cardW - 0.3, h: 0.02, fill: { color: C.slateLight }, line: { color: C.slateLight } });
    s.addText(m.role, { x: x + 0.15, y: y + 1.18, w: cardW - 0.3, h: 0.45, fontSize: 11, color: colors[i], align: "center", margin: 0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.45, w: 10, h: 0.175, fill: { color: C.slate }, line: { color: C.slate } });
  s.addText("ASPM IA FIAP — Challenge 2026 Pride Security", { x: 0.5, y: 5.45, w: 9, h: 0.175, fontSize: 9, color: C.muted, align: "left", valign: "middle", margin: 0 });
}

// ============================================================
// SLIDE 12 — CONCLUSÃO E PRÓXIMOS PASSOS
// ============================================================
{
  let s = pres.addSlide();
  s.background = { color: C.dark };

  // Top + bottom accent
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.08, fill: { color: C.cyan }, line: { color: C.cyan } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.38, w: 10, h: 0.245, fill: { color: C.slate }, line: { color: C.slate } });

  // Background circles (decorative)
  s.addShape(pres.shapes.OVAL, { x: -1, y: 2.5, w: 5, h: 5, fill: { color: C.purple, transparency: 90 }, line: { color: C.purple, transparency: 90, width: 1 } });
  s.addShape(pres.shapes.OVAL, { x: 7, y: -0.5, w: 4, h: 4, fill: { color: C.cyan, transparency: 90 }, line: { color: C.cyan, transparency: 90, width: 1 } });

  s.addText("Conclusão", { x: 0.6, y: 0.22, w: 9, h: 0.52, fontSize: 30, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
  s.addShape(pres.shapes.LINE, { x: 0.6, y: 0.73, w: 4, h: 0, line: { color: C.cyan, width: 2 } });

  const conclusions = [
    "CLI modular capaz de analisar projetos multi-linguagem com 14 tipos de vulnerabilidade",
    "Integração com LLM local via LM Studio garante privacidade e análise cognitiva offline",
    "Separação AMD/NVIDIA facilita laboratórios didáticos e auditoria por hardware",
    "Relatório real: 3.628 arquivos, 1.548 achados — parecer executivo gerado em <1min",
  ];

  conclusions.forEach((c, i) => {
    s.addShape(pres.shapes.OVAL, { x: 0.55, y: 0.95 + i * 0.58, w: 0.24, h: 0.24, fill: { color: C.cyan }, line: { color: C.cyan } });
    s.addText(c, { x: 0.92, y: 0.92 + i * 0.58, w: 8.5, h: 0.3, fontSize: 12, color: C.white, valign: "middle", margin: 0 });
  });

  s.addText("Próximos Passos", { x: 0.6, y: 3.28, w: 9, h: 0.4, fontSize: 18, bold: true, color: C.gold, margin: 0 });

  const nexts = [
    { icon: "🔗", text: "Integração com pipelines CI/CD (GitHub Actions, GitLab CI)" },
    { icon: "🌐", text: "Interface Web com dashboard de vulnerabilidades" },
    { icon: "📦", text: "Banco de dados para persistência de histórico de scans" },
    { icon: "🤖", text: "Suporte a múltiplos modelos LLM e backends GPU (ROCm, TensorRT)" },
  ];

  nexts.forEach((n, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.45 + col * 4.9;
    const y = 3.78 + row * 0.65;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.55, h: 0.52, fill: { color: C.slate }, line: { color: C.slateLight } });
    s.addText(n.icon + "  " + n.text, { x: x + 0.12, y, w: 4.3, h: 0.52, fontSize: 11, color: C.mutedLight, valign: "middle", margin: 0 });
  });

  s.addText("github.com/carmipa/CHALLENGE_2026_PRIDE_SECURITY  |  Turma 1TDCPV  |  FIAP 2026", {
    x: 0.5, y: 5.38, w: 9, h: 0.245,
    fontSize: 9, color: C.muted, align: "center", valign: "middle", margin: 0,
  });
}

// ============================================================
// WRITE FILE
// ============================================================
pres.writeFile({ fileName: "ASPM_IA_FIAP_Apresentacao_GPU.pptx" })
  .then(() => console.log("✅  ASPM_IA_FIAP_Apresentacao_GPU.pptx gerado com sucesso!"))
  .catch(err => console.error("❌ Erro:", err));
