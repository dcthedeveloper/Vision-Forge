import React, { useState } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Slider } from "./ui/slider";
import { Separator } from "./ui/separator";
import { toast } from "sonner";
import { 
  Crown, 
  Sword, 
  Shield, 
  Zap, 
  Heart, 
  Brain,
  Star,
  Shuffle,
  Plus,
  Minus,
  RotateCcw
} from "lucide-react";

const TropeBuilder = () => {
  const [selectedArchetypes, setSelectedArchetypes] = useState([]);
  const [selectedOrigins, setSelectedOrigins] = useState([]);
  const [customPowers, setCustomPowers] = useState([]);
  const [powerCosts, setPowerCosts] = useState({});

  const archetypes = [
    {
      id: "hero",
      name: "The Hero",
      icon: Crown,
      description: "Noble, brave, destined for greatness",
      clicheRisk: 0.8,
      subversions: ["Reluctant hero", "Fallen hero", "Hero by accident"]
    },
    {
      id: "mentor",
      name: "The Mentor", 
      icon: Brain,
      description: "Wise teacher, guides others",
      clicheRisk: 0.6,
      subversions: ["False mentor", "Learning mentor", "Rival mentor"]
    },
    {
      id: "trickster",
      name: "The Trickster",
      icon: Star,
      description: "Clever, unpredictable, rule-breaker",
      clicheRisk: 0.3,
      subversions: ["Noble trickster", "Tragic trickster", "Reformed trickster"]
    },
    {
      id: "guardian",
      name: "The Guardian",
      icon: Shield,
      description: "Protector, loyal, sacrificial",
      clicheRisk: 0.5,
      subversions: ["Conflicted guardian", "Guardian turned enemy", "Reluctant guardian"]
    },
    {
      id: "lover",
      name: "The Lover",
      icon: Heart,
      description: "Passionate, devoted, emotional",
      clicheRisk: 0.7,
      subversions: ["Forbidden lover", "Lost lover", "Dangerous lover"]
    },
    {
      id: "rebel",
      name: "The Rebel",
      icon: Sword,
      description: "Revolutionary, defiant, outcast",
      clicheRisk: 0.4,
      subversions: ["Noble rebel", "Misguided rebel", "Accidental rebel"]
    }
  ];

  const origins = [
    {
      id: "royalty",
      name: "Royal Bloodline",
      description: "Born into nobility and power",
      clicheRisk: 0.9,
      twist: "Unknown royal heritage"
    },
    {
      id: "commoner",
      name: "Common Folk",
      description: "Ordinary background, extraordinary circumstances",
      clicheRisk: 0.3,
      twist: "Hidden extraordinary lineage"
    },
    {
      id: "exile",
      name: "Exiled Outcast", 
      description: "Banished from their homeland",
      clicheRisk: 0.6,
      twist: "Self-imposed exile for protection"
    },
    {
      id: "prodigy",
      name: "Child Prodigy",
      description: "Exceptional abilities from a young age",
      clicheRisk: 0.7,
      twist: "Powers come with a terrible cost"
    },
    {
      id: "survivor",
      name: "Lone Survivor",
      description: "Only one left from their group/family",
      clicheRisk: 0.8,
      twist: "Survival wasn't by chance"
    },
    {
      id: "created",
      name: "Artificially Created",
      description: "Made, not born - magical or technological origin",
      clicheRisk: 0.4,
      twist: "Creator had hidden motives"
    }
  ];

  const powerTemplates = [
    {
      name: "Elemental Control",
      description: "Manipulate fire, water, air, or earth",
      baseCost: 6,
      limitations: ["Emotional state affects control", "Requires environmental source"]
    },
    {
      name: "Telepathy",
      description: "Read minds and communicate mentally",
      baseCost: 7,
      limitations: ["Constant mental noise", "Invasive thoughts"]
    },
    {
      name: "Enhanced Physique",
      description: "Superior strength, speed, or agility", 
      baseCost: 4,
      limitations: ["Increased caloric needs", "Wear and tear on body"]
    },
    {
      name: "Precognition",
      description: "See glimpses of possible futures",
      baseCost: 8,
      limitations: ["Visions are unreliable", "Causes severe headaches"]
    },
    {
      name: "Shapeshifting",
      description: "Change physical form at will",
      baseCost: 7,
      limitations: ["Risk of losing original form", "Painful transformation"]
    },
    {
      name: "Time Manipulation",
      description: "Slow, stop, or reverse time in small areas",
      baseCost: 9,
      limitations: ["Extreme energy drain", "Temporal backlash"]
    }
  ];

  const handleArchetypeToggle = (archetype) => {
    setSelectedArchetypes(prev => 
      prev.find(a => a.id === archetype.id)
        ? prev.filter(a => a.id !== archetype.id)
        : [...prev, archetype]
    );
  };

  const handleOriginToggle = (origin) => {
    setSelectedOrigins(prev =>
      prev.find(o => o.id === origin.id)
        ? prev.filter(o => o.id !== origin.id)
        : [...prev, origin]
    );
  };

  const addCustomPower = (powerTemplate) => {
    const newPower = {
      id: Date.now(),
      ...powerTemplate,
      cost: powerTemplate.baseCost
    };
    setCustomPowers(prev => [...prev, newPower]);
    setPowerCosts(prev => ({
      ...prev,
      [newPower.id]: powerTemplate.baseCost
    }));
    toast.success(`Added ${powerTemplate.name}`);
  };

  const removePower = (powerId) => {
    setCustomPowers(prev => prev.filter(p => p.id !== powerId));
    setPowerCosts(prev => {
      const newCosts = { ...prev };
      delete newCosts[powerId];
      return newCosts;
    });
  };

  const updatePowerCost = (powerId, newCost) => {
    setPowerCosts(prev => ({
      ...prev,
      [powerId]: newCost
    }));
  };

  const generateRandomBuild = () => {
    // Select 1-2 random archetypes
    const shuffledArchetypes = [...archetypes].sort(() => 0.5 - Math.random());
    const numArchetypes = Math.random() < 0.7 ? 1 : 2;
    setSelectedArchetypes(shuffledArchetypes.slice(0, numArchetypes));

    // Select 1 random origin
    const randomOrigin = origins[Math.floor(Math.random() * origins.length)];
    setSelectedOrigins([randomOrigin]);

    // Add 1-3 random powers
    const shuffledPowers = [...powerTemplates].sort(() => 0.5 - Math.random());
    const numPowers = Math.floor(Math.random() * 3) + 1;
    const selectedPowers = shuffledPowers.slice(0, numPowers).map(power => ({
      id: Date.now() + Math.random(),
      ...power,
      cost: power.baseCost + Math.floor(Math.random() * 3) - 1 // ±1 variation
    }));
    
    setCustomPowers(selectedPowers);
    
    const newPowerCosts = {};
    selectedPowers.forEach(power => {
      newPowerCosts[power.id] = power.cost;
    });
    setPowerCosts(newPowerCosts);

    toast.success("Random character build generated!");
  };

  const resetBuild = () => {
    setSelectedArchetypes([]);
    setSelectedOrigins([]);
    setCustomPowers([]);
    setPowerCosts({});
    toast.success("Character build reset!");
  };

  const calculateClicheRisk = () => {
    const archetypeRisk = selectedArchetypes.reduce((sum, arch) => sum + arch.clicheRisk, 0) / Math.max(selectedArchetypes.length, 1);
    const originRisk = selectedOrigins.reduce((sum, orig) => sum + orig.clicheRisk, 0) / Math.max(selectedOrigins.length, 1);
    const powerCount = customPowers.length;
    const powerRisk = powerCount > 3 ? 0.3 : powerCount < 1 ? 0.1 : 0.0;
    
    return Math.min((archetypeRisk + originRisk + powerRisk) / 3, 1);
  };

  const getClicheColor = (risk) => {
    if (risk < 0.3) return "text-green-400";
    if (risk < 0.6) return "text-yellow-400";
    return "text-red-400";
  };

  const getClicheLabel = (risk) => {
    if (risk < 0.3) return "Fresh & Original";
    if (risk < 0.6) return "Somewhat Familiar";
    return "High Cliché Risk";
  };

  const clicheRisk = calculateClicheRisk();
  const totalPowerCost = customPowers.reduce((sum, power) => sum + (powerCosts[power.id] || power.cost), 0);

  return (
    <div className="space-y-6">
      {/* Control Panel */}
      <Card className="visionforge-card">
        <CardHeader>
          <CardTitle className="flex items-center justify-between text-white">
            <div className="flex items-center gap-2">
              <Star className="w-5 h-5 text-indigo-400" />
              Character Builder
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={generateRandomBuild}
                className="border-indigo-500/50 text-indigo-300 hover:bg-indigo-500/10"
                data-testid="random-build-button"
              >
                <Shuffle className="w-4 h-4 mr-1" />
                Random
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={resetBuild}
                className="border-slate-500/50 text-slate-300 hover:bg-slate-500/10"
                data-testid="reset-build-button"
              >
                <RotateCcw className="w-4 h-4 mr-1" />
                Reset
              </Button>
            </div>
          </CardTitle>
          <CardDescription className="text-indigo-200">
            Mix archetypes, origins, and powers to create unique characters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{selectedArchetypes.length}</div>
              <div className="text-sm text-slate-400">Archetypes</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{selectedOrigins.length}</div>
              <div className="text-sm text-slate-400">Origins</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{customPowers.length}</div>
              <div className="text-sm text-slate-400">Powers</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Cliché Risk Assessment */}
      {(selectedArchetypes.length > 0 || selectedOrigins.length > 0 || customPowers.length > 0) && (
        <Card className="visionforge-card" data-testid="cliche-assessment">
          <CardHeader>
            <CardTitle className="flex items-center justify-between text-white">
              <span>Originality Assessment</span>
              <Badge className={`${getClicheColor(clicheRisk)} bg-slate-800 border-slate-600`}>
                {getClicheLabel(clicheRisk)}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Cliché Risk</span>
                <span className={getClicheColor(clicheRisk)}>
                  {Math.round(clicheRisk * 100)}%
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${
                    clicheRisk < 0.3 ? 'bg-green-500' :
                    clicheRisk < 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${clicheRisk * 100}%` }}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Archetypes */}
      <Card className="visionforge-card">
        <CardHeader>
          <CardTitle className="text-white">Character Archetypes</CardTitle>
          <CardDescription className="text-indigo-200">
            Select personality types and roles (mix multiple for complexity)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {archetypes.map((archetype) => {
              const isSelected = selectedArchetypes.find(a => a.id === archetype.id);
              const IconComponent = archetype.icon;
              
              return (
                <div
                  key={archetype.id}
                  className={`trope-card ${isSelected ? 'trope-selected' : ''}`}
                  onClick={() => handleArchetypeToggle(archetype)}
                  data-testid={`archetype-${archetype.id}`}
                >
                  <div className="flex items-start gap-3">
                    <IconComponent className="w-6 h-6 text-indigo-400 flex-shrink-0 mt-1" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-semibold text-white">{archetype.name}</h3>
                        <Badge 
                          className={`text-xs ${
                            archetype.clicheRisk > 0.7 ? 'bg-red-500/20 text-red-300' :
                            archetype.clicheRisk > 0.4 ? 'bg-yellow-500/20 text-yellow-300' :
                            'bg-green-500/20 text-green-300'
                          }`}
                        >
                          {archetype.clicheRisk > 0.7 ? 'Cliché' :
                           archetype.clicheRisk > 0.4 ? 'Common' : 'Fresh'}
                        </Badge>
                      </div>
                      <p className="text-sm text-slate-400 mb-2">
                        {archetype.description}
                      </p>
                      <div className="text-xs text-indigo-300">
                        <strong>Subversions:</strong> {archetype.subversions.join(", ")}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Origins */}
      <Card className="visionforge-card">
        <CardHeader>
          <CardTitle className="text-white">Character Origins</CardTitle>
          <CardDescription className="text-indigo-200">
            Choose background and origin story elements
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {origins.map((origin) => {
              const isSelected = selectedOrigins.find(o => o.id === origin.id);
              
              return (
                <div
                  key={origin.id}
                  className={`trope-card ${isSelected ? 'trope-selected' : ''}`}
                  onClick={() => handleOriginToggle(origin)}
                  data-testid={`origin-${origin.id}`}
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-white">{origin.name}</h3>
                      <Badge 
                        className={`text-xs ${
                          origin.clicheRisk > 0.7 ? 'bg-red-500/20 text-red-300' :
                          origin.clicheRisk > 0.4 ? 'bg-yellow-500/20 text-yellow-300' :
                          'bg-green-500/20 text-green-300'
                        }`}
                      >
                        {origin.clicheRisk > 0.7 ? 'Overused' :
                         origin.clicheRisk > 0.4 ? 'Familiar' : 'Original'}
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-400">
                      {origin.description}
                    </p>
                    <div className="text-xs text-indigo-300">
                      <strong>Twist:</strong> {origin.twist}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Powers */}
      <Card className="visionforge-card">
        <CardHeader>
          <CardTitle className="flex items-center justify-between text-white">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              Superpower Builder
            </div>
            {customPowers.length > 0 && (
              <Badge className="bg-yellow-500/20 text-yellow-300 border-yellow-500/30">
                Total Cost: {totalPowerCost}/10
              </Badge>
            )}
          </CardTitle>
          <CardDescription className="text-indigo-200">
            Add powers with customizable cost and limitation sliders
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Power Templates */}
          <div>
            <h4 className="text-sm font-medium text-indigo-300 mb-3">Add Powers</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {powerTemplates.map((power, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="h-auto p-3 text-left justify-start border-slate-600 hover:bg-slate-700/50"
                  onClick={() => addCustomPower(power)}
                  data-testid={`power-template-${index}`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center justify-between w-full">
                      <span className="font-medium text-indigo-300">{power.name}</span>
                      <Badge className="text-xs bg-slate-600 text-slate-300">
                        Cost: {power.baseCost}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-400">{power.description}</p>
                  </div>
                </Button>
              ))}
            </div>
          </div>

          {/* Custom Powers List */}
          {customPowers.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-indigo-300 mb-3">Your Powers</h4>
              <div className="space-y-4">
                {customPowers.map((power) => (
                  <div
                    key={power.id}
                    className="bg-slate-700/30 rounded-lg p-4 border border-slate-600/50"
                    data-testid={`custom-power-${power.id}`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h5 className="font-semibold text-white">{power.name}</h5>
                        <p className="text-sm text-slate-400">{power.description}</p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => removePower(power.id)}
                        className="border-red-500/50 text-red-300 hover:bg-red-500/10"
                      >
                        <Minus className="w-4 h-4" />
                      </Button>
                    </div>

                    <div className="space-y-3">
                      {/* Cost Slider */}
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span className="text-slate-300">Power Level</span>
                          <span className="text-indigo-300">{powerCosts[power.id] || power.cost}/10</span>
                        </div>
                        <Slider
                          value={[powerCosts[power.id] || power.cost]}
                          onValueChange={(value) => updatePowerCost(power.id, value[0])}
                          max={10}
                          min={1}
                          step={1}
                          className="w-full"
                        />
                      </div>

                      {/* Limitations */}
                      <div>
                        <span className="text-xs text-slate-400">Limitations:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {power.limitations.map((limitation, idx) => (
                            <Badge
                              key={idx}
                              className="text-xs bg-red-500/20 text-red-300 border-red-500/30"
                            >
                              {limitation}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Character Summary */}
      {(selectedArchetypes.length > 0 || selectedOrigins.length > 0 || customPowers.length > 0) && (
        <Card className="visionforge-card" data-testid="character-summary">
          <CardHeader>
            <CardTitle className="text-white">Character Summary</CardTitle>
            <CardDescription className="text-indigo-200">
              Your unique character build
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {selectedArchetypes.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-indigo-300 mb-2">Archetypes</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedArchetypes.map((archetype) => (
                    <Badge
                      key={archetype.id}
                      className="bg-indigo-500/20 text-indigo-300 border-indigo-500/30"
                    >
                      {archetype.name}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {selectedOrigins.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-indigo-300 mb-2">Origins</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedOrigins.map((origin) => (
                    <Badge
                      key={origin.id}
                      className="bg-purple-500/20 text-purple-300 border-purple-500/30"
                    >
                      {origin.name}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {customPowers.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-indigo-300 mb-2">Powers</h4>
                <div className="flex flex-wrap gap-2">
                  {customPowers.map((power) => (
                    <Badge
                      key={power.id}
                      className="bg-yellow-500/20 text-yellow-300 border-yellow-500/30"
                    >
                      {power.name} ({powerCosts[power.id] || power.cost}/10)
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default TropeBuilder;