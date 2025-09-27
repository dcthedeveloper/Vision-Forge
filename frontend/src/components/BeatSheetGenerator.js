import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { toast } from 'sonner';
import { Loader2, FileText, Zap, BookOpen, Clock } from 'lucide-react';

const BeatSheetGenerator = () => {
  const [beatSheetTypes, setBeatSheetTypes] = useState([]);
  const [tonePacing, setTonePacing] = useState([]);
  const [selectedSheetType, setSelectedSheetType] = useState('');
  const [selectedTonePacing, setSelectedTonePacing] = useState('');
  const [storyLength, setStoryLength] = useState(110);
  const [characterData, setCharacterData] = useState(null);
  const [generatedBeatSheet, setGeneratedBeatSheet] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [analysisHistory, setAnalysisHistory] = useState([]);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchBeatSheetTypes();
    fetchAnalysisHistory();
  }, []);

  const fetchBeatSheetTypes = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/beat-sheet-types`);
      const data = await response.json();
      setBeatSheetTypes(data.sheet_types || []);
      setTonePacing(data.tone_pacing || []);
      
      // Set defaults
      if (data.sheet_types?.length > 0) {
        setSelectedSheetType(data.sheet_types[0].value);
      }
      if (data.tone_pacing?.length > 0) {
        setSelectedTonePacing(data.tone_pacing[1].value); // Default to "standard"
      }
    } catch (error) {
      console.error('Failed to fetch beat sheet types:', error);
      toast.error('Failed to load beat sheet options');
    }
  };

  const fetchAnalysisHistory = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/analyses`);
      const data = await response.json();
      setAnalysisHistory(data || []);
    } catch (error) {
      console.error('Failed to fetch analysis history:', error);
    }
  };

  const generateBeatSheet = async () => {
    if (!selectedSheetType) {
      toast.error('Please select a beat sheet type');
      return;
    }

    if (!selectedTonePacing) {
      toast.error('Please select tone/pacing');
      return;
    }

    setIsLoading(true);
    try {
      const requestData = {
        sheet_type: selectedSheetType,
        tone_pacing: selectedTonePacing,
        story_length: parseInt(storyLength),
        character_data: characterData
      };

      const response = await fetch(`${backendUrl}/api/generate-beat-sheet`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      if (data.success) {
        setGeneratedBeatSheet(data.beat_sheet);
        toast.success('Beat sheet generated successfully!');
      } else {
        throw new Error(data.message || 'Failed to generate beat sheet');
      }
    } catch (error) {
      console.error('Beat sheet generation failed:', error);
      toast.error('Failed to generate beat sheet: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const selectCharacterFromHistory = (analysis) => {
    const characterData = {
      id: analysis.id,
      character_origin: analysis.character_origin || 'unknown',
      power_source: analysis.power_source || 'unknown',
      social_status: analysis.social_status || 'unknown',
      archetype_tags: analysis.archetype_tags || [],
      genre_universe: analysis.genre || 'urban_realistic',
      traits: analysis.traits || [],
      backstory_seeds: analysis.backstory_seeds || [],
      power_suggestions: analysis.power_suggestions || []
    };
    
    setCharacterData(characterData);
    toast.success(`Selected character: ${analysis.persona_summary?.substring(0, 50) || 'Character'}...`);
  };

  const getFreshnessIcon = (freshnessLevel) => {
    switch (freshnessLevel) {
      case 'groundbreaking':
        return <Zap className="w-4 h-4 text-yellow-400" />;
      case 'fresh':
        return <BookOpen className="w-4 h-4 text-green-400" />;
      case 'familiar':
        return <Clock className="w-4 h-4 text-blue-400" />;
      default:
        return <FileText className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Configuration Panel */}
      <Card className="border-indigo-500/30 bg-slate-700/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Beat Sheet Configuration
          </CardTitle>
          <CardDescription className="text-indigo-200">
            Configure your story structure and optional character integration
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="sheet-type" className="text-white">Beat Sheet Type</Label>
              <Select value={selectedSheetType} onValueChange={setSelectedSheetType}>
                <SelectTrigger className="bg-slate-600 border-slate-500 text-white">
                  <SelectValue placeholder="Select structure..." />
                </SelectTrigger>
                <SelectContent>
                  {beatSheetTypes.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      <div className="space-y-1">
                        <div className="font-medium">{type.name}</div>
                        <div className="text-xs text-gray-400">{type.description}</div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="tone-pacing" className="text-white">Tone & Pacing</Label>
              <Select value={selectedTonePacing} onValueChange={setSelectedTonePacing}>
                <SelectTrigger className="bg-slate-600 border-slate-500 text-white">
                  <SelectValue placeholder="Select pacing..." />
                </SelectTrigger>
                <SelectContent>
                  {tonePacing.map((tone) => (
                    <SelectItem key={tone.value} value={tone.value}>
                      <div className="space-y-1">
                        <div className="font-medium">{tone.name}</div>
                        <div className="text-xs text-gray-400">{tone.description}</div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="story-length" className="text-white">Story Length (pages)</Label>
              <Input
                id="story-length"
                type="number"
                value={storyLength}
                onChange={(e) => setStoryLength(e.target.value)}
                min="80"
                max="200"
                className="bg-slate-600 border-slate-500 text-white"
              />
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 items-center">
            {characterData && (
              <div className="flex-1 p-3 bg-slate-600/50 rounded-lg border border-indigo-500/30">
                <div className="text-sm text-indigo-200">
                  <strong>Selected Character:</strong> {characterData.character_origin} • {characterData.power_source}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {characterData.archetype_tags?.join(', ') || 'No tags'}
                </div>
              </div>
            )}
            
            <Button
              onClick={generateBeatSheet}
              disabled={isLoading || !selectedSheetType || !selectedTonePacing}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Generate Beat Sheet
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Character Selection Panel */}
      {analysisHistory.length > 0 && (
        <Card className="border-indigo-500/30 bg-slate-700/50">
          <CardHeader>
            <CardTitle className="text-white">Select Character (Optional)</CardTitle>
            <CardDescription className="text-indigo-200">
              Choose a character from your analysis history to customize the beat sheet
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-60 overflow-y-auto">
              {analysisHistory.slice(0, 9).map((analysis, index) => (
                <div
                  key={index}
                  onClick={() => selectCharacterFromHistory(analysis)}
                  className="p-3 bg-slate-600/50 rounded-lg border border-slate-500 hover:border-indigo-400 cursor-pointer transition-colors"
                >
                  <div className="text-sm font-medium text-white truncate">
                    {analysis.persona_summary?.substring(0, 40) || 'Unnamed Character'}...
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {analysis.character_origin} • {analysis.traits?.length || 0} traits
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Generated Beat Sheet Display */}
      {generatedBeatSheet && (
        <Card className="border-indigo-500/30 bg-slate-700/50">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <FileText className="w-5 h-5" />
              {generatedBeatSheet.title}
            </CardTitle>
            <CardDescription className="text-indigo-200">
              {generatedBeatSheet.description} • {generatedBeatSheet.total_beats} beats • {generatedBeatSheet.estimated_pages} pages
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Beat Sheet Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-slate-600/30 rounded-lg">
              <div className="text-center">
                <div className="text-2xl font-bold text-white">{generatedBeatSheet.total_beats}</div>
                <div className="text-sm text-gray-400">Total Beats</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-white">{generatedBeatSheet.estimated_pages}</div>
                <div className="text-sm text-gray-400">Estimated Pages</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-400 capitalize">{generatedBeatSheet.tone_pacing}</div>
                <div className="text-sm text-gray-400">Pacing</div>
              </div>
            </div>

            {/* Beats List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-white">Story Beats</h3>
              {generatedBeatSheet.beats?.map((beat, index) => (
                <div key={index} className="p-4 bg-slate-600/30 rounded-lg border border-slate-500">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                        {beat.beat_number}
                      </span>
                      <h4 className="font-semibold text-white">{beat.beat_name}</h4>
                    </div>
                    <div className="text-xs text-gray-400">
                      Pages {beat.page_range} • {Math.round(beat.percentage * 100)}%
                    </div>
                  </div>
                  
                  <div className="text-gray-300 mb-2">
                    {beat.description}
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-indigo-400 font-medium">Character Focus:</span>
                      <span className="text-gray-400 ml-1">{beat.character_focus}</span>
                    </div>
                    <div>
                      <span className="text-indigo-400 font-medium">Plot Function:</span>
                      <span className="text-gray-400 ml-1">{beat.plot_function}</span>
                    </div>
                  </div>
                  
                  {beat.tone_notes && (
                    <div className="mt-2 text-xs">
                      <span className="text-indigo-400 font-medium">Tone Notes:</span>
                      <span className="text-gray-400 ml-1">{beat.tone_notes}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Integration Notes */}
            {generatedBeatSheet.character_integration_notes?.length > 0 && (
              <div className="mt-6 p-4 bg-indigo-900/20 rounded-lg border border-indigo-500/30">
                <h3 className="text-lg font-semibold text-white mb-2">Character Integration Notes</h3>
                <ul className="list-disc list-inside space-y-1">
                  {generatedBeatSheet.character_integration_notes.map((note, index) => (
                    <li key={index} className="text-indigo-200 text-sm">{note}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Marcus Adaptations */}
            {generatedBeatSheet.marcus_adaptations?.length > 0 && (
              <div className="mt-4 p-4 bg-yellow-900/20 rounded-lg border border-yellow-500/30">
                <h3 className="text-lg font-semibold text-white mb-2">Sophisticated Character Adaptations</h3>
                <ul className="list-disc list-inside space-y-1">
                  {generatedBeatSheet.marcus_adaptations.map((adaptation, index) => (
                    <li key={index} className="text-yellow-200 text-sm">{adaptation}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default BeatSheetGenerator;