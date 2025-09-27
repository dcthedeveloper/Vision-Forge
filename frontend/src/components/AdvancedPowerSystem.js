import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Label } from './ui/label';
import { toast } from 'sonner';
import { Zap, Sparkles, Target, TrendingUp, Brain, Shield, Clock, Users, Lightbulb } from 'lucide-react';

const AdvancedPowerSystem = ({ aiSettings = { provider: 'ollama', safetyLevel: 'moderate' } }) => {
  const [themes, setThemes] = useState([]);
  const [selectedTheme, setSelectedTheme] = useState('none');
  const [complexityLevel, setComplexityLevel] = useState('moderate');
  const [characterContext, setCharacterContext] = useState({});
  const [generatedSystem, setGeneratedSystem] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchThemes();
  }, []);

  const fetchThemes = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/power-system-themes`);
      const data = await response.json();
      setThemes(data.themes || []);
    } catch (error) {
      console.error('Failed to fetch themes:', error);
      toast.error('Failed to load power system themes');
    }
  };

  const generatePowerSystem = async () => {
    setIsLoading(true);
    try {
      const requestData = {
        character_context: characterContext,
        narrative_focus: selectedTheme && selectedTheme !== 'none' ? selectedTheme : undefined,
        complexity_level: complexityLevel
      };

      const response = await fetch(`${backendUrl}/api/generate-power-system`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      if (data.success) {
        setGeneratedSystem(data.power_system);
        toast.success('Advanced power system generated!');
      } else {
        throw new Error(data.message || 'Failed to generate power system');
      }
    } catch (error) {
      console.error('Power system generation failed:', error);
      toast.error('Failed to generate power system: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const getMetricColor = (value) => {
    if (value >= 0.7) return 'text-red-400';
    if (value >= 0.5) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getMetricIcon = (metric) => {
    const icons = {
      raw_power_level: <Zap className="w-4 h-4" />,
      control_precision: <Target className="w-4 h-4" />,
      cost_severity: <Shield className="w-4 h-4" />,
      social_impact: <Users className="w-4 h-4" />,
      progression_speed: <TrendingUp className="w-4 h-4" />,
      uniqueness_factor: <Sparkles className="w-4 h-4" />
    };
    return icons[metric] || <Brain className="w-4 h-4" />;
  };

  return (
    <div className="space-y-6">
      {/* Configuration Panel */}
      <Card className="border-indigo-500/30 bg-slate-700/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Brain className="w-5 h-5" />
            Advanced Power System Generator
          </CardTitle>
          <CardDescription className="text-indigo-200">
            Generate sophisticated power systems using patterns from 20+ fictional works
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="theme" className="text-white">Narrative Theme (Optional)</Label>
              <Select value={selectedTheme} onValueChange={setSelectedTheme}>
                <SelectTrigger className="bg-slate-600 border-slate-500 text-white">
                  <SelectValue placeholder="Choose thematic focus..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No specific theme</SelectItem>
                  {themes.map((theme) => (
                    <SelectItem key={theme.id} value={theme.id}>
                      <div className="space-y-1">
                        <div className="font-medium">{theme.name}</div>
                        <div className="text-xs text-gray-400">{theme.description}</div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="complexity" className="text-white">Complexity Level</Label>
              <Select value={complexityLevel} onValueChange={setComplexityLevel}>
                <SelectTrigger className="bg-slate-600 border-slate-500 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="simple">
                    <div className="space-y-1">
                      <div className="font-medium">Simple</div>
                      <div className="text-xs text-gray-400">Straightforward powers with clear rules</div>
                    </div>
                  </SelectItem>
                  <SelectItem value="moderate">
                    <div className="space-y-1">
                      <div className="font-medium">Moderate</div>
                      <div className="text-xs text-gray-400">Balanced complexity with interesting interactions</div>
                    </div>
                  </SelectItem>
                  <SelectItem value="complex">
                    <div className="space-y-1">
                      <div className="font-medium">Complex</div>
                      <div className="text-xs text-gray-400">Intricate systems with multiple layers</div>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button
            onClick={generatePowerSystem}
            disabled={isLoading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            {isLoading ? (
              <>
                <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                Generating Power System...
              </>
            ) : (
              <>
                <Brain className="w-4 h-4 mr-2" />
                Generate Advanced Power System
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Generated Power System Display */}
      {generatedSystem && (
        <div className="space-y-6">
          {/* Power System Overview */}
          <Card className="border-purple-500/30 bg-slate-700/50">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Zap className="w-5 h-5 text-purple-400" />
                Power System Blueprint
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Power Source */}
                <div className="p-4 bg-blue-900/20 rounded-lg border border-blue-500/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-blue-400" />
                    <h4 className="font-semibold text-blue-300">Power Source</h4>
                  </div>
                  <h5 className="text-white font-medium">{generatedSystem.power_source.name}</h5>
                  <p className="text-blue-200 text-sm mt-1">{generatedSystem.power_source.description}</p>
                </div>

                {/* Mechanic */}
                <div className="p-4 bg-green-900/20 rounded-lg border border-green-500/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Target className="w-4 h-4 text-green-400" />
                    <h4 className="font-semibold text-green-300">Mechanic</h4>
                  </div>
                  <h5 className="text-white font-medium">{generatedSystem.mechanic.name}</h5>
                  <p className="text-green-200 text-sm mt-1">{generatedSystem.mechanic.description}</p>
                </div>

                {/* Primary Limitation */}
                <div className="p-4 bg-red-900/20 rounded-lg border border-red-500/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Shield className="w-4 h-4 text-red-400" />
                    <h4 className="font-semibold text-red-300">Primary Limitation</h4>
                  </div>
                  <h5 className="text-white font-medium">{generatedSystem.limitations.primary.name}</h5>
                  <p className="text-red-200 text-sm mt-1">{generatedSystem.limitations.primary.description}</p>
                </div>

                {/* Progression Model */}
                <div className="p-4 bg-yellow-900/20 rounded-lg border border-yellow-500/30">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-yellow-400" />
                    <h4 className="font-semibold text-yellow-300">Progression Model</h4>
                  </div>
                  <h5 className="text-white font-medium">{generatedSystem.progression.name}</h5>
                  <p className="text-yellow-200 text-sm mt-1">{generatedSystem.progression.description}</p>
                </div>
              </div>

              {/* Secondary Limitation */}
              {generatedSystem.limitations.secondary && (
                <div className="p-4 bg-orange-900/20 rounded-lg border border-orange-500/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="w-4 h-4 text-orange-400" />
                    <h4 className="font-semibold text-orange-300">Secondary Limitation</h4>
                  </div>
                  <h5 className="text-white font-medium">{generatedSystem.limitations.secondary.name}</h5>
                  <p className="text-orange-200 text-sm mt-1">{generatedSystem.limitations.secondary.description}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Power Metrics */}
          <Card className="border-cyan-500/30 bg-slate-700/50">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-cyan-400" />
                Power Metrics
              </CardTitle>
              <CardDescription className="text-cyan-200">
                Quantified aspects of this power system
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(generatedSystem.power_metrics).map(([metric, value]) => (
                  <div key={metric} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getMetricIcon(metric)}
                        <span className="text-white text-sm font-medium">
                          {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      </div>
                      <span className={`text-sm font-bold ${getMetricColor(value)}`}>
                        {Math.round(value * 100)}%
                      </span>
                    </div>
                    <Progress value={value * 100} className="h-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Narrative Elements */}
          <Card className="border-purple-500/30 bg-slate-700/50">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-400" />
                Narrative Elements
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Thematic Resonance */}
              <div>
                <h4 className="text-purple-300 font-medium mb-2">Thematic Resonance</h4>
                <div className="flex flex-wrap gap-2">
                  {generatedSystem.narrative_elements.thematic_resonance.map((theme, index) => (
                    <Badge key={index} variant="outline" className="bg-purple-900/30 text-purple-200 border-purple-500/30">
                      {theme}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Societal Role */}
              <div>
                <h4 className="text-purple-300 font-medium mb-2">Societal Role</h4>
                <p className="text-white bg-purple-900/20 p-3 rounded border border-purple-500/30">
                  {generatedSystem.narrative_elements.societal_role}
                </p>
              </div>

              {/* Philosophical Question */}
              <div>
                <h4 className="text-purple-300 font-medium mb-2">Core Philosophical Question</h4>
                <p className="text-white bg-purple-900/20 p-3 rounded border border-purple-500/30 italic">
                  "{generatedSystem.narrative_elements.philosophical_question}"
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Creative Applications */}
          <Card className="border-green-500/30 bg-slate-700/50">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-green-400" />
                Creative Applications
              </CardTitle>
              <CardDescription className="text-green-200">
                Specific ways to use this power system in stories
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {generatedSystem.creative_suggestions.map((suggestion, index) => (
                  <div key={index} className="p-3 bg-green-900/20 rounded-lg border border-green-500/30">
                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                        {index + 1}
                      </div>
                      <p className="text-green-100">{suggestion}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AdvancedPowerSystem;