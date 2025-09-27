import React, { useState, useCallback } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Textarea } from "./ui/textarea";
import { Progress } from "./ui/progress";
import { Separator } from "./ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { toast } from "sonner";
import { Upload, ImageIcon, Sparkles, Zap, Eye, Plus, ArrowRight } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const GENRES = {
  "dc_comics": "DC Comics",
  "marvel_comics": "Marvel Comics", 
  "anime_manga": "Anime/Manga",
  "manhwa": "Manhwa",
  "image_comics": "Image Comics",
  "milestone": "Milestone Comics",
  "wildstorm": "Wildstorm",
  "urban_realistic": "Urban Realistic"
};

const ImageAnalyzer = ({ onAnalysisComplete, onCharacterCreated }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedGenre, setSelectedGenre] = useState("urban_realistic");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [currentCharacter, setCurrentCharacter] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleFileSelect = useCallback((event) => {
    const file = event.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        toast.error("Please select an image file");
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) {
        toast.error("File size must be less than 10MB");
        return;
      }

      setSelectedFile(file);
      setAnalysis(null);
      setCurrentCharacter(null);
      
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      
      toast.success("Image selected successfully");
    }
  }, []);

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      const fakeEvent = { target: { files: [file] } };
      handleFileSelect(fakeEvent);
    }
  }, [handleFileSelect]);

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
  }, []);

  const analyzeImage = async () => {
    if (!selectedFile) {
      toast.error("Please select an image first");
      return;
    }

    setAnalyzing(true);
    setUploadProgress(0);
    setAnalysis(null);
    setCurrentCharacter(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (selectedGenre) {
        formData.append('genre', selectedGenre);
      }

      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      const response = await axios.post(`${API}/analyze-image`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,
        params: selectedGenre ? { genre: selectedGenre } : {}
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.data.success) {
        setAnalysis(response.data);
        setCurrentCharacter(response.data.character);
        onAnalysisComplete?.();
        onCharacterCreated?.(response.data.character);
        toast.success("Character analysis completed!");
      } else {
        throw new Error(response.data.message || "Analysis failed");
      }
    } catch (error) {
      console.error("Analysis error:", error);
      toast.error(
        error.response?.data?.detail || 
        error.message || 
        "Failed to analyze image. Please try again."
      );
    } finally {
      setAnalyzing(false);
      setUploadProgress(0);
    }
  };

  const enhanceCharacter = async (enhancementType) => {
    if (!currentCharacter) return;
    
    try {
      const response = await axios.post(`${API}/enhance-character`, {
        character_id: currentCharacter.id,
        enhancement_type: enhancementType
      });
      
      if (response.data.success) {
        toast.success(`Character ${enhancementType.replace('_', ' ')} added!`);
        // Refresh character data
        const updatedChar = await axios.get(`${API}/character/${currentCharacter.id}`);
        setCurrentCharacter(updatedChar.data);
      }
    } catch (error) {
      toast.error(`Failed to enhance character: ${error.message}`);
    }
  };

  const resetAnalysis = () => {
    setSelectedFile(null);
    setAnalysis(null);
    setCurrentCharacter(null);
    setPreviewUrl(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return "bg-green-500/20 text-green-300 border-green-500/30";
    if (confidence >= 0.6) return "bg-yellow-500/20 text-yellow-300 border-yellow-500/30";
    return "bg-red-500/20 text-red-300 border-red-500/30";
  };

  const getCostLevelColor = (level) => {
    if (level <= 3) return "bg-blue-500/20 text-blue-300 border-blue-500/30";
    if (level <= 6) return "bg-yellow-500/20 text-yellow-300 border-yellow-500/30";
    return "bg-red-500/20 text-red-300 border-red-500/30";
  };

  return (
    <div className="space-y-6">
      {/* File Upload Section */}
      <Card className="visionforge-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Upload className="w-5 h-5 text-indigo-400" />
            Upload Character Image
          </CardTitle>
          <CardDescription className="text-indigo-200">
            Upload artwork and select genre/universe for tailored analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Genre Selection */}
          <div>
            <label className="block text-sm font-medium text-indigo-300 mb-2">
              Genre/Universe
            </label>
            <Select value={selectedGenre} onValueChange={setSelectedGenre}>
              <SelectTrigger className="bg-slate-800 border-indigo-500/30 text-white">
                <SelectValue placeholder="Select genre/universe" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-indigo-500/30">
                {Object.entries(GENRES).map(([key, name]) => (
                  <SelectItem key={key} value={key} className="text-white hover:bg-slate-700">
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-slate-400 mt-1">
              Powers and backstory will be adapted to fit the selected universe
            </p>
          </div>

          {/* Upload Area */}
          <div 
            className="file-upload-area"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            data-testid="image-upload-area"
          >
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
              id="image-upload"
              data-testid="image-upload-input"
            />
            <label htmlFor="image-upload" className="cursor-pointer block">
              <div className="flex flex-col items-center space-y-4">
                <ImageIcon className="w-16 h-16 text-indigo-400" />
                <div className="text-center">
                  <p className="text-xl font-semibold text-white mb-2">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-sm text-indigo-200">
                    PNG, JPG, JPEG, WebP up to 10MB
                  </p>
                </div>
              </div>
            </label>
          </div>

          {previewUrl && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-white">Selected Image:</p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={resetAnalysis}
                  className="text-red-400 border-red-500/50 hover:bg-red-500/10"
                  data-testid="reset-image-button"
                >
                  Remove
                </Button>
              </div>
              <div className="relative max-w-md mx-auto">
                <img 
                  src={previewUrl} 
                  alt="Preview" 
                  className="w-full h-auto max-h-64 object-contain rounded-lg border-2 border-indigo-500/30"
                  data-testid="image-preview"
                />
              </div>
            </div>
          )}

          {analyzing && (
            <div className="mt-6 space-y-3">
              <div className="flex items-center gap-2 text-indigo-300">
                <Sparkles className="w-4 h-4 animate-spin" />
                <span className="text-sm font-medium">
                  Analyzing for {GENRES[selectedGenre]} universe...
                </span>
              </div>
              <Progress value={uploadProgress} className="w-full" />
            </div>
          )}

          <div className="mt-6">
            <Button
              onClick={analyzeImage}
              disabled={!selectedFile || analyzing}
              className="w-full btn-primary"
              size="lg"
              data-testid="analyze-button"
            >
              {analyzing ? (
                <>
                  <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Eye className="w-4 h-4 mr-2" />
                  Analyze for {GENRES[selectedGenre]}
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysis && currentCharacter && (
        <Card className="visionforge-card fade-in" data-testid="analysis-results">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-white">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                Character Profile Created
              </CardTitle>
              <Badge className="bg-indigo-500/20 text-indigo-300 border-indigo-500/30">
                {GENRES[selectedGenre]}
              </Badge>
            </div>
            <CardDescription className="text-indigo-200">
              AI-generated character analysis adapted for {GENRES[selectedGenre]} universe
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Enhancement Tools Integration */}
            <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 rounded-lg p-4 border border-green-500/30">
              <h3 className="text-lg font-semibold text-green-300 mb-3 flex items-center gap-2">
                <Plus className="w-5 h-5" />
                Enhance with VisionForge Tools
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <Button
                  variant="outline"
                  onClick={() => enhanceCharacter("expand_backstory")}
                  className="border-green-500/50 text-green-300 hover:bg-green-500/10"
                  data-testid="enhance-backstory"
                >
                  <ArrowRight className="w-4 h-4 mr-2" />
                  Expand Backstory
                </Button>
                <Button
                  variant="outline"
                  onClick={() => enhanceCharacter("add_dialogue")}
                  className="border-blue-500/50 text-blue-300 hover:bg-blue-500/10"
                  data-testid="enhance-dialogue"
                >
                  <ArrowRight className="w-4 h-4 mr-2" />
                  Add Dialogue
                </Button>
                <Button
                  variant="outline"
                  onClick={() => enhanceCharacter("trope_analysis")}
                  className="border-purple-500/50 text-purple-300 hover:bg-purple-500/10"
                  data-testid="enhance-tropes"
                >
                  <ArrowRight className="w-4 h-4 mr-2" />
                  Analyze Tropes
                </Button>
              </div>
              <p className="text-sm text-slate-400 mt-2">
                Use other VisionForge tools to refine and develop this character further
              </p>
            </div>

            {/* Character Summary */}
            <div className="analysis-summary">
              <h3 className="text-lg font-semibold text-indigo-300 mb-3">Character Summary</h3>
              <p className="text-indigo-100 leading-relaxed" data-testid="persona-summary">
                {currentCharacter.persona_summary}
              </p>
              {currentCharacter.genre_context && (
                <p className="text-sm text-indigo-300 mt-3 italic">
                  <strong>Universe Context:</strong> {currentCharacter.genre_context}
                </p>
              )}
            </div>

            {/* Mood */}
            <div>
              <h3 className="text-lg font-semibold text-indigo-300 mb-3">Mood & Atmosphere</h3>
              <Badge 
                className="bg-indigo-500/20 text-indigo-300 border-indigo-500/30 px-4 py-2 text-base"
                data-testid="character-mood"
              >
                {currentCharacter.mood}
              </Badge>
            </div>

            <Separator className="bg-indigo-500/30" />

            {/* Character Traits */}
            <div>
              <h3 className="text-lg font-semibold text-indigo-300 mb-4">Character Traits</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {currentCharacter.traits.map((trait, index) => (
                  <div 
                    key={index} 
                    className="bg-slate-700/50 rounded-lg p-4 space-y-2"
                    data-testid={`trait-${index}`}
                  >
                    <div className="flex items-center justify-between">
                      <Badge variant="outline" className="text-indigo-300 border-indigo-500/50">
                        {trait.category}
                      </Badge>
                      <Badge className={getConfidenceColor(trait.confidence)}>
                        {Math.round(trait.confidence * 100)}% confident
                      </Badge>
                    </div>
                    <p className="text-slate-200">{trait.trait}</p>
                  </div>
                ))}
              </div>
            </div>

            <Separator className="bg-indigo-500/30" />

            {/* Backstory Seeds */}
            <div>
              <h3 className="text-lg font-semibold text-indigo-300 mb-4">Backstory Seeds</h3>
              <div className="grid grid-cols-1 gap-3">
                {currentCharacter.backstory_seeds.map((seed, index) => (
                  <div 
                    key={index}
                    className="backstory-seed"
                    data-testid={`backstory-seed-${index}`}
                  >
                    <p>{seed}</p>
                  </div>
                ))}
              </div>
            </div>

            <Separator className="bg-indigo-500/30" />

            {/* Power Suggestions */}
            <div>
              <h3 className="text-lg font-semibold text-indigo-300 mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5" />
                {GENRES[selectedGenre]} Power Suggestions
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {currentCharacter.power_suggestions.map((power, index) => (
                  <div 
                    key={index}
                    className="power-card"
                    data-testid={`power-suggestion-${index}`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-semibold text-white">{power.name}</h4>
                      <Badge className={getCostLevelColor(power.cost_level)}>
                        Cost: {power.cost_level}/10
                      </Badge>
                    </div>
                    <p className="text-slate-300 text-sm mb-3">{power.description}</p>
                    {power.universe_context && (
                      <p className="text-xs text-indigo-300 mb-2">
                        <strong>Universe Context:</strong> {power.universe_context}
                      </p>
                    )}
                    <div className="bg-red-900/20 rounded px-3 py-2">
                      <p className="text-xs text-red-300">
                        <strong>Limitations:</strong> {power.limitations}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Creation Stages */}
            <div className="bg-slate-700/30 rounded-lg p-4">
              <h4 className="text-sm font-medium text-slate-300 mb-2">Creation Stages Completed</h4>
              <div className="flex flex-wrap gap-2">
                {currentCharacter.creation_stages.map((stage, index) => (
                  <Badge key={index} variant="outline" className="text-slate-400 border-slate-500">
                    {stage.replace('_', ' ')}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ImageAnalyzer;