import React, { useState, useCallback } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner";
import ImageAnalyzer from "./components/ImageAnalyzer";
import AnalysisHistory from "./components/AnalysisHistory";
import { Button } from "./components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";

function App() {
  const [activeTab, setActiveTab] = useState("analyzer");
  const [refreshHistory, setRefreshHistory] = useState(0);

  const handleAnalysisComplete = useCallback(() => {
    setRefreshHistory(prev => prev + 1);
    toast.success("Character analysis completed!");
  }, []);

  return (
    <div className="App min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            <div className="container mx-auto px-4 py-8">
              <div className="text-center mb-8">
                <h1 className="text-6xl font-bold text-white mb-4 font-['Playfair_Display']">
                  VisionForge
                </h1>
                <p className="text-xl text-purple-200 max-w-2xl mx-auto font-['Inter']">
                  Transform your images into rich character lore with AI-powered analysis. 
                  Upload art and instantly generate traits, backstories, and power suggestions.
                </p>
              </div>

              <div className="max-w-6xl mx-auto">
                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                  <TabsList className="grid w-full grid-cols-2 mb-8">
                    <TabsTrigger value="analyzer" className="text-lg py-3">
                      Image Analyzer
                    </TabsTrigger>
                    <TabsTrigger value="history" className="text-lg py-3">
                      Analysis History
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="analyzer" className="space-y-8">
                    <Card className="border-purple-500/20 bg-slate-800/50 backdrop-blur-sm">
                      <CardHeader className="text-center">
                        <CardTitle className="text-3xl font-bold text-white font-['Inter']">
                          Image-to-Lore Analyzer
                        </CardTitle>
                        <CardDescription className="text-purple-200 text-lg">
                          Upload character art to extract traits, mood, backstory seeds, and power suggestions
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <ImageAnalyzer onAnalysisComplete={handleAnalysisComplete} />
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="history" className="space-y-8">
                    <Card className="border-purple-500/20 bg-slate-800/50 backdrop-blur-sm">
                      <CardHeader className="text-center">
                        <CardTitle className="text-3xl font-bold text-white font-['Inter']">
                          Character Analysis History
                        </CardTitle>
                        <CardDescription className="text-purple-200 text-lg">
                          View and manage your previous character analyses
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <AnalysisHistory key={refreshHistory} />
                      </CardContent>
                    </Card>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          } />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;