import React, { useState, useCallback } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Textarea } from "./ui/textarea";
import { Progress } from "./ui/progress";
import { Separator } from "./ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Checkbox } from "./ui/checkbox";
import { toast } from "sonner";
import { Upload, ImageIcon, Sparkles, Zap, Eye, Plus, ArrowRight, Settings, Shield } from "lucide-react";
import ContinuityLinter from "./ContinuityLinter";

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

const CHARACTER_ORIGINS = {
  "human": { name: "Human", description: "Baseline human with no supernatural abilities" },
  "metahuman": { name: "Metahuman", description: "Human with acquired supernatural abilities" },
  "mutant": { name: "Mutant", description: "Born with genetic mutations granting powers" },
  "alien": { name: "Alien", description: "Extraterrestrial being with natural abilities" },
  "inhuman": { name: "Inhuman", description: "Genetically modified human subspecies" },
  "super_soldier": { name: "Super Soldier", description: "Enhanced through military experiments" },
  "tech_based": { name: "Tech-Based", description: "Powers derived from advanced technology" },
  "genetically_modified": { name: "Genetically Modified", description: "Artificially altered genetics" },
  "magic_user": { name: "Magic User", description: "Powers from mystical/supernatural sources" },
  "cosmic_entity": { name: "Cosmic Entity", description: "Being of cosmic or divine nature" },
  "android": { name: "Android/Cyborg", description: "Artificial being or human-machine hybrid" },
  "enhanced_human": { name: "Enhanced Human", description: "Human with augmented abilities" },
  "nootropic_enhanced": { name: "Nootropic Enhanced", description: "Enhanced through experimental cognitive drugs" },
  "biotech_subject": { name: "Biotech Subject", description: "Modified through cutting-edge biotechnology" },
  "self_optimized": { name: "Self-Optimized", description: "Achieved enhancement through systematic self-improvement" }
};

const SOCIAL_STATUS = {
  "wealthy": "Wealthy Elite",
  "middle_class": "Middle Class", 
  "working_class": "Working Class",
  "street_level": "Street Level",
  "royalty": "Royalty/Nobility",
  "corporate": "Corporate Executive",
  "military": "Military/Government",
  "criminal": "Criminal Underworld",
  "academic": "Academic/Scientist",
  "celebrity": "Public Figure/Celebrity",
  "entrepreneurial": "Self-Made Entrepreneur",
  "old_money": "Generational Wealth",
  "nouveau_riche": "New Money/Tech Wealth",
  "underground_elite": "Shadow Power Broker"
};

const POWER_SOURCES = {
  "innate": "Born with Powers",
  "accident": "Freak Accident", 
  "experiment": "Scientific Experiment",
  "training": "Intensive Training",
  "technology": "Advanced Technology",
  "magic": "Mystical/Magical",
  "cosmic": "Cosmic Event",
  "divine": "Divine/Religious",
  "alien_tech": "Alien Technology",
  "mutation": "Genetic Mutation",
  "nootropic_drug": "Experimental Nootropic (NZT-48 style)",
  "meta_drug": "Meta-Enhancement Drug",
  "biotech_implant": "Biotech Implantation",
  "neural_enhancement": "Neural Network Optimization",
  "self_evolution": "Conscious Self-Evolution",
  "symbiotic_merger": "Symbiotic Entity Merger",
  "dimensional_exposure": "Dimensional Energy Exposure",
  // OP Mode exclusive sources
  "reality_breach": "🔥 Reality Breach Event",
  "omnipotent_artifact": "🔥 Omnipotent Artifact Fusion",
  "conceptual_embodiment": "🔥 Conceptual Force Embodiment",
  "narrative_transcendence": "🔥 Story-Breaking Transcendence"
};

const OP_CHARACTER_ORIGINS = {
  "narrative_breaker": { name: "🔥 Narrative Breaker", description: "Character so powerful they break story logic" },
  "meta_aware": { name: "🔥 Meta-Aware Entity", description: "Knows they're in a story and exploits it" },
  "power_creep": { name: "🔥 Power Creep Incarnate", description: "Constantly escalating beyond all limits" },
  "deus_ex_machina": { name: "🔥 Deus Ex Machina", description: "Appears to solve impossible problems" },
  "reality_warper": { name: "🔥 Reality Warper", description: "Reshapes existence on a whim" },
  "omnipotent_being": { name: "🔥 Omnipotent Entity", description: "Unlimited power in all aspects" }
};

