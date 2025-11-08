# 🎓 PyMaster - Advanced Python Learning Assistant

<div align="center">

```
██████╗ ██╗   ██╗███╗   ███╗ █████╗ ███████╗████████╗
██╔══██╗╚██╗ ██╔╝████╗ ████║██╔══██╗██╔════╝╚══██╔══╝
██████╔╝ ╚████╔╝ ██╔████╔██║███████║███████╗   ██║
██╔═══╝   ╚██╔╝  ██║╚██╔╝██║██╔══██║╚════██║   ██║
██║        ██║   ██║ ╚═╝ ██║██║  ██║███████║   ██║
╚═╝        ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝
```

**An interactive Python learning platform with adaptive challenges, real-time feedback, and progress tracking**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

---
<img width="2325" height="980" alt="image" src="https://github.com/user-attachments/assets/bbcabb63-a522-4f31-a027-4c04bb311520" />

## ✨ Features

- 🧠 **Adaptive Assessment** - Smart quiz system that adjusts difficulty based on your performance
- 🎯 **Interactive Challenges** - Hands-on coding exercises across multiple modules
- 📊 **Real-time Analysis** - Instant feedback on syntax, PEP8 compliance, and performance
- 🏆 **Achievement System** - Earn badges for milestones and accomplishments
- 📈 **Progress Tracking** - Visual dashboard showing mastery levels across concepts
- 💡 **Smart Hints** - Progressive hint system to guide you without spoiling solutions
- 📤 **Export Reports** - Generate detailed learning reports in Markdown, HTML, or PDF
- 🔒 **Safe Execution** - Sandboxed code execution for security

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/matte1782/pymaster.git
cd pymaster
```

2. **Create virtual environment** (recommended)
```bash
python -m venv .venv

# Activate on macOS/Linux:
source .venv/bin/activate

# Activate on Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run PyMaster**
```bash
python pymaster.py
```

## 📚 Usage

### First Time Setup

When you first run PyMaster, you'll be prompted for a username:

```
Enter your username [python_learner]: yourname
```

### Main Menu

```
🎓 PyMaster - Advanced Python Learning
==================================================
1. 🏃 Start Assessment
2. 📚 View Learning Path
3. 🎯 Practice Challenges
4. 📊 Progress Dashboard
5. 💡 Show Hints
6. 🏆 Achievements
7. 📤 Export Report
8. 🚪 Exit
```

### Taking the Assessment

The assessment adapts to your skill level:
- Answer questions correctly → harder questions
- Answer incorrectly → easier questions
- Determines your recommended starting level

### Practice Challenges

1. Select "Practice Challenges" from menu
2. Read the challenge description and template
3. Write your solution
4. Type `END` on a new line to submit
5. Get instant feedback on your code

**Example Challenge Flow:**
```
🚀 Challenge: List Comprehension Practice
Filter even numbers from a list and double them

📝 Template Code:
[template shown...]

💻 Enter your solution (type 'END' on a new line to finish):
def process_data(data):
    return [x * 2 for x in data if x % 2 == 0]
END

✅ PASSED
📊 Code Quality Metrics:
  Syntax Validity: ✅
  PEP8 Compliance: 95.0%
  Performance: 100.0%
  Execution Time: 0.0002s
```

### Using Hints

During challenges, you can request hints:
- Hints are revealed progressively
- Each hint provides more specific guidance
- Hints used count is tracked

### Viewing Progress

The dashboard shows:
- Mastery percentage for each concept
- Visual progress bars
- Module completion status
- Recent activity

### Earning Achievements

Unlock achievements by:
- ✨ Completing your first challenge
- 🎯 Perfect first-attempt passes
- ⚡ Fast execution times
- 📐 Perfect PEP8 scores
- 🔥 Maintaining learning streaks

### Exporting Reports

Generate comprehensive reports including:
- Overall progress summary
- Mastery levels by module
- Challenge statistics
- Achievements earned
- Personalized recommendations

Supported formats: Markdown (`.md`), HTML (`.html`), PDF (`.pdf`)

## 🏗️ Project Structure

```
pymaster/
├── pymaster.py              # Main application
├── requirements.txt         # Runtime dependencies
├── requirements-dev.txt     # Development dependencies
├── pytest.ini              # Pytest configuration
├── .flake8                 # Flake8 configuration
├── pymaster.db             # SQLite database (created on first run)
├── reports/                # Generated reports directory
├── tests/                  # Test suite
│   ├── test_database.py
│   ├── test_code_analyzer.py
│   ├── test_challenges.py
│   ├── test_performance.py
│   ├── test_progress.py
│   ├── test_achievements.py
│   ├── test_export.py
│   └── test_integration.py
└── docs/                   # Documentation
    ├── ARCHITECTURE.md
    ├── API.md
    ├── DATABASE.md
    ├── CHALLENGES.md
    └── DEPLOYMENT.md
```

## 🎓 Learning Modules

### Available Modules

1. **Core Python** - Functions, data types, control flow
2. **Data Structures** - Lists, dicts, sets, comprehensions
3. **Object-Oriented Programming** - Classes, inheritance, polymorphism
4. **Error Handling** - Exceptions, try/except, custom exceptions
5. **File I/O** - Reading/writing files, context managers
6. **Decorators** - Function decorators, class decorators
7. **Concurrency** - Threading, async/await
8. **Testing** - Unit tests, pytest, TDD

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_database.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy . --ignore-missing-imports
```

### Adding New Challenges

See [docs/CHALLENGES.md](docs/CHALLENGES.md) for detailed guide.

Quick example:
```python
challenge = CorePythonChallenge(
    challenge_id="core_004",
    title="Your Challenge Title",
    description="Challenge description",
    difficulty=3,
    module="core_python",
    concept="your_concept"
)
challenge.add_test_case({'function': 'solution', 'args': [1, 2]}, 3)
challenge.add_hint("First hint")
```

## 🔧 Configuration

### Environment Variables

- `PYMASTER_DB_PATH` - Custom database location (default: `pymaster.db`)
- `PYMASTER_SAFE_MODE` - Enable strict sandboxing (`true`/`false`)
- `PYMASTER_TIMEOUT` - Code execution timeout in seconds (default: `5`)

### Database Configuration

The SQLite database is created automatically. To use a custom location:

```bash
export PYMASTER_DB_PATH="/path/to/custom/database.db"
python pymaster.py
```

## 🐛 Troubleshooting

### Common Issues

**Import Error: No module named 'rich'**
```bash
pip install -r requirements.txt
```

**Permission Error on Windows**
- Run PowerShell as Administrator
- Or use: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Database Lock Error**
- Close any other PyMaster instances
- Delete `pymaster.db-journal` if it exists

**Code Execution Timeout**
- Increase timeout: `export PYMASTER_TIMEOUT=10`
- Check for infinite loops in your solution

### Getting Help

- 📖 Check [documentation](docs/)
- 🐛 [Open an issue](https://github.com/matte1782/pymaster/issues)
- 💬 [Discussions](https://github.com/matte1782/pymaster/discussions)

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- ✨ Add new challenges
- 🧪 Write tests
- 🔧 Fix issues

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal UI
- Inspired by interactive learning platforms
- Thanks to all contributors!

## 📊 Stats

- 15+ Interactive Challenges
- 8 Learning Modules
- 10+ Achievement Badges
- Comprehensive Progress Tracking

---

<div align="center">

**Made with ❤️ by Python learners, for Python learners**

[Getting Started](#-quick-start) • [Documentation](docs/) • [Report Bug](https://github.com/matte1782/pymaster/issues) • [Request Feature](https://github.com/matte1782/pymaster/issues)

</div>
