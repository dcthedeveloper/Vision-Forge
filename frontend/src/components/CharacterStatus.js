import React from 'react';
import { useCharacter } from '../contexts/CharacterContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { User, History, RefreshCw, X } from 'lucide-react';

const CharacterStatus = ({ showHistory = false }) => {
  const { 
    currentCharacter, 
    hasActiveCharacter, 
    getCharacterName, 
    getCharacterSummary, 
    clearCharacter,
    loadCurrentCharacter,
    isLoading 
  } = useCharacter();

  if (!hasActiveCharacter) {
    return (
      <Card className="border-slate-600/20 bg-slate-800/30 backdrop-blur-sm mb-4">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium text-slate-300 flex items-center gap-2">
            <User className="h-4 w-4" />
            No Active Character
          </CardTitle>
          <CardDescription className="text-xs text-slate-400">
            Analyze an image to create a character that persists across all tools
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card className="border-indigo-500/30 bg-indigo-900/20 backdrop-blur-sm mb-4">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-indigo-400" />
            <CardTitle className="text-sm font-medium text-white">
              Active Character: {getCharacterName()}
            </CardTitle>
          </div>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={loadCurrentCharacter}
              disabled={isLoading}
              className="h-6 w-6 p-0 text-slate-400 hover:text-white"
            >
              <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearCharacter}
              className="h-6 w-6 p-0 text-slate-400 hover:text-red-400"
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        </div>
        <CardDescription className="text-xs text-indigo-200">
          {getCharacterSummary()}
        </CardDescription>
      </CardHeader>
      
      {currentCharacter && (
        <CardContent className="pt-0">
          <div className="flex flex-wrap gap-1">
            {/* Show basic character info as badges */}
            {currentCharacter.genre_universe && (
              <Badge variant="secondary" className="text-xs">
                {currentCharacter.genre_universe}
              </Badge>
            )}
            {currentCharacter.character_origin && (
              <Badge variant="outline" className="text-xs">
                {currentCharacter.character_origin}
              </Badge>
            )}
            {currentCharacter.social_status && (
              <Badge variant="outline" className="text-xs">
                {currentCharacter.social_status.replace('_', ' ')}
              </Badge>
            )}
            {currentCharacter.power_source && (
              <Badge variant="outline" className="text-xs">
                {currentCharacter.power_source.replace('_', ' ')}
              </Badge>
            )}
          </div>
          
          {/* Show character traits if available */}
          {currentCharacter.traits && currentCharacter.traits.length > 0 && (
            <div className="mt-3">
              <h4 className="text-xs font-medium text-slate-300 mb-1">Key Traits:</h4>
              <div className="text-xs text-slate-400 space-y-1">
                {currentCharacter.traits.slice(0, 2).map((trait, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span className="text-indigo-300 font-medium">{trait.category}:</span>
                    <span className="truncate">{trait.trait}</span>
                  </div>
                ))}
                {currentCharacter.traits.length > 2 && (
                  <div className="text-slate-500">
                    +{currentCharacter.traits.length - 2} more traits
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* Show character mood/summary if available */}
          {currentCharacter.mood && (
            <div className="mt-3">
              <h4 className="text-xs font-medium text-slate-300 mb-1">Mood:</h4>
              <p className="text-xs text-slate-400 line-clamp-2">
                {currentCharacter.mood}
              </p>
            </div>
          )}
          
          {showHistory && (
            <div className="mt-3 pt-3 border-t border-slate-600/20">
              <Button
                variant="ghost"
                size="sm"
                className="text-xs text-slate-400 hover:text-white p-0 h-auto"
              >
                <History className="h-3 w-3 mr-1" />
                View Character History
              </Button>
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
};

export default CharacterStatus;