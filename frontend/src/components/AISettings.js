import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Label } from './ui/label';
import { toast } from 'sonner';
import { Settings, Shield, Cpu, Cloud, Zap, CheckCircle, AlertTriangle } from 'lucide-react';

const AISettings = ({ onSettingsChange }) => {
  const [aiProviders, setAiProviders] = useState([]);
  const [safetyLevels, setSafetyLevels] = useState([]);
  const [currentProvider, setCurrentProvider] = useState('');
  const [currentSafetyLevel, setCurrentSafetyLevel] = useState('moderate');
  const [isLoading, setIsLoading] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchAIProviders();
    fetchSafetyLevels();
  }, []);

  const fetchAIProviders = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/ai-providers`);
      const data = await response.json();
      
      if (data.success) {
        setAiProviders(data.providers || []);
        setCurrentProvider(data.default_provider || 'ollama');
      }
    } catch (error) {
      console.error('Failed to fetch AI providers:', error);
      toast.error('Failed to load AI providers');
    }
  };

  const fetchSafetyLevels = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/content-safety-levels`);
      const data = await response.json();
      
      if (data.success) {
        setSafetyLevels(data.safety_levels || []);
      }
    } catch (error) {
      console.error('Failed to fetch safety levels:', error);
      toast.error('Failed to load content safety levels');
    }
  };

  const handleProviderChange = async (providerId) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/set-default-provider`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ provider: providerId }),
      });

      const data = await response.json();
      
      if (data.success) {
        setCurrentProvider(providerId);
        toast.success(`Default AI provider set to ${data.provider}`);
        
        // Notify parent component
        if (onSettingsChange) {
          onSettingsChange({ provider: providerId, safetyLevel: currentSafetyLevel });
        }
      } else {
        throw new Error(data.message || 'Failed to set provider');
      }
    } catch (error) {
      console.error('Failed to set provider:', error);
      toast.error('Failed to change AI provider: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSafetyLevelChange = (level) => {
    setCurrentSafetyLevel(level);
    toast.success(`Content safety set to ${level}`);
    
    // Notify parent component
    if (onSettingsChange) {
      onSettingsChange({ provider: currentProvider, safetyLevel: level });
    }
  };

  const getProviderIcon = (providerId) => {
    switch (providerId) {
      case 'ollama':
        return <Cpu className="w-4 h-4" />;
      case 'claude':
        return <Cloud className="w-4 h-4" />;
      case 'openai':
        return <Zap className="w-4 h-4" />;
      default:
        return <Settings className="w-4 h-4" />;
    }
  };

  const getSafetyIcon = (level) => {
    switch (level) {
      case 'strict':
        return <Shield className="w-4 h-4 text-green-400" />;
      case 'moderate':
        return <CheckCircle className="w-4 h-4 text-blue-400" />;
      case 'permissive':
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      default:
        return <Shield className="w-4 h-4" />;
    }
  };

  const getSafetyColor = (level) => {
    switch (level) {
      case 'strict':
        return 'border-green-500/30 bg-green-900/20';
      case 'moderate':
        return 'border-blue-500/30 bg-blue-900/20';
      case 'permissive':
        return 'border-yellow-500/30 bg-yellow-900/20';
      default:
        return 'border-gray-500/30 bg-gray-900/20';
    }
  };

  return (
    <div className="space-y-6">
      {/* AI Provider Selection */}
      <Card className="border-indigo-500/30 bg-slate-700/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Settings className="w-5 h-5" />
            AI Provider Selection
          </CardTitle>
          <CardDescription className="text-indigo-200">
            Choose between local Ollama models and cloud-based AI for different use cases
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label className="text-white">Current Provider</Label>
            <Select value={currentProvider} onValueChange={handleProviderChange} disabled={isLoading}>
              <SelectTrigger className="bg-slate-600 border-slate-500 text-white">
                <SelectValue placeholder="Select AI provider..." />
              </SelectTrigger>
              <SelectContent>
                {aiProviders.map((provider) => (
                  <SelectItem key={provider.id} value={provider.id}>
                    <div className="flex items-center gap-2 w-full">
                      {getProviderIcon(provider.id)}
                      <div className="flex-1">
                        <div className="font-medium">{provider.name}</div>
                        <div className="text-xs text-gray-400">{provider.description}</div>
                      </div>
                      <div className="flex items-center gap-1">
                        {provider.status?.available ? (
                          <Badge variant="secondary" className="text-xs bg-green-900/30 text-green-400">
                            Available
                          </Badge>
                        ) : (
                          <Badge variant="destructive" className="text-xs">
                            Unavailable
                          </Badge>
                        )}
                      </div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Provider Details */}
          {aiProviders.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {aiProviders.map((provider) => (
                <div
                  key={provider.id}
                  className={`p-3 rounded-lg border transition-all ${
                    currentProvider === provider.id
                      ? 'border-indigo-500 bg-indigo-900/20'
                      : 'border-slate-500 bg-slate-600/30'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    {getProviderIcon(provider.id)}
                    <span className="font-medium text-white text-sm">{provider.name}</span>
                    {provider.status?.available && (
                      <CheckCircle className="w-3 h-3 text-green-400" />
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <div>
                      <div className="text-xs text-gray-400 mb-1">Strengths:</div>
                      <div className="flex flex-wrap gap-1">
                        {provider.strengths?.slice(0, 2).map((strength, index) => (
                          <Badge key={index} variant="outline" className="text-xs bg-slate-800/50 text-gray-300">
                            {strength}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-xs text-gray-400 mb-1">Best for:</div>
                      <div className="text-xs text-gray-300">
                        {provider.best_for?.slice(0, 2).join(', ')}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Content Safety Settings */}
      <Card className="border-yellow-500/30 bg-slate-700/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Content Safety Level
          </CardTitle>
          <CardDescription className="text-yellow-200">
            Control content filtering for your creative projects - a key VisionForge differentiator
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {safetyLevels.map((level) => (
              <div
                key={level.id}
                onClick={() => handleSafetyLevelChange(level.id)}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  currentSafetyLevel === level.id
                    ? getSafetyColor(level.id) + ' ring-2 ring-current'
                    : 'border-slate-500 bg-slate-600/30 hover:bg-slate-600/50'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  {getSafetyIcon(level.id)}
                  <span className="font-medium text-white">{level.name}</span>
                  {currentSafetyLevel === level.id && (
                    <CheckCircle className="w-4 h-4 text-current ml-auto" />
                  )}
                </div>
                
                <p className="text-sm text-gray-300 mb-2">{level.description}</p>
                
                <div className="text-xs text-gray-400">
                  <strong>Target:</strong> {level.target_audience}
                </div>
                
                {level.allowed_categories && (
                  <div className="mt-2">
                    <div className="text-xs text-gray-400 mb-1">Allowed content:</div>
                    <div className="flex flex-wrap gap-1">
                      {level.allowed_categories.slice(0, 3).map((category, index) => (
                        <Badge key={index} variant="outline" className="text-xs bg-slate-800/30 text-gray-400">
                          {category.replace('_', ' ')}
                        </Badge>
                      ))}
                      {level.allowed_categories.length > 3 && (
                        <Badge variant="outline" className="text-xs bg-slate-800/30 text-gray-400">
                          +{level.allowed_categories.length - 3} more
                        </Badge>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Current Settings Summary */}
          <div className="p-3 bg-slate-600/30 rounded-lg border border-slate-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Settings className="w-4 h-4 text-indigo-400" />
                <span className="text-sm font-medium text-white">Current Configuration</span>
              </div>
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1">
                  {getProviderIcon(currentProvider)}
                  <span className="text-gray-300">{currentProvider.toUpperCase()}</span>
                </div>
                <div className="flex items-center gap-1">
                  {getSafetyIcon(currentSafetyLevel)}
                  <span className="text-gray-300">{currentSafetyLevel.toUpperCase()}</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AISettings;