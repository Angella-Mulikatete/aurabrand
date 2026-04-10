"use client";

import React, { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Loader2, Wand2, Download, FileText, MonitorPlay, Sparkles, 
  Palette, Type, Image as ImageIcon, Upload, GraduationCap, XCircle, CheckCircle2 
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type OutputFile = {
  url: string;
  type: string;
  title: string;
};

const COLOR_PALETTES = [
  { name: "Aura Purple", value: "#7C3AED" },
  { name: "Ocean Blue", value: "#3B82F6" },
  { name: "Emerald Green", value: "#10B981" },
  { name: "Crimson Red", value: "#EF4444" },
  { name: "Amber Gold", value: "#F59E0B" },
];

const FONTS = ["Fira Sans", "Roboto", "Inter", "Arial", "Georgia"];

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [brandName, setBrandName] = useState("AuraBrand");
  const [primaryColor, setPrimaryColor] = useState("#7C3AED");
  const [fontFamily, setFontFamily] = useState("Fira Sans");
  const [enableVisuals, setEnableVisuals] = useState(true);
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLearning, setIsLearning] = useState(false);
  const [activeTab, setActiveTab] = useState<"PRESENTATION" | "DOCUMENT">("PRESENTATION");
  const [results, setResults] = useState<OutputFile[]>([]);
  const [finalDocument, setFinalDocument] = useState<string | null>(null);
  const [refinePrompt, setRefinePrompt] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [progressMsg, setProgressMsg] = useState("Initializing agent...");
  const [uploadStatus, setUploadStatus] = useState<{msg: string, type: 'success' | 'error' | 'idle'}>({msg: '', type: 'idle'});
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const progressMessages = [
    "Initializing LangGraph agent loop...",
    "Consulting learned benchmarks...",
    "Researching brand guidelines...",
    "Synthesizing assets via Pollinations AI...",
    "Building structured slides...",
    "Finalizing branded document...",
  ];

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt) return;

    setIsGenerating(true);
    setError(null);
    setResults([]);
    
    let msgIdx = 0;
    setProgressMsg(progressMessages[0]);
    const interval = setInterval(() => {
      msgIdx = (msgIdx + 1) % progressMessages.length;
      setProgressMsg(progressMessages[msgIdx]);
    }, 4500);

    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_request: prompt,
          intent: activeTab,
          brand_name: brandName,
          primary_color: primaryColor,
          font_family: fontFamily,
          enable_images: enableVisuals
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Generation failed.");
      }

      const data = await response.json();

      const outputs: OutputFile[] = (data.output_files || []).map((fp: string) => {
        const filename = fp.split("/").pop() || fp;
        const ext = filename.split(".").pop()?.toUpperCase() || "FILE";
        return {
          url: `${API_URL}/outputs/${filename}`,
          type: ext,
          title: filename,
        };
      });

      setResults(outputs);
      setFinalDocument(data.final_document || null);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Could not connect to the API server.";
      setError(message);
    } finally {
      clearInterval(interval);
      setIsGenerating(false);
    }
  };

  const handleRefine = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!refinePrompt || !finalDocument) return;

    setIsGenerating(true);
    setError(null);
    setResults([]);
    
    let msgIdx = 0;
    setProgressMsg("Refining document with feedback...");
    const interval = setInterval(() => {
      msgIdx = (msgIdx + 1) % progressMessages.length;
      setProgressMsg(progressMessages[msgIdx]);
    }, 4500);

    try {
      const response = await fetch(`${API_URL}/refine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          feedback: refinePrompt,
          previous_document: finalDocument,
          intent: activeTab,
          brand_name: brandName,
          primary_color: primaryColor,
          font_family: fontFamily,
          enable_images: enableVisuals
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Refinement failed.");
      }

      const data = await response.json();

      const outputs: OutputFile[] = (data.output_files || []).map((fp: string) => {
        const filename = fp.split("/").pop() || fp;
        const ext = filename.split(".").pop()?.toUpperCase() || "FILE";
        return {
          url: `${API_URL}/outputs/${filename}`,
          type: ext,
          title: filename,
        };
      });

      setResults(outputs);
      setFinalDocument(data.final_document || null);
      setRefinePrompt("");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Could not connect to the API server.";
      setError(message);
    } finally {
      clearInterval(interval);
      setIsGenerating(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsLearning(true);
    setUploadStatus({msg: 'Uploading & learning...', type: 'idle'});
    
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const response = await fetch(`${API_URL}/benchmarks/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Upload failed (${response.status}): ${errText.substring(0, 100)}`);
      }
      
      const data = await response.json();
      setUploadStatus({
        msg: `Successfully learned ${data.total_learned} patterns from benchmarks.`, 
        type: 'success'
      });
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Unknown error';
      setUploadStatus({msg: `Learning Failed: ${errMsg}`, type: 'error'});
    } finally {
      setIsLearning(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleResetKnowledge = async () => {
    if (!confirm("Are you sure you want to clear all learned brand patterns?")) return;
    
    try {
      const response = await fetch(`${API_URL}/benchmarks/reset`, { method: 'POST' });
      if (response.ok) {
        setUploadStatus({msg: 'Brand knowledge reset.', type: 'success'});
      }
    } catch (err) {
      setUploadStatus({msg: 'Failed to reset knowledge.', type: 'error'});
    }
  };

  return (
    <main className="min-h-screen relative overflow-hidden bg-background">
      <div className="absolute inset-0 morph-gradient opacity-20 -z-10" />
      <div className="absolute inset-0 bg-gradient-radial from-transparent via-background/60 to-background -z-10" />

      <div className="container max-w-6xl mx-auto pt-12 px-4 pb-24 text-foreground">

        <div className="text-center space-y-4 mb-16">
          {/* <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-full text-sm font-mono font-semibold border border-primary/20 mb-2">
            <Sparkles className="w-4 h-4" />
            AI-Powered Brand Synthesis Loop
          </div> */}
          <h1 className="text-5xl font-mono font-bold tracking-tight text-foreground sm:text-6xl">
            Aura<span className="text-primary">Brand</span>
          </h1>
          <p className="text-xl text-foreground/70 max-w-2xl mx-auto font-sans leading-relaxed">
            Upload benchmarks, select guidelines, and let the agent synthesize pixel-perfect, learned brand assets.
          </p>
        </div>

        <div className="grid md:grid-cols-12 gap-8 items-start">

          {/* Left Panel: Knowledge & Controls */}
          <div className="md:col-span-5 space-y-6">
            <Card className="glass-panel border-0 shadow-lg relative overflow-hidden">
              <CardHeader className="pb-4 border-b border-white/20">
                <CardTitle className="font-sans text-lg text-foreground">Benchmark Knowledge</CardTitle>
                <CardDescription className="font-sans text-xs">Help AuraBrand learn from your best work.</CardDescription>
              </CardHeader>
              <CardContent className="pt-6 space-y-4">
                <div 
                  className="border-2 border-dashed border-primary/20 rounded-xl p-6 text-center hover:border-primary/40 transition-all cursor-pointer bg-white/5 group"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    className="hidden" 
                    multiple 
                    accept=".pdf,.docx,.txt" 
                    onChange={handleFileUpload}
                  />
                  {isLearning ? (
                    <div className="flex flex-col items-center gap-2">
                      <Loader2 className="w-8 h-8 animate-spin text-primary" />
                      <p className="text-xs font-mono text-primary animate-pulse">Analyzing Patterns...</p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center gap-2">
                      <Upload className="w-8 h-8 text-primary group-hover:scale-110 transition-transform" />
                      <p className="text-sm font-sans font-medium">Upload Benchmarks</p>
                      <p className="text-[10px] text-foreground/50">Supports PDF, DOCX, TXT</p>
                    </div>
                  )}
                </div>

                {uploadStatus.msg && (
                  <div className={`flex items-center gap-2 p-3 rounded-lg text-[10px] font-mono ${
                    uploadStatus.type === 'success' ? 'bg-green-500/10 text-green-600' : 
                    uploadStatus.type === 'error' ? 'bg-red-500/10 text-red-600' : 'bg-primary/5 text-primary'
                  }`}>
                    {uploadStatus.type === 'success' ? <CheckCircle2 className="w-3 h-3" /> : 
                     uploadStatus.type === 'error' ? <XCircle className="w-3 h-3" /> : <GraduationCap className="w-3 h-3" />}
                    {uploadStatus.msg}
                    {uploadStatus.type === 'success' && (
                      <button onClick={handleResetKnowledge} className="ml-auto underline hover:text-red-600">Reset</button>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="glass-panel border-0 shadow-lg relative overflow-hidden">
              <CardHeader className="pb-4 border-b border-white/20">
                <CardTitle className="font-sans text-lg text-foreground text-primary">Brand Guidelines</CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <form onSubmit={handleGenerate} className="space-y-6">
                  {/* Brand Basic */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label className="uppercase text-[10px] tracking-wider text-foreground/60 font-bold">Brand Name</Label>
                      <Input
                        placeholder="AuraBrand"
                        className="bg-white/50 border-white/40 text-foreground focus-visible:ring-primary/40 h-10"
                        value={brandName}
                        onChange={(e) => setBrandName(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="uppercase text-[10px] tracking-wider text-foreground/60 font-bold">Output</Label>
                      <div className="flex rounded-lg p-1 bg-white/30 border border-white/40 h-10">
                        {(["PRESENTATION", "DOCUMENT"] as const).map(type => (
                          <button
                            key={type}
                            type="button"
                            onClick={() => setActiveTab(type)}
                            className={`flex-1 text-[10px] font-bold rounded transition-all cursor-pointer ${
                              activeTab === type ? "bg-white text-primary shadow-sm" : "text-foreground/40 hover:text-foreground"
                            }`}
                          >
                            {type === "PRESENTATION" ? "SLIDES" : "DOC"}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Brand Identity */}
                  <div className="p-4 rounded-xl bg-primary/5 border border-primary/10 space-y-5">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2"><Palette className="w-4 h-4 text-primary" /><Label className="uppercase text-[10px] tracking-wider text-foreground/60 font-bold">Primary Palette</Label></div>
                      <div className="flex items-center gap-3">
                        {COLOR_PALETTES.map(cp => (
                          <button key={cp.value} type="button" onClick={() => setPrimaryColor(cp.value)} className={`w-8 h-8 rounded-full border-2 transition-all hover:scale-110 shadow-sm ${primaryColor === cp.value ? "border-white ring-2 ring-primary" : "border-transparent opacity-70"}`} style={{ backgroundColor: cp.value }} />
                        ))}
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center gap-2"><Type className="w-4 h-4 text-primary" /><Label className="uppercase text-[10px] tracking-wider text-foreground/60 font-bold">Typography</Label></div>
                      <select value={fontFamily} onChange={(e) => setFontFamily(e.target.value)} className="w-full bg-white/50 border border-white/40 rounded-lg p-2 text-sm font-sans focus:outline-none focus:ring-2 focus:ring-primary/40 appearance-none cursor-pointer">{FONTS.map(f => (<option key={f} value={f}>{f}</option>))}</select>
                    </div>
                    <div className="flex items-center justify-between pt-2">
                      <div className="flex items-center gap-2"><ImageIcon className="w-4 h-4 text-primary" /><Label className="uppercase text-[10px] tracking-wider text-foreground/60 font-bold">AI Visuals</Label></div>
                      <button type="button" onClick={() => setEnableVisuals(!enableVisuals)} className={`w-12 h-6 rounded-full p-1 transition-all duration-300 ${enableVisuals ? "bg-primary" : "bg-foreground/20"}`}><div className={`w-4 h-4 bg-white rounded-full transition-all duration-300 ${enableVisuals ? "translate-x-6" : "translate-x-0"}`} /></button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="uppercase text-[10px] tracking-wider text-foreground/60 font-bold">Mission Context</Label>
                    <textarea rows={3} placeholder="Describe what you want to create..." className="w-full rounded-lg border border-white/40 bg-white/50 p-3 text-sm font-sans text-foreground placeholder:text-foreground/40 focus:outline-none focus:ring-2 focus:ring-primary/40 resize-none" value={prompt} onChange={(e) => setPrompt(e.target.value)} />
                  </div>

                  <Button type="submit" className="w-full bg-primary hover:bg-[#6d28d9] text-white shadow-lg shadow-primary/20 font-mono py-6 cursor-pointer transition-all hover:scale-[1.01]" disabled={isGenerating || !prompt}>
                    {isGenerating ? (<><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Synthesizing Brand Assets...</>) : (<><Sparkles className="mr-2 h-4 w-4" /> Dispatch Asset Synthesis</>)}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Right Panel: Output */}
          <div className="md:col-span-7 h-full">
            <Card className="glass-panel border-0 shadow-2xl h-full min-h-[700px] flex flex-col relative overflow-hidden">
               <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-accent to-primary" />
              <CardHeader className="pb-4 border-b border-white/20">
                <CardTitle className="font-mono text-xl text-foreground flex items-center gap-2">
                  <MonitorPlay className="w-5 h-5 text-accent" />
                  Asset Command Center
                </CardTitle>
                <CardDescription className="font-sans text-foreground/60">
                  Real-time synchronization for your learned brand assets.
                </CardDescription>
              </CardHeader>

              <CardContent className="flex-grow p-8 flex items-center justify-center">
                {isGenerating ? (
                  <div className="flex flex-col items-center text-foreground/70 space-y-4">
                    <div className="w-20 h-20 rounded-2xl bg-primary/20 flex items-center justify-center">
                      <Loader2 className="w-10 h-10 animate-spin text-primary" />
                    </div>
                    <p className="font-mono text-lg text-foreground animate-pulse">{progressMsg}</p>
                    <div className="w-48 h-1 bg-primary/20 rounded-full overflow-hidden">
                      <div className="h-full bg-primary rounded-full morph-gradient animate-pulse" style={{ width: "60%" }} />
                    </div>
                  </div>
                ) : error ? (
                  <div className="max-w-md text-center space-y-3">
                    <div className="w-16 h-16 rounded-2xl bg-red-100 flex items-center justify-center mx-auto">
                      <span className="text-3xl">⚠️</span>
                    </div>
                    <p className="font-mono text-red-600 font-semibold">API Error</p>
                    <p className="text-sm text-foreground/60 font-sans">{error}</p>
                  </div>
                ) : finalDocument || results.length > 0 ? (
                  <div className="w-full h-full flex flex-col space-y-4 max-h-[600px]">
                    <div className="flex-grow p-4 rounded-xl bg-white/50 border border-white overflow-y-auto font-sans text-sm text-foreground/80 whitespace-pre-wrap shadow-inner relative">
                        <div className="absolute top-2 right-2 text-[10px] font-mono opacity-50 uppercase tracking-widest">{activeTab} DRAFT</div>
                        {finalDocument || "Document generated successfully."}
                    </div>
                    
                    <form onSubmit={handleRefine} className="flex gap-2">
                        <Input 
                            className="bg-white/50 border-white/40 focus-visible:ring-primary/40 flex-grow" 
                            placeholder="Improve this draft (e.g. 'Make it more persuasive')"
                            value={refinePrompt}
                            onChange={(e) => setRefinePrompt(e.target.value)}
                        />
                        <Button type="submit" disabled={!refinePrompt || isGenerating} className="bg-accent hover:bg-accent/80 text-white cursor-pointer px-6">
                            Refine
                        </Button>
                    </form>

                    <div className="grid grid-cols-2 gap-4 mt-2">
                      {results.map((r, i) => (
                        <a key={i} href={r.url} download className="block">
                            <div className="flex items-center justify-between p-3 rounded-xl bg-white/60 border border-primary/20 hover:bg-primary/5 hover:border-primary/40 transition-all shadow-sm cursor-pointer group">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center group-hover:scale-105 transition-transform">
                                <FileText className="w-5 h-5 text-primary" />
                                </div>
                                <div>
                                <h4 className="font-bold text-foreground font-sans text-sm truncate max-w-[150px]">{r.title}</h4>
                                <p className="text-[10px] text-foreground/50 uppercase tracking-widest mt-0.5">Download {r.type}</p>
                                </div>
                            </div>
                            <Download className="w-4 h-4 text-primary opacity-50 group-hover:opacity-100 transition-opacity" />
                            </div>
                        </a>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center opacity-40">
                    <GraduationCap className="w-16 h-16 mx-auto mb-4 text-primary" />
                    <p className="font-mono text-foreground">Upload benchmarks to enhance the AI's brand intelligence.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

        </div>
      </div>
    </main>
  );
}
