import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';  
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Textarea } from './ui/textarea';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { toast } from 'sonner';
import { BookOpen, AlertCircle, CheckCircle, Lightbulb, TrendingUp, Eye, Zap, Brain } from 'lucide-react';

const EnhancedStyleCoach = ({ aiSettings = { provider: 'ollama', safetyLevel: 'moderate' } }) => {
  const [text, setText] = useState('');
  const [styleAnalysis, setStyleAnalysis] = useState(null);
  const [helpResources, setHelpResources] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchHelpResources();
  }, []);

  const fetchHelpResources = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/style-coach-help`);
      const data = await response.json();
      if (data.success) {
        setHelpResources(data);
      }
    } catch (error) {
      console.error('Failed to fetch help resources:', error);
    }
  };

  const analyzeStyle = async () => {
    if (!text.trim()) {
      toast.error('Please enter text to analyze');
      return;
    }

    setIsLoading(true);
    try {
      const requestData = {
        text: text,
        focus_areas: [] // Could be expanded for targeted analysis
      };

      const response = await fetch(`${backendUrl}/api/analyze-style-enhanced`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      if (data.success) {
        setStyleAnalysis(data.style_analysis);
        toast.success('Style analysis completed!');
      } else {
        throw new Error(data.message || 'Failed to analyze style');
      }
    } catch (error) {
      console.error('Style analysis failed:', error);
      toast.error('Failed to analyze style: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-400';
    if (score >= 0.6) return 'text-yellow-400';
    if (score >= 0.4) return 'text-orange-400';
    return 'text-red-400';
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'high':
        return <AlertCircle className="w-4 h-4 text-orange-500" />;
      case 'medium':
        return <Eye className="w-4 h-4 text-yellow-500" />;
      case 'low':
        return <CheckCircle className="w-4 h-4 text-blue-500" />;
      default:
        return <Eye className="w-4 h-4 text-gray-500" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'border-red-500/50 bg-red-900/20';
      case 'high':
        return 'border-orange-500/50 bg-orange-900/20';
      case 'medium':
        return 'border-yellow-500/50 bg-yellow-900/20';
      case 'low':
        return 'border-blue-500/50 bg-blue-900/20';
      default:
        return 'border-gray-500/50 bg-gray-900/20';
    }
  };

  const getIssueTypeIcon = (type) => {
    const icons = {
      cliche_language: <Eye className="w-4 h-4" />,
      telling_not_showing: <BookOpen className="w-4 h-4" />,
      passive_voice: <TrendingUp className="w-4 h-4" />,
      weak_verbs: <Zap className="w-4 h-4" />,
      filter_words: <Eye className="w-4 h-4" />,
      ai_telltales: <Brain className="w-4 h-4" />,
      adverb_overuse: <AlertCircle className="w-4 h-4" />,
      repetitive_structure: <BookOpen className="w-4 h-4" />
    };
    return icons[type] || <BookOpen className="w-4 h-4" />;
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card className="border-indigo-500/30 bg-slate-700/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            Enhanced Style Coach
          </CardTitle>
          <CardDescription className="text-indigo-200">
            Get detailed explanations for style issues with educational rationale
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-white">Text to Analyze</label>
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste your writing here to get detailed style analysis with explanations..."
              className="min-h-32 bg-slate-600 border-slate-500 text-white placeholder-gray-400"
            />
          </div>

          <Button
            onClick={analyzeStyle}
            disabled={isLoading || !text.trim()}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            {isLoading ? (
              <>
                <BookOpen className="w-4 h-4 mr-2 animate-spin" />
                Analyzing Style...
              </>
            ) : (
              <>
                <BookOpen className="w-4 h-4 mr-2" />
                Analyze Writing Style
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results Section */}
      {styleAnalysis && (
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="issues">Issues</TabsTrigger>
            <TabsTrigger value="education">Learn</TabsTrigger>
            <TabsTrigger value="strengths">Strengths</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <Card className="border-cyan-500/30 bg-slate-700/50">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-cyan-400" />
                  Style Analysis Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="text-center">
                    <div className={`text-3xl font-bold ${getScoreColor(styleAnalysis.overall_score)}`}>
                      {Math.round(styleAnalysis.overall_score * 100)}%
                    </div>
                    <div className="text-sm text-gray-400">Overall Score</div>
                  </div>
                  <div className="text-center">
                    <div className={`text-3xl font-bold ${getScoreColor(styleAnalysis.readability_score)}`}>
                      {Math.round(styleAnalysis.readability_score * 100)}%
                    </div>
                    <div className="text-sm text-gray-400">Readability</div>
                  </div>
                  <div className="text-center">
                    <div className={`text-3xl font-bold ${getScoreColor(styleAnalysis.engagement_score)}`}>
                      {Math.round(styleAnalysis.engagement_score * 100)}%
                    </div>
                    <div className="text-sm text-gray-400">Engagement</div>
                  </div>
                  <div className="text-center">
                    <div className={`text-3xl font-bold ${getScoreColor(styleAnalysis.professionalism_score)}`}>
                      {Math.round(styleAnalysis.professionalism_score * 100)}%
                    </div>
                    <div className="text-sm text-gray-400">Professionalism</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <h4 className="text-white font-medium mb-2">Progress Breakdown</h4>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-300">Overall Quality</span>
                          <span className={getScoreColor(styleAnalysis.overall_score)}>
                            {Math.round(styleAnalysis.overall_score * 100)}%
                          </span>
                        </div>
                        <Progress value={styleAnalysis.overall_score * 100} className="h-2" />
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-300">Readability</span>
                          <span className={getScoreColor(styleAnalysis.readability_score)}>
                            {Math.round(styleAnalysis.readability_score * 100)}%
                          </span>
                        </div>
                        <Progress value={styleAnalysis.readability_score * 100} className="h-2" />
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-300">Engagement</span>
                          <span className={getScoreColor(styleAnalysis.engagement_score)}>
                            {Math.round(styleAnalysis.engagement_score * 100)}%
                          </span>
                        </div>
                        <Progress value={styleAnalysis.engagement_score * 100} className="h-2" />
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-white">{styleAnalysis.total_issues}</div>
                      <div className="text-sm text-gray-400">Total Issues</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-red-400">{styleAnalysis.critical_issues}</div>
                      <div className="text-sm text-gray-400">Critical</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-orange-400">{styleAnalysis.high_issues}</div>
                      <div className="text-sm text-gray-400">High Priority</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-yellow-400">{styleAnalysis.medium_issues}</div>
                      <div className="text-sm text-gray-400">Medium</div>
                    </div>
                  </div>

                  <Alert className="border-blue-500/50 bg-blue-900/20">
                    <Lightbulb className="h-4 w-4 text-blue-400" />
                    <AlertTitle className="text-blue-300">Improvement Summary</AlertTitle>
                    <AlertDescription className="text-blue-200">
                      {styleAnalysis.improvement_summary}
                    </AlertDescription>
                  </Alert>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Issues Tab */}
          <TabsContent value="issues">
            <Card className="border-red-500/30 bg-slate-700/50">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-red-400" />
                  Detailed Style Issues
                </CardTitle>
                <CardDescription className="text-red-200">
                  Each issue includes explanation, examples, and specific improvement suggestions
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {styleAnalysis.issues.length === 0 ? (
                  <Alert className="border-green-500/50 bg-green-900/20">
                    <CheckCircle className="h-4 w-4 text-green-400" />
                    <AlertTitle className="text-green-300">Excellent Writing!</AlertTitle>
                    <AlertDescription className="text-green-200">
                      No significant style issues detected. Your writing demonstrates good clarity and engagement.
                    </AlertDescription>
                  </Alert>
                ) : (
                  styleAnalysis.issues.map((issue, index) => (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border ${getSeverityColor(issue.severity)} cursor-pointer transition-all`}
                      onClick={() => setSelectedIssue(selectedIssue === index ? null : index)}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          {getSeverityIcon(issue.severity)}
                          {getIssueTypeIcon(issue.type)}
                          <h4 className="font-semibold text-white">{issue.title}</h4>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {issue.severity.toUpperCase()}
                        </Badge>
                      </div>

                      <p className="text-gray-300 mb-3">{issue.explanation}</p>

                      {issue.problematic_text && (
                        <div className="mb-3 p-2 bg-slate-600/50 rounded border-l-4 border-red-400">
                          <div className="text-xs text-red-300 mb-1">Problematic Text:</div>
                          <div className="text-white text-sm font-mono">"{issue.problematic_text}"</div>
                        </div>
                      )}

                      {selectedIssue === index && (
                        <div className="mt-4 space-y-3 border-t border-slate-600 pt-3">
                          {/* Reasoning */}
                          <div>
                            <div className="text-sm font-medium text-yellow-400 mb-2 flex items-center gap-1">
                              <Brain className="w-3 h-3" />
                              Why This Matters:
                            </div>
                            <p className="text-yellow-200 text-sm">{issue.reasoning}</p>
                          </div>

                          {/* Suggested Revision */}
                          {issue.suggested_revision && (
                            <div className="p-2 bg-green-900/20 rounded border-l-4 border-green-400">
                              <div className="text-xs text-green-300 mb-1">Suggested Improvement:</div>
                              <div className="text-green-100 text-sm">{issue.suggested_revision}</div>
                            </div>
                          )}

                          {/* Examples */}
                          {issue.examples && (
                            <div className="space-y-2">
                              <div className="text-sm font-medium text-cyan-400">Examples:</div>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                {Object.entries(issue.examples).map(([key, value]) => (
                                  <div key={key} className="p-2 bg-slate-600/30 rounded">
                                    <div className="text-xs font-medium text-gray-400 capitalize mb-1">
                                      {key.replace('_', ' ')}:
                                    </div>
                                    <div className="text-white text-sm">"{value}"</div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Learning Resources */}
                          {issue.learning_resources && issue.learning_resources.length > 0 && (
                            <div>
                              <div className="text-sm font-medium text-indigo-400 mb-2 flex items-center gap-1">
                                <BookOpen className="w-3 h-3" />
                                Learn More:
                              </div>
                              <ul className="list-disc list-inside space-y-1">
                                {issue.learning_resources.map((resource, resourceIndex) => (
                                  <li key={resourceIndex} className="text-indigo-200 text-sm">{resource}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Education Tab */}
          <TabsContent value="education">
            <Card className="border-purple-500/30 bg-slate-700/50">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-purple-400" />
                  Writing Education
                </CardTitle>
                <CardDescription className="text-purple-200">
                  Learn about the style principles behind the analysis
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {styleAnalysis.educational_notes.map((note, index) => (
                  <Alert key={index} className="border-purple-500/50 bg-purple-900/20">
                    <BookOpen className="h-4 w-4 text-purple-400" />
                    <AlertDescription className="text-purple-200">
                      {note}
                    </AlertDescription>
                  </Alert>
                ))}

                {/* Additional Educational Resources */}
                {helpResources && helpResources.educational_resources && (
                  <div className="space-y-4">
                    <h4 className="text-white font-medium">Writing Principles</h4>
                    {Object.entries(helpResources.educational_resources).map(([category, resources]) => (
                      <div key={category} className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                        <h5 className="text-purple-300 font-medium mb-2 capitalize">
                          {category.replace('_', ' ')}
                        </h5>
                        <ul className="list-disc list-inside space-y-1">
                          {resources.map((resource, resourceIndex) => (
                            <li key={resourceIndex} className="text-purple-200 text-sm">{resource}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Strengths Tab */}
          <TabsContent value="strengths">
            <Card className="border-green-500/30 bg-slate-700/50">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  Writing Strengths
                </CardTitle>
                <CardDescription className="text-green-200">
                  Positive aspects of your writing to build upon
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {styleAnalysis.strengths.map((strength, index) => (
                  <Alert key={index} className="border-green-500/50 bg-green-900/20">
                    <CheckCircle className="h-4 w-4 text-green-400" />
                    <AlertDescription className="text-green-200">
                      {strength}
                    </AlertDescription>
                  </Alert>
                ))}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};

export default EnhancedStyleCoach;