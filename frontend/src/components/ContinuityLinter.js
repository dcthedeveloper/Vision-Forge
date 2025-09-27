import React, { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { Alert, AlertDescription } from "./ui/alert";
import { toast } from "sonner";
import { 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  Info,
  Lightbulb,
  Zap,
  Brain,
  Shield
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ContinuityLinter = ({ characterId, characterData, onViolationsUpdate }) => {
  const [ruleEngineStatus, setRuleEngineStatus] = useState(null);
  const [violations, setViolations] = useState([]);
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    fetchRuleEngineStatus();
  }, []);

  const fetchRuleEngineStatus = async () => {
    try {
      const response = await axios.get(`${API}/rule-engine/status`);
      setRuleEngineStatus(response.data);
    } catch (error) {
      console.error("Failed to fetch rule engine status:", error);
    }
  };

  const runContinuityCheck = async () => {
    if (!characterId || !characterData) {
      toast.error("No character data available for checking");
      return;
    }

    setChecking(true);
    try {
      const response = await axios.post(`${API}/check-continuity`, {
        character_id: characterId,
        content: characterData.persona_summary || "",
        content_type: "character_update",
        character_data: characterData
      });

      const allViolations = [
        ...response.data.continuity_conflicts.map(c => ({...c, type: "continuity"})),
        ...response.data.style_violations.map(s => ({...s, type: "style"})),
        ...response.data.character_violations.map(cr => ({...cr, type: "character"}))
      ];

      setViolations(allViolations);
      onViolationsUpdate?.(allViolations);
      
      if (allViolations.length === 0) {
        toast.success("No rule violations detected! Character follows best practices.");
      } else {
        toast.warning(`Found ${allViolations.length} issues to review`);
      }
    } catch (error) {
      console.error("Continuity check failed:", error);
      toast.error("Failed to run continuity check");
    } finally {
      setChecking(false);
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case "error":
      case "critical":
        return <XCircle className="w-4 h-4 text-red-400" />;
      case "warning":
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case "info":
        return <Info className="w-4 h-4 text-blue-400" />;
      default:
        return <CheckCircle className="w-4 h-4 text-green-400" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "error":
      case "critical":
        return "border-red-500/50 bg-red-900/20";
      case "warning":
        return "border-yellow-500/50 bg-yellow-900/20";
      case "info":
        return "border-blue-500/50 bg-blue-900/20";
      default:
        return "border-green-500/50 bg-green-900/20";
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case "continuity":
        return <Shield className="w-4 h-4 text-purple-400" />;
      case "style":
        return <Brain className="w-4 h-4 text-indigo-400" />;
      case "character":
        return <Zap className="w-4 h-4 text-orange-400" />;
      default:
        return <CheckCircle className="w-4 h-4 text-green-400" />;
    }
  };

  return (
    <Card className="visionforge-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <Shield className="w-5 h-5 text-purple-400" />
          Continuity Linter & Rule Engine
        </CardTitle>
        <CardDescription className="text-indigo-200">
          Real-time character consistency and rule violation checking
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Rule Engine Status */}
        {ruleEngineStatus && (
          <Alert className="border-green-500/50 bg-green-900/20">
            <CheckCircle className="w-4 h-4 text-green-400" />
            <AlertDescription className="text-green-300">
              <strong>Rule Engine Active:</strong> {ruleEngineStatus.rule_summary.character_rules} character rules, 
              {ruleEngineStatus.rule_summary.style_rules} style rules loaded
            </AlertDescription>
          </Alert>
        )}

        {/* Run Check Button */}
        <Button
          onClick={runContinuityCheck}
          disabled={!characterId || checking}
          className="w-full btn-primary"
          data-testid="run-continuity-check"
        >
          {checking ? (
            <>
              <Shield className="w-4 h-4 mr-2 animate-spin" />
              Checking Rules...
            </>
          ) : (
            <>
              <Shield className="w-4 h-4 mr-2" />
              Run Continuity & Rule Check
            </>
          )}
        </Button>

        {/* Violations Display */}
        {violations.length > 0 && (
          <div className="space-y-4">
            <Separator className="bg-indigo-500/30" />
            
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold text-white">Rule Violations Found</h4>
              <Badge variant="outline" className="text-yellow-300 border-yellow-500/50">
                {violations.length} {violations.length === 1 ? 'issue' : 'issues'}
              </Badge>
            </div>

            <div className="space-y-3">
              {violations.map((violation, index) => (
                <div 
                  key={index}
                  className={`rounded-lg border p-4 ${getSeverityColor(violation.severity)}`}
                  data-testid={`violation-${index}`}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex items-center gap-2 mt-1">
                      {getSeverityIcon(violation.severity)}
                      {getTypeIcon(violation.type)}
                    </div>
                    
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center justify-between">
                        <h5 className="font-semibold text-white">
                          {violation.rule_name || violation.conflict_type}
                        </h5>
                        <Badge 
                          className={`text-xs ${
                            violation.type === 'continuity' ? 'bg-purple-500/20 text-purple-300' :
                            violation.type === 'style' ? 'bg-indigo-500/20 text-indigo-300' :
                            'bg-orange-500/20 text-orange-300'
                          }`}
                        >
                          {violation.type}
                        </Badge>
                      </div>
                      
                      <p className="text-slate-300 text-sm">
                        {violation.message}
                      </p>
                      
                      {violation.explanation && (
                        <div className="bg-slate-800/50 rounded p-3">
                          <p className="text-xs text-slate-400 mb-2">
                            <strong>Why this matters:</strong>
                          </p>
                          <p className="text-xs text-slate-300">
                            {violation.explanation}
                          </p>
                        </div>
                      )}
                      
                      {violation.quick_fix && (
                        <div className="flex items-start gap-2 bg-green-900/20 rounded p-3">
                          <Lightbulb className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-xs text-green-300 font-medium mb-1">Quick Fix:</p>
                            <p className="text-xs text-green-200">
                              {violation.quick_fix}
                            </p>
                          </div>
                        </div>
                      )}
                      
                      {violation.suggested_replacement && (
                        <div className="bg-blue-900/20 rounded p-3">
                          <p className="text-xs text-blue-300 font-medium mb-1">Suggested Alternative:</p>
                          <p className="text-xs text-blue-200 font-mono">
                            {violation.suggested_replacement}
                          </p>
                        </div>
                      )}
                      
                      {violation.similarity_score && (
                        <p className="text-xs text-slate-400">
                          Similarity: {Math.round(violation.similarity_score * 100)}%
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Violations State */}
        {violations.length === 0 && characterId && (
          <Alert className="border-green-500/50 bg-green-900/20">
            <CheckCircle className="w-4 h-4 text-green-400" />
            <AlertDescription className="text-green-300">
              <strong>Character Passes All Checks:</strong> No rule violations or continuity conflicts detected. 
              This character follows Marcus-style best practices for realistic, sophisticated character creation.
            </AlertDescription>
          </Alert>
        )}

        {/* System Capabilities */}
        {ruleEngineStatus && (
          <div className="bg-slate-700/30 rounded-lg p-4 mt-4">
            <h5 className="text-sm font-medium text-indigo-300 mb-3">Active Rule Capabilities:</h5>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {ruleEngineStatus.capabilities.map((capability, index) => (
                <div key={index} className="flex items-center gap-2 text-slate-300">
                  <CheckCircle className="w-3 h-3 text-green-400" />
                  {capability}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ContinuityLinter;