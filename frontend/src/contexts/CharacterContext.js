import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';

const CharacterContext = createContext();

export const useCharacter = () => {
  const context = useContext(CharacterContext);
  if (!context) {
    throw new Error('useCharacter must be used within a CharacterProvider');
  }
  return context;
};

export const CharacterProvider = ({ children }) => {
  const [currentCharacter, setCurrentCharacter] = useState(null);
  const [characterHistory, setCharacterHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasActiveCharacter, setHasActiveCharacter] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  // Load current character on mount
  useEffect(() => {
    loadCurrentCharacter();
  }, []);

  const loadCurrentCharacter = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${backendUrl}/api/character/current`);
      const data = await response.json();
      
      if (data.success && data.character) {
        setCurrentCharacter(data.character);
        setHasActiveCharacter(true);
        console.log('✅ Loaded current character:', data.character.id || 'Unknown ID');
      } else {
        setCurrentCharacter(null);
        setHasActiveCharacter(false);
        console.log('ℹ️ No active character session');
      }
    } catch (error) {
      console.error('Failed to load current character:', error);
      setCurrentCharacter(null);
      setHasActiveCharacter(false);
    } finally {
      setIsLoading(false);
    }
  }, [backendUrl]);

  const saveCharacter = useCallback(async (characterData, promptContext, toolName, description = 'Character update') => {
    try {
      setIsLoading(true);
      
      const requestData = {
        character_data: characterData,
        prompt_context: promptContext,
        tool_name: toolName,
        description: description
      };

      const response = await fetch(`${backendUrl}/api/character/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      if (data.success) {
        setCurrentCharacter(characterData);
        setHasActiveCharacter(true);
        console.log('✅ Character saved to session:', data.character_id);
        toast.success('Character saved to session');
        return data;
      } else {
        throw new Error(data.message || 'Failed to save character');
      }
    } catch (error) {
      console.error('Failed to save character:', error);
      toast.error('Failed to save character: ' + error.message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [backendUrl]);

  const updateCharacter = useCallback(async (characterData, toolName, description = 'Character modification') => {
    try {
      setIsLoading(true);
      
      const requestData = {
        character_data: characterData,
        tool_name: toolName,
        description: description
      };

      const response = await fetch(`${backendUrl}/api/character/update`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      if (data.success) {
        setCurrentCharacter(characterData);
        console.log('✅ Character updated from:', toolName);
        toast.success(`Character updated from ${toolName}`);
        return data;
      } else {
        throw new Error(data.message || 'Failed to update character');
      }
    } catch (error) {
      console.error('Failed to update character:', error);
      toast.error('Failed to update character: ' + error.message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [backendUrl]);

  const getCharacterHistory = useCallback(async (characterId) => {
    try {
      const response = await fetch(`${backendUrl}/api/character/history/${characterId}`);
      const data = await response.json();
      
      if (data.success) {
        setCharacterHistory(data.lineage);
        return data.lineage;
      } else {
        throw new Error(data.message || 'Failed to get character history');
      }
    } catch (error) {
      console.error('Failed to get character history:', error);
      toast.error('Failed to load character history');
      throw error;
    }
  }, [backendUrl]);

  const rollbackCharacter = useCallback(async (characterId, versionId) => {
    try {
      setIsLoading(true);
      
      const response = await fetch(`${backendUrl}/api/character/rollback/${characterId}/${versionId}`, {
        method: 'POST',
      });

      const data = await response.json();

      if (data.success) {
        setCurrentCharacter(data.character_data);
        toast.success('Character rolled back successfully');
        return data;
      } else {
        throw new Error(data.message || 'Failed to rollback character');
      }
    } catch (error) {
      console.error('Failed to rollback character:', error);
      toast.error('Failed to rollback character: ' + error.message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [backendUrl]);

  const clearCharacter = useCallback(() => {
    setCurrentCharacter(null);
    setHasActiveCharacter(false);
    setCharacterHistory([]);
    console.log('🗑️ Character session cleared');
  }, []);

  // Helper function to get character name
  const getCharacterName = useCallback(() => {
    if (!currentCharacter) return 'No Character';
    return currentCharacter.name || 
           currentCharacter.image_name || 
           `Character ${currentCharacter.id?.slice(0, 8) || 'Unknown'}`;
  }, [currentCharacter]);

  // Helper function to get character summary
  const getCharacterSummary = useCallback(() => {
    if (!currentCharacter) return 'No active character';
    
    const origin = currentCharacter.character_origin || currentCharacter.origin || 'Unknown origin';
    const genre = currentCharacter.genre_universe || currentCharacter.genre || 'Unknown universe';
    
    return `${origin} character in ${genre}`;
  }, [currentCharacter]);

  const contextValue = {
    // State
    currentCharacter,
    characterHistory,
    isLoading,
    hasActiveCharacter,
    
    // Actions
    loadCurrentCharacter,
    saveCharacter,
    updateCharacter,
    getCharacterHistory,
    rollbackCharacter,
    clearCharacter,
    
    // Helpers
    getCharacterName,
    getCharacterSummary,
  };

  return (
    <CharacterContext.Provider value={contextValue}>
      {children}
    </CharacterContext.Provider>
  );
};

export default CharacterProvider;