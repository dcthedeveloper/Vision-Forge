import React, { useState, useCallback } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner";
import ImageAnalyzer from "./components/ImageAnalyzer";
import AnalysisHistory from "./components/AnalysisHistory";
import TextGenerator from "./components/TextGenerator";
import StyleCoach from "./components/StyleCoach";
import TropeBuilder from "./components/TropeBuilder";
import { Button } from "./components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";

function App() {
  const [activeTab, setActiveTab] = useState("image-analyzer");
  const [refreshHistory, setRefreshHistory] = useState(0);

  const handleAnalysisComplete = useCallback(() => {
    setRefreshHistory(prev => prev + 1);
    toast.success("Character analysis completed!");
  }, []);

  return (
    <div className="App min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            <div className="container mx-auto px-4 py-8">
              <div className="text-center mb-8">
                <h1 className="text-6xl font-bold text-white mb-4 font-['Playfair_Display']">
                  VisionForge
                </h1>
                <p className="text-xl text-indigo-200 max-w-3xl mx-auto font-['Inter']">
                  The ultimate character creation and storytelling platform. Transform images into rich lore, 
                  generate compelling narratives, and craft authentic characters with AI-powered tools.
                </p>
              </div>

              <div className="max-w-7xl mx-auto">
                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                  <TabsList className="grid w-full grid-cols-7 mb-8">
                    <TabsTrigger value="image-analyzer" className="text-sm py-3">
                      Image Analyzer
                    </TabsTrigger>
                    <TabsTrigger value="text-generator" className="text-sm py-3">
                      Text Generator
                    </TabsTrigger>
                    <TabsTrigger value="style-coach" className="text-sm py-3">
                      Style Coach
                    </TabsTrigger>
                    <TabsTrigger value="trope-builder" className="text-sm py-3">
                      Trope Builder
                    </TabsTrigger>
                    <TabsTrigger value="beat-sheet" className="text-sm py-3">
                      Beat Sheets
                    </TabsTrigger>
                    <TabsTrigger value="trope-meter" className="text-sm py-3">
                      Trope Meter
                    </TabsTrigger>
                    <TabsTrigger value="history" className="text-sm py-3">
                      History
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="image-analyzer" className="space-y-8">
                    <Card className="border-indigo-500/20 bg-slate-800/50 backdrop-blur-sm">
                      <CardHeader className="text-center">
                        <CardTitle className="text-3xl font-bold text-white font-['Inter']">
                          Image-to-Lore Analyzer
                        </CardTitle>
                        <CardDescription className="text-indigo-200 text-lg">
                          Upload character art to extract traits, mood, backstory seeds, and power suggestions
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <ImageAnalyzer onAnalysisComplete={handleAnalysisComplete} />
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="text-generator" className="space-y-8">
                    <Card className="border-indigo-500/20 bg-slate-800/50 backdrop-blur-sm">
                      <CardHeader className="text-center">
                        <CardTitle className="text-3xl font-bold text-white font-['Inter']">
                          AI Text Generator
                        </CardTitle>
                        <CardDescription className="text-indigo-200 text-lg">
                          Create characters, stories, backstories, and dialogue with Claude Sonnet 4
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <TextGenerator />
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="style-coach" className="space-y-8">
                    <Card className="border-indigo-500/20 bg-slate-800/50 backdrop-blur-sm">
                      <CardHeader className="text-center">
                        <CardTitle className="text-3xl font-bold text-white font-['Inter']">
                          Style Coach
                        </CardTitle>
                        <CardDescription className="text-indigo-200 text-lg">
                          Analyze and improve your writing by detecting clichés and style issues
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <StyleCoach />
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="trope-builder" className="space-y-8">
                    <Card className="border-indigo-500/20 bg-slate-800/50 backdrop-blur-sm">
                      <CardHeader className="text-center">
                        <CardTitle className="text-3xl font-bold text-white font-['Inter']">
                          Trope & Archetype Builder
                        </CardTitle>
                        <CardDescription className="text-indigo-200 text-lg">
                          Mix archetypes, build powers, and create unique character concepts
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <TropeBuilder />
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="beat-sheet" className="space-y-8">
                    <Card className="border-indigo-500/20 bg-slate-800/50 backdrop-blur-sm">
                      <CardHeader className="text-center">
                        <CardTitle className="text-3xl font-bold text-white font-['Inter']">
                          Beat Sheet Generator
                        </CardTitle>
                        <CardDescription className="text-indigo-200 text-lg">
                          Generate narrative beat sheets adapted to your characters with Ollama AI
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <BeatSheetGenerator />
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="trope-meter" className="space-y-8">
                    <Card className="border-indigo-500/20 bg-slate-800/50 backdrop-blur-sm">
                      <CardHeader className="text-center">
                        <CardTitle className="text-3xl font-bold text-white font-['Inter']">
                          Enhanced Trope Risk Meter
                        </CardTitle>
                        <CardDescription className="text-indigo-200 text-lg">
                          Analyze characters for cliché risks and get AI-powered suggestions for improvement
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <TropeRiskMeter />
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="history" className="space-y-8">
                    <Card className="border-indigo-500/20 bg-slate-800/50 backdrop-blur-sm">
                      <CardHeader className="text-center">
                        <CardTitle className="text-3xl font-bold text-white font-['Inter']">
                          Analysis History
                        </CardTitle>
                        <CardDescription className="text-indigo-200 text-lg">
                          View and manage your previous analyses and creations
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