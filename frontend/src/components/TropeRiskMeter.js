import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { Loader2, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Zap, Eye, Lightbulb, User } from 'lucide-react';
import { useCharacter } from '../contexts/CharacterContext';

const TropeRiskMeter = () => {
  // Character context for cross-tool character access
  const { currentCharacter, hasActiveCharacter, getCharacterName } = useCharacter();
  
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [tropeAnalysis, setTropeAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [useCurrentCharacter, setUseCurrentCharacter] = useState(true);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchAnalysisHistory();
  }, []);

  const fetchAnalysisHistory = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/analyses`);
      const data = await response.json();
      setAnalysisHistory(data || []);
    } catch (error) {
      console.error('Failed to fetch analysis history:', error);
      toast.error('Failed to load character history');
    }
  };

  const analyzeTropeRisk = async (character) => {
    setIsLoading(true);
    setSelectedCharacter(character);
    
    try {
      const characterData = {
        id: character.id,
        character_origin: character.character_origin || 'unknown',
        power_source: character.power_source || 'unknown',
        social_status: character.social_status || 'unknown',
        archetype_tags: character.archetype_tags || [],
        genre_universe: character.genre || 'urban_realistic',
        traits: character.traits || [],
        backstory_seeds: character.backstory_seeds || [],
        power_suggestions: character.power_suggestions || []
      };

      const response = await fetch(`${backendUrl}/api/analyze-trope-risk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ character_data: characterData }),
      });

      const data = await response.json();

      if (data.success) {
        setTropeAnalysis(data.trope_analysis);
        toast.success('Trope analysis completed!');
      } else {
        throw new Error(data.message || 'Failed to analyze tropes');
      }
    } catch (error) {
      console.error('Trope analysis failed:', error);
      toast.error('Failed to analyze tropes: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const getFreshnessColor = (score) => {
    if (score >= 0.8) return 'text-green-400';
    if (score >= 0.6) return 'text-blue-400';
    if (score >= 0.4) return 'text-yellow-400';
    if (score >= 0.2) return 'text-orange-400';
    return 'text-red-400';
  };

  const getFreshnessIcon = (level) => {
    switch (level) {
      case 'groundbreaking':
        return <Zap className="w-4 h-4 text-yellow-400" />;
      case 'fresh':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'familiar':
        return <Eye className="w-4 h-4 text-blue-400" />;
      case 'clichéd':
        return <TrendingDown className="w-4 h-4 text-orange-400" />;
      case 'overused':
        return <AlertTriangle className="w-4 h-4 text-red-400" />;
      default:
        return <Eye className="w-4 h-4 text-gray-400" />;
    }
  };

  const getRiskBadgeVariant = (score) => {
    if (score <= 0.3) return 'secondary'; // Low risk
    if (score <= 0.6) return 'default';   // Medium risk
    return 'destructive';                 // High risk
  };

  return (
    <div className="space-y-6">
      {/* Character Selection */}
      <Card className="border-indigo-500/30 bg-slate-700/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Select Character for Analysis
          </CardTitle>
          <CardDescription className="text-indigo-200">
            Choose a character from your analysis history to evaluate trope usage and cliché risks
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Current Character Option */}
          {hasActiveCharacter && (
            <div className="mb-6 p-4 bg-indigo-900/20 rounded-lg border border-indigo-500/30">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4 text-indigo-400" />
                  <span className="text-white font-medium">Current Character</span>
                </div>
                <Button
                  onClick={() => analyzeTropeRisk(currentCharacter)}
                  disabled={isLoading}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  {isLoading && selectedCharacter === currentCharacter ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <TrendingUp className="w-4 h-4 mr-2" />
                      Analyze Current
                    </>
                  )}
                </Button>
              </div>
              <div className="text-sm text-indigo-200">
                <div className="font-medium">{getCharacterName()}</div>
                <div className="text-xs text-indigo-300">
                  {currentCharacter?.character_origin || 'Unknown origin'} • {currentCharacter?.genre_universe || 'Unknown genre'}
                </div>
              </div>
            </div>
          )}
          
          {analysisHistory.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Eye className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No characters available for analysis.</p>
              <p className="text-sm">Create some characters using the Image Analyzer first.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analysisHistory.map((character, index) => (
                <div
                  key={index}
                  className="p-4 bg-slate-600/50 rounded-lg border border-slate-500 hover:border-indigo-400 cursor-pointer transition-all duration-200 hover:bg-slate-600/70"
                  onClick={() => analyzeTropeRisk(character)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-medium text-white truncate">
                      {character.persona_summary?.substring(0, 30) || 'Unnamed Character'}...
                    </div>
                    <div className="text-xs text-gray-400">
                      {character.traits?.length || 0} traits
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-300 mb-2">
                    <div>{character.character_origin || 'Unknown Origin'}</div>
                    <div className="text-xs text-gray-400">{character.power_source || 'Unknown Power'}</div>
                  </div>
                  
                  {character.archetype_tags && character.archetype_tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {character.archetype_tags.slice(0, 2).map((tag, tagIndex) => (
                        <Badge key={tagIndex} variant="outline" className="text-xs bg-indigo-900/30 text-indigo-300 border-indigo-500/30">
                          {tag}
                        </Badge>
                      ))}
                      {character.archetype_tags.length > 2 && (
                        <Badge variant="outline" className="text-xs bg-gray-900/30 text-gray-400">
                          +{character.archetype_tags.length - 2}
                        </Badge>
                      )}
                    </div>
                  )}
                  
                  <Button
                    size="sm"
                    variant="outline"
                    className="w-full mt-2 bg-indigo-900/30 border-indigo-500/30 text-indigo-300 hover:bg-indigo-800/50"
                    disabled={isLoading}
                  >
                    {isLoading && selectedCharacter === character ? (
                      <>
                        <Loader2 className="w-3 h-3 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <TrendingUp className="w-3 h-3 mr-2" />
                        Analyze Tropes
                      </>
                    )}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Trope Analysis Results */}
      {tropeAnalysis && (
        <div className="space-y-6">
          {/* Overall Score */}
          <Card className="border-indigo-500/30 bg-slate-700/50">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Overall Freshness Analysis
              </CardTitle>
              <CardDescription className="text-indigo-200">
                Character ID: {tropeAnalysis.character_id}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className={`text-4xl font-bold ${getFreshnessColor(tropeAnalysis.overall_freshness_score)}`}>
                    {Math.round(tropeAnalysis.overall_freshness_score * 100)}%
                  </div>
                  <div className="text-sm text-gray-400 mt-1">Overall Freshness</div>
                  <div className="text-indigo-300 font-medium mt-2">{tropeAnalysis.freshness_rating}</div>
                </div>
                
                <div className="text-center">
                  <div className={`text-4xl font-bold ${getFreshnessColor(tropeAnalysis.marcus_level_rating)}`}>
                    {Math.round(tropeAnalysis.marcus_level_rating * 100)}%
                  </div>
                  <div className="text-sm text-gray-400 mt-1">Sophistication Level</div>
                  <div className="text-yellow-300 font-medium mt-2">
                    {tropeAnalysis.marcus_level_rating >= 0.8 ? 'Marcus-Level' :
                     tropeAnalysis.marcus_level_rating >= 0.6 ? 'Sophisticated' :
                     tropeAnalysis.marcus_level_rating >= 0.4 ? 'Developing' : 'Basic'}
                  </div>
                </div>
                
                <div className="text-center">
                  <div className="text-4xl font-bold text-white">
                    {tropeAnalysis.trope_analyses?.length || 0}
                  </div>
                  <div className="text-sm text-gray-400 mt-1">Tropes Analyzed</div>
                  <div className="flex justify-center gap-2 mt-2">
                    <Badge variant="secondary" className="text-xs">
                      {tropeAnalysis.strength_factors?.length || 0} strengths
                    </Badge>
                    <Badge variant="destructive" className="text-xs">
                      {tropeAnalysis.risk_factors?.length || 0} risks
                    </Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Individual Trope Analysis */}
          {tropeAnalysis.trope_analyses && tropeAnalysis.trope_analyses.length > 0 && (
            <Card className="border-indigo-500/30 bg-slate-700/50">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Eye className="w-5 h-5" />
                  Individual Trope Analysis
                </CardTitle>
                <CardDescription className="text-indigo-200">
                  Detailed breakdown of each identified trope and its freshness level
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {tropeAnalysis.trope_analyses.map((trope, index) => (
                  <div key={index} className="p-4 bg-slate-600/30 rounded-lg border border-slate-500">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        {getFreshnessIcon(trope.freshness_level)}
                        <h4 className="font-semibold text-white capitalize">
                          {trope.trope_name.replace(/_/g, ' ')}
                        </h4>
                      </div>
                      <div className="text-right">
                        <Badge variant={getRiskBadgeVariant(trope.cliche_score)} className="mb-1">
                          {Math.round((1 - trope.cliche_score) * 100)}% Fresh
                        </Badge>
                        <div className="text-xs text-gray-400">
                          Used {trope.usage_frequency?.toLocaleString() || 0} times in fiction
                        </div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <Progress 
                        value={(1 - trope.cliche_score) * 100} 
                        className="h-2"
                      />
                      <div className="flex justify-between text-xs text-gray-400 mt-1">
                        <span>Clichéd</span>
                        <span className="capitalize">{trope.freshness_level}</span>
                        <span>Original</span>
                      </div>
                    </div>
                    
                    {/* Subversion Suggestions */}
                    {trope.subversion_suggestions && trope.subversion_suggestions.length > 0 && (
                      <div className="mb-3">
                        <div className="text-sm font-medium text-indigo-300 mb-2">Subversion Ideas:</div>
                        <ul className="list-disc list-inside space-y-1">
                          {trope.subversion_suggestions.map((suggestion, sugIndex) => (
                            <li key={sugIndex} className="text-sm text-gray-300">{suggestion}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* Combination Alternatives */}
                    {trope.combination_alternatives && trope.combination_alternatives.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-yellow-300 mb-2">Combination Ideas:</div>
                        <ul className="list-disc list-inside space-y-1">
                          {trope.combination_alternatives.map((combo, comboIndex) => (
                            <li key={comboIndex} className="text-sm text-gray-300">{combo}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Improvement Suggestions */}
          {tropeAnalysis.improvement_suggestions && tropeAnalysis.improvement_suggestions.length > 0 && (
            <Card className="border-green-500/30 bg-green-900/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Lightbulb className="w-5 h-5" />
                  AI-Enhanced Improvement Suggestions
                </CardTitle>
                <CardDescription className="text-green-200">
                  Personalized recommendations generated by Ollama AI
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {tropeAnalysis.improvement_suggestions.map((suggestion, index) => (
                    <div key={index} className="p-3 bg-green-900/20 rounded-lg border border-green-500/30">
                      <div className="flex items-start gap-3">
                        <div className="w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                          {index + 1}
                        </div>
                        <div className="text-green-100">{suggestion}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Marcus-Style Adaptations */}
          {tropeAnalysis.marcus_adaptations && tropeAnalysis.marcus_adaptations.length > 0 && (
            <Card className="border-yellow-500/30 bg-yellow-900/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Zap className="w-5 h-5" />
                  Sophisticated Character Adaptations
                </CardTitle>
                <CardDescription className="text-yellow-200">
                  Guidelines for creating Marcus-level character sophistication
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {tropeAnalysis.marcus_adaptations.map((adaptation, index) => (
                    <div key={index} className="p-3 bg-yellow-900/20 rounded-lg border border-yellow-500/30">
                      <div className="flex items-start gap-3">
                        <div className="w-6 h-6 bg-yellow-600 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                          ★
                        </div>
                        <div className="text-yellow-100">{adaptation}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default TropeRiskMeter;