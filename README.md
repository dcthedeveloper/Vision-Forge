# VisionForge 🚀

**The Ultimate Character Creation & Storytelling Platform**

Transform images into rich lore, generate compelling narratives, and craft authentic characters with AI-powered tools designed for creators who demand both **deep control** and **sophisticated output**.

![VisionForge Interface](https://via.placeholder.com/800x400/1e293b/ffffff?text=VisionForge+Interface)

## ✨ Key Features

### 🖼️ **Image-to-Lore Analyzer** *(Flagship Feature)*
- Upload character artwork and get comprehensive AI analysis
- Extract traits, backstory seeds, and power suggestions from visual elements
- Support for multiple genres: Urban Realistic, High Fantasy, Sci-Fi, Cyberpunk, and more
- Advanced character classification with origins, social status, and power sources
- **BROKEN/OP Character Mode** for creating overpowered yet balanced characters

### 🧠 **Advanced Power System Generator** *(New!)*
- Generate sophisticated power systems using patterns from 20+ fictional works
- Choose from 10 power sources, 10 mechanics, 10 limitations, and 10 progression models
- Thematic coherence with 6 narrative clusters (identity crisis, power corruption, etc.)
- Modular sliders for fine-tuning: raw power, control precision, cost severity, social impact
- Creative applications and philosophical frameworks for each generated system

### 📖 **Beat Sheet Generator** *(Phase 2)*
- Multiple narrative structures: Save the Cat, Dan Harmon Story Circle, Three-Act, Hero's Journey, Kishōtenketsu
- Character-integrated beat descriptions using AI enhancement
- Customizable tone and pacing (Slow Burn, Standard, Fast Paced, Explosive)
- Professional page estimates and story structure visualization

### 🎯 **Enhanced Trope Risk Meter** *(Phase 2)*
- Analyze characters for cliché risks and freshness scoring
- Marcus-level sophistication detection
- AI-powered improvement suggestions with Ollama enhancement
- Individual trope analysis with subversion ideas and combination alternatives

### ✍️ **Style Coach 2.0**
- Detect overused AI words, generic fantasy tropes, and passive voice
- Show-don't-tell analysis with specific improvement suggestions
- Real-time cliché scoring and style issue identification
- Content rewriting with rationale

### 🔧 **Text Generator**
- Multiple generation types: Character creation, Story writing, Backstory development, Dialogue
- Style preference customization
- Anti-cliché detection and scoring
- Professional terminology focus

### 🏗️ **Trope & Archetype Builder**
- Interactive archetype building and combination system
- Avoid common character tropes with guided alternatives
- Sophisticated character development frameworks

## 🤖 **Hybrid AI System**

### **Model Flexibility**
Choose your AI backend based on your needs:

- **🏠 Ollama (Local)**: Privacy, no API costs, NSFW-friendly, always available
- **🧠 Claude Sonnet 4**: Best prose quality, low "cheese" factor, complex reasoning  
- **⚡ OpenAI GPT-4o**: Speed, consistency, function calling, vision capabilities

### **Content Safety Control** *(Key Differentiator)*
Creator-first NSFW filtering that no other platform offers:

- **🔒 Strict**: Family-friendly content only
- **⚖️ Moderate**: Standard content with mild mature themes
- **🔓 Permissive**: Full creative freedom for adult fiction, horror, dark themes

*Per-project settings allow different content levels for different stories.*

## 🏗️ **Technical Architecture**

```
Frontend (React + Tailwind)
├── Image Analyzer
├── Text Generator  
├── Style Coach
├── Trope Builder
├── Beat Sheet Generator
├── Trope Risk Meter
├── Power System Generator
├── AI Settings
└── Analysis History

Backend (FastAPI + Python)
├── Hybrid AI Client (Ollama + emergentintegrations)
├── Content Filter (3-tier safety system)
├── Power System Framework
├── Beat Sheet Templates
├── Enhanced Trope Database
├── Knowledge Graph Integration
├── Vector Database (Qdrant)
└── Rule Engine

Database (MongoDB)
├── Character Analyses
├── Generated Content
├── User Preferences
└── Power System Profiles
```

## 🚀 **Quick Start**

### Prerequisites
- **Node.js** 16+ and **Yarn**
- **Python** 3.11+ and **pip** 
- **MongoDB** (local or cloud)
- **Ollama** installed and running
- **Emergent LLM Key** (for Claude/OpenAI access)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/visionforge.git
   cd visionforge
   ```

2. **Install Ollama and models**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama serve &
   ollama pull llama3.2
   ollama pull llava:7b
   ```

3. **Backend setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Create .env file
   echo "MONGO_URL=mongodb://localhost:27017/visionforge" > .env
   echo "EMERGENT_LLM_KEY=your-emergent-key-here" >> .env
   
   # Start backend
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```

4. **Frontend setup**
   ```bash
   cd frontend
   yarn install
   
   # Create .env file
   echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env
   
   # Start frontend
   yarn start
   ```

5. **Access VisionForge**
   - Open `http://localhost:3000`
   - Configure your AI provider in Settings
   - Start creating characters!

## 📡 **API Endpoints**

### Core Features
- `POST /api/analyze-image` - Analyze character images with hybrid AI
- `POST /api/generate-text` - Generate stories, dialogue, backstories
- `POST /api/analyze-style` - Analyze writing for cliché and style issues
- `GET /api/analyses` - Retrieve analysis history

### Phase 2 Features  
- `POST /api/generate-beat-sheet` - Generate narrative beat sheets
- `GET /api/beat-sheet-types` - Available beat sheet structures
- `POST /api/analyze-trope-risk` - Analyze character trope risks

### Advanced Features
- `POST /api/generate-power-system` - Generate sophisticated power systems
- `GET /api/power-system-themes` - Available narrative themes

### AI & Content Management
- `GET /api/ai-providers` - Available AI providers and status
- `POST /api/set-default-provider` - Set default AI provider
- `GET /api/content-safety-levels` - Available safety levels
- `POST /api/analyze-content-safety` - Analyze content safety

## 🎨 **Usage Examples**

### Character Analysis from Image
```python
import requests

files = {'file': open('character.jpg', 'rb')}
data = {
    'genre': 'cyberpunk',
    'origin': 'enhanced',
    'power_source': 'technology_fusion',
    'ai_provider': 'claude',
    'safety_level': 'moderate'
}

response = requests.post('http://localhost:8001/api/analyze-image', 
                        files=files, data=data)
analysis = response.json()['analysis']
print(f"Character: {analysis['persona_summary']}")
```

### Generate Power System
```python
payload = {
    "narrative_focus": "power_corruption",
    "complexity_level": "complex",
    "character_context": {
        "character_origin": "enhanced",
        "social_status": "entrepreneur"
    }
}

response = requests.post('http://localhost:8001/api/generate-power-system',
                        json=payload)
power_system = response.json()['power_system']
print(f"Power: {power_system['mechanic']['name']}")
print(f"Limitation: {power_system['limitations']['primary']['name']}")
```

### Generate Beat Sheet
```python
payload = {
    "sheet_type": "save_the_cat",
    "tone_pacing": "fast_paced", 
    "story_length": 120,
    "character_data": character_analysis_data
}

response = requests.post('http://localhost:8001/api/generate-beat-sheet',
                        json=payload)
beat_sheet = response.json()['beat_sheet']
print(f"Structure: {beat_sheet['title']} - {beat_sheet['total_beats']} beats")
```

## 🌟 **Key Differentiators**

### **Creator-First Philosophy**
- **User-controlled content filtering** vs locked-down competitors
- **Hybrid AI flexibility** vs vendor lock-in
- **Transparent control** vs black-box magic
- **Professional sophistication** vs generic fantasy tropes

### **Sophisticated Character Creation**
- **Multi-stage analysis** combining vision and narrative AI
- **Marcus-style character depth** with nootropic enhancements
- **Power system patterns** extracted from 20+ fictional works
- **Cross-modal continuity** between image, text, and narrative elements

### **Advanced Narrative Tools**
- **5 beat sheet structures** with character integration
- **Trope risk analysis** with AI-powered suggestions
- **Style coaching** beyond basic grammar checking
- **Philosophical frameworks** for power system creation

## 🔧 **Configuration**

### AI Provider Setup
1. Go to **AI Settings** tab
2. Choose your preferred provider:
   - **Ollama**: No setup needed if running locally
   - **Claude/OpenAI**: Requires Emergent LLM Key
3. Set global default or use per-tool overrides

### Content Safety Configuration
1. Select your project's content level:
   - **Strict**: Family-friendly only
   - **Moderate**: Standard + mild mature themes  
   - **Permissive**: Adult fiction, horror, dark themes
2. Settings apply to all AI generation for consistency

### Power System Customization
- Choose narrative theme for thematic coherence
- Adjust complexity level (Simple/Moderate/Complex)
- Use character context for personalized systems
- Export systems for use in other tools

## 📊 **System Requirements**

### Minimum Requirements
- **CPU**: 4 cores, 2.5GHz
- **RAM**: 8GB (16GB recommended for Ollama)
- **Storage**: 10GB free space
- **GPU**: Optional (improves Ollama performance)

### Recommended Setup
- **CPU**: 8+ cores, 3.0GHz+
- **RAM**: 16GB+ 
- **Storage**: SSD with 20GB+ free space
- **GPU**: NVIDIA RTX 3060 or equivalent for optimal Ollama performance

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Submit a pull request with detailed description

### Areas for Contribution
- **New power system patterns** from additional fictional works
- **Additional beat sheet structures** (Blake Snyder variations, etc.)
- **Enhanced trope detection** algorithms
- **UI/UX improvements** and accessibility features
- **API integrations** with writing tools
- **Mobile responsiveness** enhancements

## 📜 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Fictional Works Analysis**: Patterns extracted from The Boys, Heroes, My Hero Academia, JoJo's Bizarre Adventure, One Piece, One Punch Man, and 15+ other works
- **AI Integration**: Built on Ollama, OpenAI, and Anthropic technologies
- **UI Components**: Powered by Shadcn/UI and Tailwind CSS
- **Community**: Thanks to all beta testers and contributors

## 📞 **Support**

- **Documentation**: Visit our [Wiki](https://github.com/your-username/visionforge/wiki)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/your-username/visionforge/issues)
- **Discussions**: Join our [Community Forum](https://github.com/your-username/visionforge/discussions)
- **Discord**: Real-time chat in our [Creator Community](https://discord.gg/visionforge)

---

**Made with ❤️ for creators who demand both control and sophistication in their storytelling tools.**

*VisionForge: Where vision meets craft, and creativity knows no bounds.*
