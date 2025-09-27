import React, { useState, useCallback } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Textarea } from "./ui/textarea";
import { Progress } from "./ui/progress";
import { Separator } from "./ui/separator";
import { toast } from "sonner";
import { Upload, ImageIcon, Sparkles, Zap, Eye } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ImageAnalyzer = ({ onAnalysisComplete }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleFileSelect = useCallback((event) => {
    const file = event.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        toast.error("Please select an image file");
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        toast.error("File size must be less than 10MB");
        return;
      }

      setSelectedFile(file);
      setAnalysis(null);
      
      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      
      toast.success("Image selected successfully");
    }
  }, []);

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      // Simulate file input change
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

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await axios.post(`${API}/analyze-image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 second timeout for AI processing
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.data.success) {
        setAnalysis(response.data.analysis);
        onAnalysisComplete?.();
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

  const resetAnalysis = () => {
    setSelectedFile(null);
    setAnalysis(null);
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
            <Upload className="w-5 h-5 text-purple-400" />
            Upload Character Image
          </CardTitle>
          <CardDescription className="text-purple-200">
            Upload artwork, character designs, or reference images for analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
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
                <ImageIcon className="w-16 h-16 text-purple-400" />
                <div className="text-center">
                  <p className="text-xl font-semibold text-white mb-2">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-sm text-purple-200">
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
                  className="w-full h-auto max-h-64 object-contain rounded-lg border-2 border-purple-500/30"
                  data-testid="image-preview"
                />
              </div>
            </div>
          )}

          {analyzing && (
            <div className="mt-6 space-y-3">
              <div className="flex items-center gap-2 text-purple-300">
                <Sparkles className="w-4 h-4 animate-spin" />
                <span className="text-sm font-medium">Analyzing character traits...</span>
              </div>
              <Progress value={uploadProgress} className="w-full" />
            </div>
          )}

          <div className="mt-6 flex gap-3">
            <Button
              onClick={analyzeImage}
              disabled={!selectedFile || analyzing}
              className="flex-1 btn-primary"
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
                  Analyze Character
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysis && (
        <Card className="visionforge-card fade-in" data-testid="analysis-results">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Sparkles className="w-5 h-5 text-purple-400" />
              Character Analysis Results
            </CardTitle>
            <CardDescription className="text-purple-200">
              AI-generated character traits, backstory, and power suggestions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Persona Summary */}
            <div className="analysis-summary">
              <h3 className="text-lg font-semibold text-purple-300 mb-3">Character Summary</h3>
              <p className="text-purple-100 leading-relaxed" data-testid="persona-summary">
                {analysis.persona_summary}
              </p>
            </div>

            {/* Mood */}
            <div>
              <h3 className="text-lg font-semibold text-purple-300 mb-3">Mood & Atmosphere</h3>
              <Badge 
                className="bg-purple-500/20 text-purple-300 border-purple-500/30 px-4 py-2 text-base"
                data-testid="character-mood"
              >
                {analysis.mood}
              </Badge>
            </div>

            <Separator className="bg-purple-500/30" />

            {/* Character Traits */}
            <div>
              <h3 className="text-lg font-semibold text-purple-300 mb-4">Character Traits</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysis.traits.map((trait, index) => (
                  <div 
                    key={index} 
                    className="bg-slate-700/50 rounded-lg p-4 space-y-2"
                    data-testid={`trait-${index}`}
                  >
                    <div className="flex items-center justify-between">
                      <Badge variant="outline" className="text-purple-300 border-purple-500/50">
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

            <Separator className="bg-purple-500/30" />

            {/* Backstory Seeds */}
            <div>
              <h3 className="text-lg font-semibold text-purple-300 mb-4">Backstory Seeds</h3>
              <div className="grid grid-cols-1 gap-3">
                {analysis.backstory_seeds.map((seed, index) => (
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

            <Separator className="bg-purple-500/30" />

            {/* Power Suggestions */}
            <div>
              <h3 className="text-lg font-semibold text-purple-300 mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Power Suggestions
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysis.power_suggestions.map((power, index) => (
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
                    <div className="bg-red-900/20 rounded px-3 py-2">
                      <p className="text-xs text-red-300">
                        <strong>Limitations:</strong> {power.limitations}
                      </p>
                    </div>
                  </div>
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