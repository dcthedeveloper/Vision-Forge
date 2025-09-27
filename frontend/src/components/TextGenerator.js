import React, { useState } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Textarea } from "./ui/textarea";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { toast } from "sonner";
import { 
  PenTool, 
  User, 
  BookOpen, 
  MessageCircle, 
  Sparkles, 
  AlertTriangle,
  Copy,
  RefreshCw
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TextGenerator = () => {
  const [generationType, setGenerationType] = useState("character");
  const [prompt, setPrompt] = useState("");
  const [generatedText, setGeneratedText] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [clicheScore, setClicheScore] = useState(null);
  const [suggestions, setSuggestions] = useState([]);

  const generationTypes = {
    character: {
      icon: User,
      title: "Character Creator",
      description: "Generate detailed character profiles with unique traits and backgrounds",
      placeholder: "Describe the character you want to create (e.g., 'A cyberpunk hacker with a secret past')",
      examples: [
        "A street-smart detective with unusual investigative methods",
        "An AI researcher who discovered something that changed everything",
        "A chef who uses cooking to solve supernatural mysteries"
      ]
    },
    story: {
      icon: BookOpen,
      title: "Story Architect",
      description: "Create compelling narratives and plot outlines",
      placeholder: "Describe your story idea (e.g., 'A heist story set in a floating city')",
      examples: [
        "Two rivals must work together when their city faces an unknown threat",
        "A memory thief discovers they've stolen their own forgotten past",
        "The last bookstore in the world becomes a refuge during an apocalypse"
      ]
    },
    backstory: {
      icon: PenTool,
      title: "Lore Master",
      description: "Develop rich character histories and world-building details",
      placeholder: "What backstory elements do you want to explore?",
      examples: [
        "How a brilliant scientist became a feared villain",
        "The hidden history of an ancient organization",
        "Why a hero gave up their powers and disappeared"
      ]
    },
    dialogue: {
      icon: MessageCircle,
      title: "Dialogue Specialist",
      description: "Write authentic conversations and character interactions",
      placeholder: "Describe the conversation scene you want to create",
      examples: [
        "A tense negotiation between former allies",
        "An awkward first meeting between two very different characters",
        "A mentor revealing a difficult truth to their student"
      ]
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error("Please enter a prompt first");
      return;
    }

    setIsGenerating(true);
    setGeneratedText("");
    setClicheScore(null);
    setSuggestions([]);

    try {
      const response = await axios.post(`${API}/generate-text`, {
        prompt: prompt.trim(),
        generation_type: generationType,
        style_preferences: {
          avoid_cliches: true,
          tone: "engaging",
          detail_level: "high"
        }
      });

      if (response.data.success) {
        setGeneratedText(response.data.generated_text);
        setClicheScore(response.data.cliche_score);
        setSuggestions(response.data.suggestions || []);
        toast.success("Text generated successfully!");
      } else {
        throw new Error(response.data.message || "Generation failed");
      }
    } catch (error) {
      console.error("Generation error:", error);
      toast.error(
        error.response?.data?.detail || 
        error.message || 
        "Failed to generate text. Please try again."
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedText);
    toast.success("Text copied to clipboard!");
  };

  const handleUseExample = (example) => {
    setPrompt(example);
  };

  const getClicheColor = (score) => {
    if (score < 0.3) return "text-green-400";
    if (score < 0.6) return "text-yellow-400";
    return "text-red-400";
  };

  const getClicheLabel = (score) => {
    if (score < 0.3) return "Fresh";
    if (score < 0.6) return "Some clichés";
    return "Very clichéd";
  };

  const currentType = generationTypes[generationType];
  const IconComponent = currentType.icon;

  return (
    <div className="space-y-6">
      {/* Generation Type Selector */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {Object.entries(generationTypes).map(([type, config]) => {
          const TypeIcon = config.icon;
          const isActive = generationType === type;
          
          return (
            <Button
              key={type}
              variant="outline"
              className={`h-auto p-4 flex flex-col items-center space-y-2 transition-all duration-200 ${
                isActive 
                  ? 'gen-type-active border-indigo-400 bg-indigo-500/20' 
                  : 'gen-type-inactive'
              }`}
              onClick={() => setGenerationType(type)}
              data-testid={`generation-type-${type}`}
            >
              <TypeIcon className="w-6 h-6" />
              <span className="text-sm font-medium capitalize">{type}</span>
            </Button>
          );
        })}
      </div>

      {/* Main Generation Interface */}
      <Card className="visionforge-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-white">
            <IconComponent className="w-6 h-6 text-indigo-400" />
            {currentType.title}
          </CardTitle>
          <CardDescription className="text-indigo-200">
            {currentType.description}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Prompt Input */}
          <div>
            <label className="block text-sm font-medium text-indigo-300 mb-2">
              Your Prompt
            </label>
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder={currentType.placeholder}
              className="text-editor min-h-24 resize-none"
              data-testid="generation-prompt"
            />
          </div>

          {/* Example Prompts */}
          <div>
            <label className="block text-sm font-medium text-indigo-300 mb-3">
              Example Prompts
            </label>
            <div className="grid grid-cols-1 gap-2">
              {currentType.examples.map((example, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="text-left justify-start h-auto p-3 text-slate-300 border-slate-600 hover:bg-slate-700/50"
                  onClick={() => handleUseExample(example)}
                  data-testid={`example-prompt-${index}`}
                >
                  "{example}"
                </Button>
              ))}
            </div>
          </div>

          {/* Generate Button */}
          <Button
            onClick={handleGenerate}
            disabled={!prompt.trim() || isGenerating}
            className="w-full btn-primary"
            size="lg"
            data-testid="generate-button"
          >
            {isGenerating ? (
              <>
                <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <IconComponent className="w-4 h-4 mr-2" />
                Generate {currentType.title.split(' ')[0]}
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Generated Content */}
      {generatedText && (
        <Card className="visionforge-card fade-in" data-testid="generated-content">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-white">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                Generated {currentType.title.split(' ')[0]}
              </CardTitle>
              <div className="flex items-center gap-3">
                {clicheScore !== null && (
                  <Badge 
                    className={`${getClicheColor(clicheScore)} bg-slate-800 border-slate-600`}
                    data-testid="cliche-score"
                  >
                    {getClicheLabel(clicheScore)}
                  </Badge>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopy}
                  className="border-indigo-500/50 text-indigo-300 hover:bg-indigo-500/10"
                  data-testid="copy-button"
                >
                  <Copy className="w-4 h-4 mr-1" />
                  Copy
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Generated Text */}
            <div className="text-gen-area">
              <div className="whitespace-pre-wrap text-slate-200 leading-relaxed" data-testid="generated-text">
                {generatedText}
              </div>
            </div>

            {/* Cliché Analysis */}
            {clicheScore !== null && clicheScore > 0.3 && (
              <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-400" />
                  <span className="text-sm font-medium text-yellow-300">
                    Style Notes
                  </span>
                </div>
                <p className="text-sm text-yellow-200">
                  This text contains some common phrases or tropes. Consider using the Style Coach 
                  to refine and improve the writing quality.
                </p>
              </div>
            )}

            {/* Suggestions */}
            {suggestions.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-indigo-300 mb-2">Suggestions</h4>
                <div className="space-y-2">
                  {suggestions.map((suggestion, index) => (
                    <div 
                      key={index}
                      className="style-suggestion"
                      data-testid={`suggestion-${index}`}
                    >
                      {suggestion}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <Separator className="bg-indigo-500/20" />

            {/* Action Buttons */}
            <div className="flex gap-3">
              <Button
                variant="outline"
                className="border-indigo-500/50 text-indigo-300 hover:bg-indigo-500/10"
                onClick={() => setGenerationType("dialogue")}
                disabled={generationType === "dialogue"}
              >
                <MessageCircle className="w-4 h-4 mr-2" />
                Add Dialogue
              </Button>
              <Button
                variant="outline"
                className="border-indigo-500/50 text-indigo-300 hover:bg-indigo-500/10"
                onClick={() => setGenerationType("backstory")}
                disabled={generationType === "backstory"}
              >
                <PenTool className="w-4 h-4 mr-2" />
                Expand Backstory
              </Button>
              <Button
                variant="outline"
                className="border-indigo-500/50 text-indigo-300 hover:bg-indigo-500/10"
                onClick={handleGenerate}
                disabled={isGenerating}
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Generate Variation
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default TextGenerator;