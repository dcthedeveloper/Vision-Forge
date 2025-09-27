import React, { useState } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Textarea } from "./ui/textarea";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { Progress } from "./ui/progress";
import { toast } from "sonner";
import { 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  BookOpen,
  Lightbulb,
  RefreshCw,
  Copy,
  Eye
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const StyleCoach = () => {
  const [inputText, setInputText] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const exampleTexts = [
    {
      title: "Fantasy Description",
      text: `The ancient castle nestled atop the misty mountain, its dark towers reaching toward the stormy sky. Sir Galahad delved deep into the mysterious chambers, his heart heavy with the weight of destiny. The enigmatic sorceress had warned him of the trials ahead, but he pressed onward with meticulous care, knowing that the tapestry of fate was being woven around him.`
    },
    {
      title: "Sci-Fi Narrative", 
      text: `Captain Sarah Martinez was a seasoned space pilot who had seen more than her share of alien encounters. The ship's AI delved into the navigation systems while she carefully examined the star charts. Her dark past haunted her thoughts as the mysterious signal beckoned from the void.`
    },
    {
      title: "Modern Dialogue",
      text: `"Listen, I know this sounds crazy, but hear me out," Jake said, running his hand through his hair nervously. "That thing we saw last night... it wasn't human." Sarah raised an eyebrow, her coffee growing cold as she processed his words.`
    }
  ];

  const handleAnalyze = async () => {
    if (!inputText.trim()) {
      toast.error("Please enter some text to analyze");
      return;
    }

    setIsAnalyzing(true);
    setAnalysis(null);

    try {
      const response = await axios.post(`${API}/analyze-style`, {
        text: inputText.trim()
      });

      if (response.data.success) {
        setAnalysis(response.data);
        toast.success("Style analysis completed!");
      } else {
        throw new Error(response.data.message || "Analysis failed");
      }
    } catch (error) {
      console.error("Analysis error:", error);
      toast.error(
        error.response?.data?.detail || 
        error.message || 
        "Failed to analyze text. Please try again."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUseExample = (exampleText) => {
    setInputText(exampleText);
    setAnalysis(null);
  };

  const handleCopyRewritten = () => {
    if (analysis?.rewritten_text) {
      navigator.clipboard.writeText(analysis.rewritten_text);
      toast.success("Rewritten text copied to clipboard!");
    }
  };

  const getClicheColor = (score) => {
    if (score < 0.3) return "text-green-400";
    if (score < 0.6) return "text-yellow-400";  
    return "text-red-400";
  };

  const getClicheLabel = (score) => {
    if (score < 0.3) return "Fresh & Original";
    if (score < 0.6) return "Some Clichés Detected";
    return "Heavy Cliché Usage";
  };

  const getIssueIcon = (type) => {
    switch (type) {
      case "cliche":
        return <XCircle className="w-4 h-4 text-red-400" />;
      case "overused_word":
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case "passive_voice":
        return <AlertTriangle className="w-4 h-4 text-orange-400" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-blue-400" />;
    }
  };

  const getIssueColor = (type) => {
    switch (type) {
      case "cliche":
        return "bg-red-500/20 text-red-300 border-red-500/30";
      case "overused_word":
        return "bg-yellow-500/20 text-yellow-300 border-yellow-500/30";
      case "passive_voice":
        return "bg-orange-500/20 text-orange-300 border-orange-500/30";
      default:
        return "bg-blue-500/20 text-blue-300 border-blue-500/30";
    }
  };

  return (
    <div className="space-y-6">
      {/* Text Input Section */}
      <Card className="visionforge-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Eye className="w-5 h-5 text-indigo-400" />
            Style Analysis
          </CardTitle>
          <CardDescription className="text-indigo-200">
            Paste your text below to analyze for clichés, overused words, and style issues
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Text Input */}
          <div>
            <label className="block text-sm font-medium text-indigo-300 mb-2">
              Text to Analyze
            </label>
            <Textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste your text here for style analysis..."
              className="text-editor min-h-40 resize-vertical"
              data-testid="style-input"
            />
            <div className="flex justify-between items-center mt-2">
              <span className="text-xs text-slate-400">
                {inputText.length} characters
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setInputText("")}
                disabled={!inputText}
                className="text-xs border-slate-600 text-slate-400 hover:bg-slate-700/50"
              >
                Clear
              </Button>
            </div>
          </div>

          {/* Example Texts */}
          <div>
            <label className="block text-sm font-medium text-indigo-300 mb-3">
              Try These Examples
            </label>
            <div className="grid grid-cols-1 gap-3">
              {exampleTexts.map((example, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="text-left justify-start h-auto p-4 border-slate-600 hover:bg-slate-700/50"
                  onClick={() => handleUseExample(example.text)}
                  data-testid={`example-${index}`}
                >
                  <div className="space-y-1">
                    <div className="font-medium text-indigo-300 text-sm">
                      {example.title}
                    </div>
                    <div className="text-xs text-slate-400 line-clamp-2">
                      {example.text.substring(0, 120)}...
                    </div>
                  </div>
                </Button>
              ))}
            </div>
          </div>

          {/* Analyze Button */}
          <Button
            onClick={handleAnalyze}
            disabled={!inputText.trim() || isAnalyzing}
            className="w-full btn-primary"
            size="lg"
            data-testid="analyze-style-button"
          >
            {isAnalyzing ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Analyzing Style...
              </>
            ) : (
              <>
                <Eye className="w-4 h-4 mr-2" />
                Analyze Writing Style
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6 fade-in">
          {/* Cliché Score Overview */}
          <Card className="visionforge-card" data-testid="style-analysis-results">
            <CardHeader>
              <CardTitle className="flex items-center justify-between text-white">
                <div className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-indigo-400" />
                  Style Analysis Results
                </div>
                <Badge 
                  className={`${getClicheColor(analysis.cliche_score)} bg-slate-800 border-slate-600`}
                  data-testid="overall-cliche-score"
                >
                  {getClicheLabel(analysis.cliche_score)}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-slate-300">Cliché Score</span>
                <span className={`font-semibold ${getClicheColor(analysis.cliche_score)}`}>
                  {Math.round(analysis.cliche_score * 100)}%
                </span>
              </div>
              <Progress 
                value={analysis.cliche_score * 100} 
                className="w-full"
              />
              <p className="text-sm text-slate-400">
                Lower scores indicate more original, fresh writing
              </p>
            </CardContent>
          </Card>

          {/* Style Issues */}
          {analysis.issues && analysis.issues.length > 0 && (
            <Card className="visionforge-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <AlertTriangle className="w-5 h-5 text-yellow-400" />
                  Style Issues Found ({analysis.issues.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysis.issues.map((issue, index) => (
                    <div 
                      key={index}
                      className="bg-slate-700/30 rounded-lg p-4 border border-slate-600/50"
                      data-testid={`style-issue-${index}`}
                    >
                      <div className="flex items-start gap-3">
                        {getIssueIcon(issue.type)}
                        <div className="flex-1 space-y-2">
                          <div className="flex items-center gap-2">
                            <Badge className={getIssueColor(issue.type)}>
                              {issue.type.replace('_', ' ').toUpperCase()}
                            </Badge>
                            <span className="text-sm font-medium text-slate-300">
                              "{issue.text}"
                            </span>
                          </div>
                          <p className="text-sm text-slate-400">
                            {issue.suggestion}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* General Suggestions */}
          {analysis.suggestions && analysis.suggestions.length > 0 && (
            <Card className="visionforge-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Lightbulb className="w-5 h-5 text-green-400" />
                  Writing Suggestions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {analysis.suggestions.map((suggestion, index) => (
                    <div 
                      key={index}
                      className="flex items-start gap-2"
                      data-testid={`suggestion-${index}`}
                    >
                      <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-slate-300">{suggestion}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Rewritten Text */}
          {analysis.rewritten_text && analysis.rewritten_text !== "Please resubmit for analysis" && (
            <Card className="visionforge-card">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2 text-white">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    Improved Version
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopyRewritten}
                    className="border-indigo-500/50 text-indigo-300 hover:bg-indigo-500/10"
                    data-testid="copy-rewritten-button"
                  >
                    <Copy className="w-4 h-4 mr-1" />
                    Copy
                  </Button>
                </div>
                <CardDescription className="text-indigo-200">
                  Here's a refined version with improved style and reduced clichés
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-gen-area">
                  <div className="whitespace-pre-wrap text-slate-200 leading-relaxed" data-testid="rewritten-text">
                    {analysis.rewritten_text}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default StyleCoach;