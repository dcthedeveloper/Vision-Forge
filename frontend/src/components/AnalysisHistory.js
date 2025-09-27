import React, { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Skeleton } from "./ui/skeleton";
import { Separator } from "./ui/separator";
import { toast } from "sonner";
import { History, Calendar, Sparkles, Zap, RefreshCw } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AnalysisHistory = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalyses = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API}/analyses`);
      setAnalyses(response.data);
    } catch (error) {
      console.error("Failed to fetch analyses:", error);
      setError("Failed to load analysis history");
      toast.error("Failed to load analysis history");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-purple-400" />
            <h2 className="text-xl font-semibold text-white">Loading Analysis History...</h2>
          </div>
        </div>
        {[1, 2, 3].map((i) => (
          <Card key={i} className="visionforge-card">
            <CardHeader>
              <Skeleton className="h-6 w-48 bg-slate-700" />
              <Skeleton className="h-4 w-32 bg-slate-700" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-20 w-full bg-slate-700" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-400 mb-4">
          <History className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-semibold">{error}</p>
        </div>
        <Button 
          onClick={fetchAnalyses}
          className="btn-primary"
          data-testid="retry-button"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Try Again
        </Button>
      </div>
    );
  }

  if (analyses.length === 0) {
    return (
      <div className="text-center py-12">
        <History className="w-16 h-16 mx-auto mb-4 text-purple-400 opacity-50" />
        <h3 className="text-xl font-semibold text-white mb-2">No Analyses Yet</h3>
        <p className="text-purple-200 mb-6">
          Upload your first character image to start building your analysis history.
        </p>
        <Button 
          onClick={fetchAnalyses}
          variant="outline"
          className="border-purple-500/50 text-purple-300 hover:bg-purple-500/10"
          data-testid="refresh-button"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-purple-400" />
          <h2 className="text-xl font-semibold text-white">Analysis History</h2>
          <Badge variant="outline" className="text-purple-300 border-purple-500/50">
            {analyses.length} {analyses.length === 1 ? 'analysis' : 'analyses'}
          </Badge>
        </div>
        <Button 
          onClick={fetchAnalyses}
          variant="outline" 
          size="sm"
          className="border-purple-500/50 text-purple-300 hover:bg-purple-500/10"
          data-testid="refresh-history-button"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {analyses.map((analysis, index) => (
          <Card 
            key={analysis.id || index} 
            className="visionforge-card analysis-card"
            data-testid={`analysis-card-${index}`}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-purple-400" />
                    {analysis.image_name}
                  </CardTitle>
                  <CardDescription className="flex items-center gap-2 text-purple-200">
                    <Calendar className="w-4 h-4" />
                    {formatDate(analysis.created_at)}
                  </CardDescription>
                </div>
                <Badge className="bg-purple-500/20 text-purple-300 border-purple-500/30">
                  {analysis.mood}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Persona Summary */}
              <div className="bg-purple-900/20 rounded-lg p-4">
                <p className="text-purple-100 text-sm leading-relaxed">
                  {analysis.persona_summary}
                </p>
              </div>

              {/* Traits Summary */}
              <div>
                <h4 className="text-sm font-semibold text-purple-300 mb-2">
                  Character Traits ({analysis.traits.length})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {analysis.traits.slice(0, 6).map((trait, traitIndex) => (
                    <Badge 
                      key={traitIndex}
                      className={`text-xs ${getConfidenceColor(trait.confidence)}`}
                      data-testid={`history-trait-${traitIndex}`}
                    >
                      {trait.category}: {trait.trait.substring(0, 30)}
                      {trait.trait.length > 30 ? '...' : ''}
                    </Badge>
                  ))}
                  {analysis.traits.length > 6 && (
                    <Badge variant="outline" className="text-xs text-purple-300 border-purple-500/50">
                      +{analysis.traits.length - 6} more
                    </Badge>
                  )}
                </div>
              </div>

              <Separator className="bg-purple-500/20" />

              {/* Backstory Seeds */}
              <div>
                <h4 className="text-sm font-semibold text-purple-300 mb-2">
                  Backstory Seeds ({analysis.backstory_seeds.length})
                </h4>
                <div className="space-y-1">
                  {analysis.backstory_seeds.slice(0, 2).map((seed, seedIndex) => (
                    <p 
                      key={seedIndex} 
                      className="text-xs text-slate-300 bg-slate-700/30 rounded px-2 py-1"
                      data-testid={`history-backstory-${seedIndex}`}
                    >
                      {seed}
                    </p>
                  ))}
                  {analysis.backstory_seeds.length > 2 && (
                    <p className="text-xs text-purple-300">
                      +{analysis.backstory_seeds.length - 2} more backstory seeds
                    </p>
                  )}
                </div>
              </div>

              {/* Power Suggestions */}
              <div>
                <h4 className="text-sm font-semibold text-purple-300 mb-2 flex items-center gap-1">
                  <Zap className="w-4 h-4" />
                  Power Suggestions ({analysis.power_suggestions.length})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {analysis.power_suggestions.map((power, powerIndex) => (
                    <Badge 
                      key={powerIndex}
                      className={`text-xs ${getCostLevelColor(power.cost_level)}`}
                      data-testid={`history-power-${powerIndex}`}
                    >
                      {power.name} (Cost: {power.cost_level}/10)
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default AnalysisHistory;