const OP_ARCHETYPE_TAGS = [
  "🔥 Story Breaker", "🔥 Power Scaling Destroyer", "🔥 Invincibility Incarnate",
  "🔥 Plot Armor Personified", "🔥 Balance Wrecker", "🔥 Meta Gaming God",
  "🔥 Narrative Cancer", "🔥 Escalation Engine", "🔥 Impossibility Made Real"
];

const POWER_EVOLUTION_STAGES = {
  "initial": "Initial Enhancement",
  "adaptive": "Adaptive Development", 
  "synergistic": "Mind-Body Synergy",
  "transcendent": "Transcendent State",
  "systemic": "System-Level Mastery"
};

const GEOGRAPHIC_CONTEXTS = {
  "detroit": "Detroit - Industrial Rebirth",
  "chicago": "Chicago - Urban Power Dynamics", 
  "new_york": "New York - Financial Hub",
  "los_angeles": "Los Angeles - Entertainment Complex",
  "miami": "Miami - International Gateway",
  "atlanta": "Atlanta - Southern Power Center",
  "seattle": "Seattle - Tech Innovation Hub",
  "international": "International Operations",
  "multi_city": "Multi-City Network",
  "rural_urban": "Rural-Urban Corridor"
};

const ImageAnalyzer = ({ onAnalysisComplete, onCharacterCreated, aiSettings = { provider: 'ollama', safetyLevel: 'moderate' } }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedGenre, setSelectedGenre] = useState("urban_realistic");
  const [characterOrigin, setCharacterOrigin] = useState("nootropic_enhanced");
  const [socialStatus, setSocialStatus] = useState("entrepreneurial");
  const [powerSource, setPowerSource] = useState("nootropic_drug");
  const [evolutionStage, setEvolutionStage] = useState("synergistic");
  const [geographicContext, setGeographicContext] = useState("detroit");
  const [additionalTags, setAdditionalTags] = useState(["System Changer", "Power Broker"]);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [currentCharacter, setCurrentCharacter] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(true);
  const [ruleViolations, setRuleViolations] = useState([]);
  const [opMode, setOpMode] = useState(false);

  const ADDITIONAL_TAGS = [
    "Anti-Hero", "Villain", "Morally Grey", "Reluctant Hero", "Team Leader",
    "Loner", "Mentor Figure", "Rookie", "Veteran", "Reformed Criminal",
    "Double Agent", "Vigilante", "Government Agent", "Rebel", "Pacifist",
    "System Changer", "Power Broker", "Empire Builder", "Network Master",
    "Strategic Mastermind", "Cultural Bridge", "Economic Disruptor", "Shadow Operator",
    "Community Leader", "Underground King", "Corporate Infiltrator", "Street Philosopher",
    // OP Mode tags get added dynamically
    ...(opMode ? OP_ARCHETYPE_TAGS : [])
  ];

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

  const handleTagToggle = (tag) => {
    setAdditionalTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

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

      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 15;
        });
      }, 800);

      // Use the enhanced analyze-image endpoint with AI settings
      const params = new URLSearchParams({
        genre: selectedGenre,
        origin: characterOrigin,
        social_status: socialStatus,
        power_source: powerSource,
        evolution_stage: evolutionStage,
        geographic_context: geographicContext,
        tags: additionalTags.join(','),
        op_mode: opMode ? 'true' : 'false',
        ai_provider: aiSettings.provider || 'ollama',
        safety_level: aiSettings.safetyLevel || 'moderate'
      });

      const response = await axios.post(`${API}/analyze-image?${params}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 90000
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.data.success || response.data.analysis) {
        const analysisData = response.data.analysis || response.data;
        setAnalysis(analysisData);
        setCurrentCharacter(analysisData);
        onAnalysisComplete?.();
        onCharacterCreated?.(analysisData);
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
    setCurrentCharacter(null);
    setPreviewUrl(null);
    setAdditionalTags([]);
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
            Upload artwork and customize character parameters for detailed analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* OP MODE TOGGLE - PROMINENTLY DISPLAYED */}
          <div className={`p-4 rounded-lg border-2 transition-all duration-300 ${
            opMode 
              ? 'border-red-500 bg-gradient-to-r from-red-900/30 to-orange-900/30 shadow-lg shadow-red-500/25' 
              : 'border-yellow-500/50 bg-gradient-to-r from-yellow-900/20 to-orange-900/20 hover:border-yellow-400 cursor-pointer'
          }`}
          onClick={() => setOpMode(!opMode)}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`text-2xl ${opMode ? 'animate-pulse' : ''}`}>
                  🔥
                </div>
                <div>
                  <h3 className={`font-bold ${opMode ? 'text-red-300' : 'text-yellow-300'}`}>
                    BROKEN/OP CHARACTER MODE
                  </h3>
                  <p className={`text-sm ${opMode ? 'text-red-200' : 'text-yellow-200'}`}>
                    Create overpowered characters that break narrative balance
                  </p>
                </div>
              </div>
              <div className={`w-12 h-6 rounded-full ${opMode ? 'bg-red-500' : 'bg-gray-600'} relative transition-colors duration-300`}>
                <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform duration-300 ${
                  opMode ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </div>
            </div>
            {opMode && (
              <div className="mt-3 p-3 bg-red-800/30 rounded border border-red-500/30">
                <p className="text-red-200 text-xs">
                  ⚠️ <strong>WARNING:</strong> OP Mode creates characters that intentionally break story balance, 
                  bypass power limitations, and disrupt narrative scaling. Perfect for exploring "what if" scenarios, 
                  creating final bosses, or writing about consequences of unlimited power.
                </p>
              </div>
            )}
          </div>

          {/* AI Settings Indicator */}
          <div className="p-3 bg-slate-600/30 rounded-lg border border-slate-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Settings className="w-4 h-4 text-indigo-400" />
                <span className="text-sm font-medium text-white">Current AI Configuration</span>
              </div>
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1">
                  {aiSettings.provider === 'ollama' && <Eye className="w-3 h-3 text-blue-400" />}
                  {aiSettings.provider === 'claude' && <Sparkles className="w-3 h-3 text-purple-400" />}
                  {aiSettings.provider === 'openai' && <Zap className="w-3 h-3 text-green-400" />}
                  <span className="text-gray-300 capitalize">{aiSettings.provider}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Shield className="w-3 h-3 text-yellow-400" />
                  <span className="text-gray-300 capitalize">{aiSettings.safetyLevel}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Basic Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            </div>

            {/* Character Origin */}
            <div>
              <label className="block text-sm font-medium text-indigo-300 mb-2">
                Character Origin {opMode && <span className="text-red-300">🔥 OP MODE</span>}
              </label>
              <Select value={characterOrigin} onValueChange={setCharacterOrigin}>
                <SelectTrigger className={`bg-slate-800 border-indigo-500/30 text-white ${
                  opMode ? 'border-red-500/50 shadow-red-500/25' : ''
                }`}>
                  <SelectValue placeholder="Select character origin" />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-indigo-500/30">
                  {/* Regular Origins */}
                  {Object.entries(CHARACTER_ORIGINS).map(([key, origin]) => (
                    <SelectItem key={key} value={key} className="text-white hover:bg-slate-700">
                      <div>
                        <div className="font-medium">{origin.name}</div>
                        <div className="text-xs text-slate-400">{origin.description}</div>
                      </div>
                    </SelectItem>
                  ))}
                  
                  {/* OP Mode Origins */}
                  {opMode && (
                    <>
                      <div className="px-2 py-1 text-xs text-red-300 border-t border-red-500/30 mt-1">
                        🔥 BROKEN ORIGINS - NARRATIVE DESTROYING
                      </div>
                      {Object.entries(OP_CHARACTER_ORIGINS).map(([key, origin]) => (
                        <SelectItem key={key} value={key} className="text-red-300 hover:bg-red-900/30">
                          <div>
                            <div className="font-medium">{origin.name}</div>
                            <div className="text-xs text-red-200">{origin.description}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </>
                  )}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Advanced Settings Toggle */}
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="border-indigo-500/50 text-indigo-300 hover:bg-indigo-500/10"
            >
              <Settings className="w-4 h-4 mr-2" />
              {showAdvanced ? "Hide" : "Show"} Advanced Options
            </Button>
          </div>

          {/* Advanced Settings */}
          {showAdvanced && (
            <div className="space-y-4 p-4 bg-slate-700/30 rounded-lg border border-indigo-500/20">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Social Status */}
                <div>
                  <label className="block text-sm font-medium text-indigo-300 mb-2">
                    Social Status
                  </label>
                  <Select value={socialStatus} onValueChange={setSocialStatus}>
                    <SelectTrigger className="bg-slate-800 border-indigo-500/30 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-indigo-500/30">
                      {Object.entries(SOCIAL_STATUS).map(([key, name]) => (
                        <SelectItem key={key} value={key} className="text-white hover:bg-slate-700">
                          {name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Power Source */}
                <div>
                  <label className="block text-sm font-medium text-indigo-300 mb-2">
                    Power Source {opMode && <span className="text-red-300">🔥 OP MODE</span>}
                  </label>
                  <Select value={powerSource} onValueChange={setPowerSource}>
                    <SelectTrigger className={`bg-slate-800 border-indigo-500/30 text-white ${
                      opMode ? 'border-red-500/50 shadow-red-500/25' : ''
                    }`}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-indigo-500/30">
                      {Object.entries(POWER_SOURCES).map(([key, name]) => {
                        const isOpPower = name.includes('🔥');
                        if (isOpPower && !opMode) return null; // Hide OP powers unless in OP mode
                        
                        return (
                          <SelectItem 
                            key={key} 
                            value={key} 
                            className={`hover:bg-slate-700 ${
                              isOpPower ? 'text-red-300' : 'text-white'
                            }`}
                          >
                            {name}
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>

                {/* Evolution Stage */}
                <div>
                  <label className="block text-sm font-medium text-indigo-300 mb-2">
                    Power Evolution
                  </label>
                  <Select value={evolutionStage} onValueChange={setEvolutionStage}>
                    <SelectTrigger className="bg-slate-800 border-indigo-500/30 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-indigo-500/30">
                      {Object.entries(POWER_EVOLUTION_STAGES).map(([key, name]) => (
                        <SelectItem key={key} value={key} className="text-white hover:bg-slate-700">
                          {name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Geographic Context */}
              <div>
                <label className="block text-sm font-medium text-indigo-300 mb-2">
                  Geographic Context
                </label>
                <Select value={geographicContext} onValueChange={setGeographicContext}>
                  <SelectTrigger className="bg-slate-800 border-indigo-500/30 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-indigo-500/30">
                    {Object.entries(GEOGRAPHIC_CONTEXTS).map(([key, name]) => (
                      <SelectItem key={key} value={key} className="text-white hover:bg-slate-700">
                        {name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Additional Character Tags */}
              <div>
                <label className="block text-sm font-medium text-indigo-300 mb-3">
                  Character Archetype Tags
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {ADDITIONAL_TAGS.map((tag) => (
                    <div key={tag} className="flex items-center space-x-2">
                      <Checkbox
                        id={tag}
                        checked={additionalTags.includes(tag)}
                        onCheckedChange={() => handleTagToggle(tag)}
                        className="border-indigo-500/50 data-[state=checked]:bg-indigo-600"
                      />
                      <label 
                        htmlFor={tag} 
                        className="text-sm text-slate-300 cursor-pointer"
                      >
                        {tag}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Selected Configuration Summary */}
              <div className="bg-slate-800/50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-indigo-300 mb-3">Marcus-Style Character Configuration:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-indigo-300 font-medium">Universe:</span> {GENRES[selectedGenre]}
                  </div>
                  <div>
                    <span className="text-indigo-300 font-medium">Origin:</span> {CHARACTER_ORIGINS[characterOrigin].name}
                  </div>
                  <div>
                    <span className="text-indigo-300 font-medium">Status:</span> {SOCIAL_STATUS[socialStatus]}
                  </div>
                  <div>
                    <span className="text-indigo-300 font-medium">Power Source:</span> {POWER_SOURCES[powerSource]}
                  </div>
                  <div>
                    <span className="text-indigo-300 font-medium">Evolution:</span> {POWER_EVOLUTION_STAGES[evolutionStage]}
                  </div>
                  <div>
                    <span className="text-indigo-300 font-medium">Location:</span> {GEOGRAPHIC_CONTEXTS[geographicContext]}
                  </div>
                  {additionalTags.length > 0 && (
                    <div className="md:col-span-2">
                      <span className="text-indigo-300 font-medium">Archetypes:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {additionalTags.map((tag) => (
                          <Badge key={tag} variant="outline" className="text-pink-300 border-pink-500/50 text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

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
                  Analyzing {CHARACTER_ORIGINS[characterOrigin].name} for {GENRES[selectedGenre]}...
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
                  Analyze {CHARACTER_ORIGINS[characterOrigin].name}
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysis && currentCharacter && (
        <Card className={`fade-in ${
          currentCharacter.op_mode 
            ? 'border-red-500 bg-gradient-to-br from-red-900/20 to-orange-900/20 shadow-lg shadow-red-500/25' 
            : 'visionforge-card'
        }`} data-testid="analysis-results">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className={`flex items-center gap-2 ${currentCharacter.op_mode ? 'text-red-300' : 'text-white'}`}>
                <Sparkles className={`w-5 h-5 ${currentCharacter.op_mode ? 'text-red-400' : 'text-indigo-400'}`} />
                {currentCharacter.op_mode ? '🔥 BROKEN CHARACTER PROFILE' : 'Character Profile Created'}
              </CardTitle>
              <div className="flex gap-2">
                {currentCharacter.op_mode && (
                  <Badge className="bg-red-500/30 text-red-200 border-red-500/50 animate-pulse">
                    🔥 OP MODE - BALANCE BREAKER
                  </Badge>
                )}
                <Badge className={`${
                  currentCharacter.op_mode 
                    ? 'bg-red-500/20 text-red-300 border-red-500/30' 
                    : 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30'
                }`}>
                  {GENRES[selectedGenre]}
                </Badge>
                <Badge className={`${
                  currentCharacter.op_mode 
                    ? 'bg-orange-500/20 text-orange-300 border-orange-500/30' 
                    : 'bg-purple-500/20 text-purple-300 border-purple-500/30'
                }`}>
                  {OP_CHARACTER_ORIGINS[currentCharacter.character_origin]?.name || 
                   CHARACTER_ORIGINS[currentCharacter.character_origin]?.name}
                </Badge>
              </div>
            </div>
            <CardDescription className={currentCharacter.op_mode ? 'text-red-200' : 'text-indigo-200'}>
              {currentCharacter.op_mode 
                ? '🔥 Overpowered character that intentionally breaks story balance and narrative constraints'
                : `${CHARACTER_ORIGINS[currentCharacter.character_origin]?.name || 'Enhanced'} character adapted for ${GENRES[selectedGenre]} universe`
              }
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* OP Mode Warning */}
            {currentCharacter.op_mode && (
              <div className="bg-red-800/30 border border-red-500/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl animate-pulse">🔥</span>
                  <h3 className="font-bold text-red-300">NARRATIVE BALANCE DESTROYED</h3>
                </div>
                <p className="text-red-200 text-sm">
                  {currentCharacter.balance_warning || 
                   "This character is intentionally overpowered and will break any balanced story. Perfect for exploring power fantasy scenarios, final boss encounters, or examining the narrative consequences of unlimited abilities."}
                </p>
                {currentCharacter.total_power_cost && (
                  <p className="text-red-300 text-xs mt-2">
                    Total Power Cost: <span className="font-mono">{currentCharacter.total_power_cost}/30</span> 
                    <span className="text-red-400"> (300% OVER LIMIT)</span>
                  </p>
                )}
              </div>
            )}

            {/* Character Summary */}
            <div className="analysis-summary">
              <h3 className="text-lg font-semibold text-indigo-300 mb-3">Character Summary</h3>
              <p className="text-indigo-100 leading-relaxed" data-testid="persona-summary">
                {currentCharacter.persona_summary}
              </p>
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
                {CHARACTER_ORIGINS[characterOrigin].name} Powers ({POWER_SOURCES[powerSource]})
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
                    <div className="bg-red-900/20 rounded px-3 py-2">
                      <p className="text-xs text-red-300">
                        <strong>Limitations:</strong> {power.limitations}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Continuity Linter Integration */}
            <Separator className="bg-indigo-500/30" />
            
            <ContinuityLinter 
              characterId={currentCharacter.id}
              characterData={currentCharacter}
              onViolationsUpdate={setRuleViolations}
            />

            {/* Character Classification Summary */}
            <div className="bg-slate-700/30 rounded-lg p-4">
              <h4 className="text-sm font-medium text-slate-300 mb-3">Character Classification</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-indigo-300 font-medium">Origin:</span> {CHARACTER_ORIGINS[characterOrigin].name}
                </div>
                <div>
                  <span className="text-indigo-300 font-medium">Social Status:</span> {SOCIAL_STATUS[socialStatus]}
                </div>
                <div>
                  <span className="text-indigo-300 font-medium">Power Source:</span> {POWER_SOURCES[powerSource]}
                </div>
                <div>
                  <span className="text-indigo-300 font-medium">Universe:</span> {GENRES[selectedGenre]}
                </div>
                {additionalTags.length > 0 && (
                  <div className="md:col-span-2">
                    <span className="text-indigo-300 font-medium">Archetypes:</span> {additionalTags.join(", ")}
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ImageAnalyzer;