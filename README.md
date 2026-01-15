# Syncora 🎓

> An intelligent educational platform built for Pakistani students, powered by AI agents that actually understand what you need.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Next.js](https://img.shields.io/badge/next.js-14.0+-black.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)

---

## What's This About?

Look, we've all been there - struggling to find good study material, trying to practice with past papers that are hard to come by, or just wanting someone to explain that one tricky physics concept at 2 AM. That's exactly why Syncora exists.

It's not just another EdTech app. We built this with Pakistani students in mind - PCTB curriculum, bilingual support (Urdu/English), and designed to work even when your internet decides to take a break.

## The Cool Stuff

### 🤖 Smart Question Generator
Upload your syllabus or past papers, and watch it generate questions that actually make sense. It understands the difference between a board exam question and a routine test.

- **Exam Mimic**: Upload a past paper, get similar questions in the same style
- **Custom Generation**: Tell it what you want - MCQs, short answers, long questions
- **Difficulty Control**: Easy, medium, or "I want to challenge myself" mode

### 💡 Problem Solver That Actually Helps
Not just answers - proper step-by-step solutions with explanations. It even searches the web when needed and can run code for programming problems.

### 📚 Knowledge Base (Your Personal Library)
Upload PDFs, notes, textbooks - anything. The system reads them, understands them, and can answer questions from your uploaded content.

### 📖 Offline Learning Packs
Internet down? No problem. Generate a complete study pack for any topic, download it, and study offline. Includes MCQs, practice questions, and key concepts - all in a neat HTML file that works without internet.

### 🔍 Research Assistant
Need to write an essay or research something? This guy's got your back with web search and smart summarization.

## Why We Built This

Three simple reasons:

1. **Access**: Not everyone has stable internet or can afford expensive platforms
2. **Relevance**: Most AI tools don't understand Pakistani curriculum
3. **Language**: Because sometimes you just want to read in Urdu

## Tech Stack (For the Curious)

**Frontend:**
- Next.js 14 (App Router, because we like living on the edge)
- TypeScript (fewer bugs = happier developers)
- Tailwind CSS (styling without the headaches)

**Backend:**
- FastAPI (async all the things!)
- Python 3.10+ 
- WebSocket (real-time updates are cool)

**AI/ML:**
- Multiple LLM providers (Groq, OpenAI-compatible APIs)
- Sentence Transformers for embeddings
- Local FLAN-T5 (for when you're offline)
- RAG with ChromaDB

**The Smart Bits:**
- 7 specialized AI agents working together
- Fallback systems everywhere (degraded mode FTW)
- Vector database with JSON fallback
- Async operations for smooth UX

## Getting Started

### Prerequisites

You'll need:
- Python 3.10 or higher
- Node.js 18+ and npm
- About 2GB free space
- Coffee ☕ (optional but recommended)

### Quick Setup

1. **Clone this repo**
```bash
git clone <your-repo-url>
cd Syncora
```

2. **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Create a .env file (copy from .env.example)
cp .env.example .env
# Add your API keys here
```

3. **Frontend Setup**
```bash
cd web
npm install
# or if you prefer yarn
yarn install
```

4. **Fire it up!**
```bash
# From the scripts directory
cd scripts
python start_web.py
```

Visit `http://localhost:3000` and you're good to go!

### Docker Setup (If You're Into That)

```bash
docker-compose up -d
```

Yeah, it's that simple.

## Project Structure

```
Syncora/
├── src/                    # Backend code
│   ├── agents/            # The 7 AI agents
│   ├── api/               # FastAPI routes
│   ├── services/          # Business logic
│   └── tools/             # Utilities and helpers
├── web/                   # Next.js frontend
│   ├── app/              # Pages and routes
│   ├── components/       # React components
│   └── context/          # Global state
├── data/                  # Storage (not in git)
├── config/               # Configuration files
└── scripts/              # Utility scripts
```

## Configuration

Main settings are in `config/main.yaml`. Some things you might want to tweak:

```yaml
llm:
  model: "kimi-k2-instruct-0905"  # Change your model
  temperature: 0.7                 # Control randomness

question:
  difficulty_levels: ["easy", "medium", "hard"]
  
curriculum:
  supported_grades: [8, 9, 10]
  board: "PCTB"
```

## Features Deep Dive

### Question Generation System

The question generator isn't just slapping random questions together. Here's what makes it smart:

1. **Research Phase**: Gathers relevant information from your knowledge base
2. **Planning**: Creates a question plan ensuring variety and coverage
3. **Generation**: Produces questions with proper formatting
4. **Validation**: Checks quality, relevance, and difficulty

### The Agent System

Each agent has a specific job:

- **Question Agent**: Generates educational questions
- **Validation Agent**: Quality control for questions
- **Solve Agent**: Solves problems with explanations
- **Research Agent**: Gathers information from multiple sources
- **Co-Writer Agent**: Helps with essays and writing
- **Guide Agent**: Provides study guidance
- **Notebook Agent**: Manages your notes

They communicate with each other through a message-passing system. Pretty neat.

### Offline Mode

When you generate an offline pack, you get:

- Self-contained HTML files
- Embedded JavaScript for progress tracking
- Styles that work without CDN
- Complete study material: concepts, examples, questions
- Works on any device with a browser

## API Documentation

Once the server is running, check out:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment Notes

For production deployment:

1. Set proper environment variables
2. Use a proper database for user data
3. Set up CORS properly
4. Use HTTPS
5. Consider rate limiting on API endpoints
6. Set up proper logging

Check `docker-compose.yml` for a production-ready setup example.

## Contributing

Found a bug? Want to add a feature? PRs are welcome!

1. Fork it
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure your code:
- Follows the existing style
- Includes tests if applicable
- Has proper error handling
- Doesn't break existing features

## Roadmap

Things we're working on:

- [ ] Mobile app (React Native)
- [ ] More curriculum support (other boards)
- [ ] Collaborative study rooms
- [ ] Gamification features
- [ ] Voice input/output
- [ ] Teacher dashboard
- [ ] Analytics and insights

## Known Issues

- ChromaDB can be flaky sometimes (we have fallbacks)
- Large PDF processing takes time (working on it)
- Offline packs can be big for content-heavy topics

## FAQ

**Q: Is it free?**  
A: Yes! Open source and free to use.

**Q: Do I need an API key?**  
A: For full features, yes. But you can use local models for basic functionality.

**Q: Works offline?**  
A: Partially - you can generate offline packs that work completely offline.

**Q: Can I contribute?**  
A: Absolutely! Check the Contributing section.

**Q: Which grades are supported?**  
A: Currently 8, 9, and 10 (PCTB). More coming soon.

## Acknowledgments

Built with ❤️ for Pakistani students who deserve better educational tools.

Special thanks to:
- The open source community
- Coffee ☕
- Stack Overflow (obviously)
- Everyone who gave feedback during development

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contact

Got questions? Suggestions? Just want to say hi?

- Open an issue on GitHub
- Or reach out to the team

---

**Remember**: Education should be accessible to everyone, everywhere. That's why we built this.

Happy learning! 📚✨
