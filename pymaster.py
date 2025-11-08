"""
PyMaster - Advanced Python Learning Assistant (Enhanced Version) - Windows Compatible

A comprehensive Python learning script that transforms intermediate learners
into advanced practitioners through adaptive assessment, interactive challenges,
and real-time feedback.
"""

import ast
import sqlite3
import json
import os
import sys
import time
import tempfile
import subprocess
import hashlib
import threading
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
import logging

# ---- Windows compatibility: DO NOT import linux-only modules like resource/pwd/grp ----

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt
    import colorama
except ImportError:
    print("Error: Required packages not installed.")
    print("Please run: pip install rich colorama")
    sys.exit(1)

# Initialize colorama for cross-platform colored output
colorama.init()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('pymaster.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'DB_PATH': os.getenv('PYMASTER_DB_PATH', 'pymaster.db'),
    'SAFE_MODE': os.getenv('PYMASTER_SAFE_MODE', 'true').lower() == 'true',
    'TIMEOUT': int(os.getenv('PYMASTER_TIMEOUT', '5')),
    'REPORTS_DIR': os.getenv('PYMASTER_REPORTS_DIR', 'reports'),
    'MAX_HINTS': int(os.getenv('PYMASTER_MAX_HINTS', '3')),
    'MAX_CONCURRENT_EXECUTIONS': int(os.getenv('PYMASTER_MAX_CONCURRENT', '5')),
}

execution_semaphore = threading.Semaphore(CONFIG['MAX_CONCURRENT_EXECUTIONS'])

PYMASTER_ART = r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██████╗ ██╗   ██╗███╗   ███╗ █████╗ ███████╗████████╗███████╗██████╗        ║
║  ██╔══██╗╚██╗ ██╔╝████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗       ║
║  ██████╔╝ ╚████╔╝ ██╔████╔██║███████║███████╗   ██║   █████╗  ██████╔╝       ║
║  ██╔═══╝   ╚██╔╝  ██║╚██╔╝██║██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗       ║
║  ██║        ██║   ██║ ╚═╝ ██║██║  ██║███████║   ██║   ███████╗██║  ██║       ║
║  ╚═╝        ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝       ║
║                                                                              ║
║              Advanced Python Learning Assistant v2.0                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ──────────────────────────────────────────────────────────────────────────────
# Dataclasses
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class UserProgress:
    user_id: str
    module: str
    concept: str
    attempts: int
    correct_attempts: int
    last_attempt: datetime
    mastery_level: float  # 0.0 to 1.0

    def get_mastery_percentage(self) -> int:
        return int(self.mastery_level * 100)


@dataclass
class ChallengeResult:
    challenge_id: str
    user_code: str
    passed: bool
    syntax_valid: bool
    performance_score: float
    pep8_score: float
    execution_time: float
    feedback: List[str]
    hints_used: int = 0


# ──────────────────────────────────────────────────────────────────────────────
# Database Manager (SQLite)
# ──────────────────────────────────────────────────────────────────────────────

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or CONFIG['DB_PATH']
        self.init_database()
        logger.info(f"Database initialized at {self.db_path}")

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('PRAGMA foreign_keys = ON')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                module TEXT NOT NULL,
                concept TEXT NOT NULL,
                attempts INTEGER DEFAULT 0 CHECK(attempts >= 0),
                correct_attempts INTEGER DEFAULT 0 CHECK(correct_attempts >= 0),
                last_attempt TIMESTAMP,
                mastery_level REAL DEFAULT 0.0 CHECK(mastery_level >= 0.0 AND mastery_level <= 1.0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, module, concept)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS challenge_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                user_code TEXT,
                passed BOOLEAN,
                syntax_valid BOOLEAN,
                performance_score REAL,
                pep8_score REAL,
                execution_time REAL,
                feedback TEXT,
                hints_used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, achievement_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                challenges_completed INTEGER DEFAULT 0 CHECK(challenges_completed >= 0)
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_challenge_results_user
            ON challenge_results(user_id, created_at DESC)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_achievements_user
            ON achievements(user_id)
        ''')

        conn.commit()
        conn.close()

    def save_progress(self, progress: UserProgress):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_progress
            (user_id, module, concept, attempts, correct_attempts, last_attempt, mastery_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, module, concept) DO UPDATE SET
                attempts = excluded.attempts,
                correct_attempts = excluded.correct_attempts,
                last_attempt = excluded.last_attempt,
                mastery_level = excluded.mastery_level
        ''', (
            progress.user_id,
            progress.module,
            progress.concept,
            progress.attempts,
            progress.correct_attempts,
            progress.last_attempt.isoformat() if progress.last_attempt else None,
            progress.mastery_level
        ))
        conn.commit()
        conn.close()

    def get_user_progress(self, user_id: str, module: str = None, concept: str = None) -> List[UserProgress]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM user_progress WHERE user_id = ?"
        params = [user_id]

        if module:
            query += " AND module = ?"
            params.append(module)
        if concept:
            query += " AND concept = ?"
            params.append(concept)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        progress_list = []
        for row in rows:
            progress_list.append(UserProgress(
                user_id=row[1],
                module=row[2],
                concept=row[3],
                attempts=row[4] or 0,
                correct_attempts=row[5] or 0,
                last_attempt=datetime.fromisoformat(row[6]) if row[6] else None,
                mastery_level=row[7] or 0.0
            ))
        return progress_list

    def save_challenge_result(self, result: ChallengeResult, user_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO challenge_results
            (challenge_id, user_id, user_code, passed, syntax_valid, performance_score, pep8_score,
             execution_time, feedback, hints_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.challenge_id,
            user_id,
            result.user_code,
            result.passed,
            result.syntax_valid,
            result.performance_score,
            result.pep8_score,
            result.execution_time,
            json.dumps(result.feedback),
            result.hints_used
        ))
        conn.commit()
        conn.close()

    def start_session(self, user_id: str) -> str:
        session_id = hashlib.md5(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_sessions (session_id, user_id) VALUES (?, ?)', (session_id, user_id))
        conn.commit()
        conn.close()
        return session_id

    def end_session(self, session_id: str, challenges_completed: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_sessions
            SET end_time = ?, challenges_completed = ?
            WHERE session_id = ?
        ''', (datetime.now().isoformat(), challenges_completed, session_id))
        conn.commit()
        conn.close()

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM challenge_results WHERE user_id = ?', (user_id,))
        total_challenges = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM challenge_results WHERE user_id = ? AND passed = 1', (user_id,))
        passed_challenges = cursor.fetchone()[0]

        cursor.execute('''
            SELECT AVG(pep8_score), AVG(performance_score), AVG(execution_time)
            FROM challenge_results WHERE user_id = ?
        ''', (user_id,))
        avg_row = cursor.fetchone()

        cursor.execute('SELECT COUNT(*), SUM(challenges_completed) FROM user_sessions WHERE user_id = ?', (user_id,))
        session_row = cursor.fetchone()

        conn.close()
        return {
            'total_challenges': total_challenges,
            'passed_challenges': passed_challenges,
            'success_rate': (passed_challenges / total_challenges * 100) if total_challenges else 0,
            'avg_pep8_score': (avg_row[0] or 0) * 100,
            'avg_performance_score': (avg_row[1] or 0) * 100,
            'avg_execution_time': avg_row[2] or 0,
            'total_sessions': session_row[0] or 0,
            'total_session_challenges': session_row[1] or 0,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Safe Code Executor (Windows-compatible)
# ──────────────────────────────────────────────────────────────────────────────

class SafeCodeExecutor:
    """
    Cross-platform safe executor:
    - Runs user code in a subprocess with a timeout.
    - Restricts dangerous imports via a pre-scan.
    - Resolves dotted call targets (e.g., "Solution().process") INSIDE the child.
    """

    def __init__(self, timeout: int = None):
        self.timeout = timeout or CONFIG['TIMEOUT']

    def execute(self, code: str, test_function: Optional[str] = None,
                args: tuple = (), kwargs: dict = None) -> Tuple[bool, Any, str]:
        kwargs = kwargs or {}

        # Simple static safety scan (best effort)
        if not self._is_safe_code(code):
            return False, None, "Code contains unsafe operations (blocked import or call)."

        with execution_semaphore:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                wrapper = self._make_wrapper(code, test_function, args, kwargs)
                f.write(wrapper)
                temp_file = f.name

            try:
                env = os.environ.copy()
                # Keep PATH; don't force Unix paths on Windows
                env["PYTHONPATH"] = ""  # reduce module search path exposure

                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    env=env
                )

                stdout = (result.stdout or "").strip()
                stderr = (result.stderr or "").strip()

                if stdout:
                    last_line = stdout.splitlines()[-1].strip()
                    try:
                        payload = json.loads(last_line)
                        if payload.get("success"):
                            return True, payload.get("result"), ""
                        else:
                            return False, None, payload.get("error", "Unknown error")
                    except json.JSONDecodeError:
                        # Not our JSON; return stderr or raw stdout
                        return False, None, stderr or "Invalid output format"
                else:
                    return False, None, stderr or "No output"

            except subprocess.TimeoutExpired:
                return False, None, f"Execution timeout ({self.timeout}s exceeded)"
            except Exception as e:
                return False, None, f"Execution error: {e}"
            finally:
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass

    def _is_safe_code(self, code: str) -> bool:
        blocked_imports = {
            "os", "sys", "subprocess", "socket", "shutil", "ctypes",
            "multiprocessing", "asyncio.subprocess", "urllib", "requests",
            "glob", "pathlib", "__future__"
        }
        blocked_calls = {"eval", "exec", "__import__", "open("}

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return True  # let syntax validator handle later

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name.split('.')[0] for a in getattr(node, "names", [])]
                mod = getattr(node, "module", None)
                check = names + ([mod.split('.')[0]] if mod else [])
                if any(x in blocked_imports for x in check if x):
                    return False

            # rudimentary string check
        lower = code.lower()
        if any(tok in lower for tok in blocked_calls):
            return False

        return True

    def _make_wrapper(self, code: str, test_function: Optional[str], args: tuple, kwargs: dict) -> str:
        # Embed test expression safely via JSON to preserve quotes/escapes
        test_expr_json = json.dumps(test_function if test_function else "")
        args_json = json.dumps(args)
        kwargs_json = json.dumps(kwargs)

        return f"""# Auto-generated safe wrapper
import json

# ===== USER CODE START =====
{code}
# ===== USER CODE END =====

def _json_out(payload):
    try:
        print(json.dumps(payload))
    except Exception as _e:
        print(json.dumps({{"success": False, "error": f"JSON encode error: {{_e}}"}}))

try:
    test_expr = {test_expr_json}
    if test_expr:
        # Resolve the target inside the sandboxed process
        try:
            target = eval(test_expr, globals(), locals())
        except Exception as e:
            _json_out({{"success": False, "error": f"Cannot resolve target '{{test_expr}}': {{e}}"}})
        else:
            try:
                args = tuple({args_json})
                kwargs = dict({kwargs_json})
                result = target(*args, **kwargs)
                _json_out({{"success": True, "result": repr(result)}})
            except Exception as e:
                _json_out({{"success": False, "error": f"Execution error: {{type(e).__name__}}: {{e}}"}})
    else:
        # No specific function to call; treat as OK if import/exec succeeded
        _json_out({{"success": True, "result": "OK"}})
except Exception as e:
    _json_out({{"success": False, "error": f"Wrapper error: {{type(e).__name__}}: {{e}}"}})
"""


# ──────────────────────────────────────────────────────────────────────────────
# Analyzers & Validator
# ──────────────────────────────────────────────────────────────────────────────

class CodeAnalyzer:
    @staticmethod
    def validate_syntax(code: str) -> Tuple[bool, List[str]]:
        try:
            ast.parse(code)
            return True, []
        except SyntaxError as e:
            return False, [f"Syntax Error on line {e.lineno}: {e.msg}"]
        except Exception as e:
            return False, [f"Error: {str(e)}"]

    @staticmethod
    def check_pep8(code: str) -> Tuple[float, List[str]]:
        feedback, score = [], 1.0
        lines = code.splitlines()
        long_lines = [i + 1 for i, line in enumerate(lines) if len(line) > 79]
        if long_lines:
            feedback.append(f"Lines {long_lines[:3]} exceed 79 characters" + (" and more..." if len(long_lines) > 3 else ""))
            score -= min(0.1 * len(long_lines), 0.3)
        trailing = [i + 1 for i, l in enumerate(lines) if l.rstrip() != l]
        if trailing:
            feedback.append(f"Trailing whitespace on lines {trailing[:3]}")
            score -= 0.05
        if not feedback:
            feedback.append("PEP8 check OK")
        return max(0.0, score), feedback


class ChallengeValidator:
    def __init__(self):
        self.executor = SafeCodeExecutor()

    def validate_solution(self, user_code: str, test_cases: List[Dict], expected_outputs: List[Any]) -> Tuple[bool, List[str]]:
        if not test_cases:
            return True, ["No test cases defined"]
        feedback = []
        passed = 0
        for i, (tc, exp) in enumerate(zip(test_cases, expected_outputs), start=1):
            func = tc.get('function')
            args = tuple(tc.get('args', []))
            kwargs = dict(tc.get('kwargs', {}))
            ok, result, err = self.executor.execute(user_code, func, args, kwargs)
            if not ok:
                feedback.append(f"❌ Test {i}: {err}")
                continue
            try:
                val = ast.literal_eval(result)
            except Exception:
                val = result
            if val == exp:
                passed += 1
                feedback.append(f"✅ Test {i}: Passed")
            else:
                feedback.append(f"❌ Test {i}: Expected {exp}, got {val}")
        all_passed = passed == len(test_cases)
        summary = f"🎉 All {len(test_cases)} test cases passed!" if all_passed else f"⚠️  {passed}/{len(test_cases)} test cases passed"
        feedback.insert(0, summary)
        return all_passed, feedback


# ──────────────────────────────────────────────────────────────────────────────
# Challenge Model
# ──────────────────────────────────────────────────────────────────────────────

class Challenge(ABC):
    def __init__(self, challenge_id: str, title: str, description: str,
                 difficulty: int, module: str, concept: str):
        self.challenge_id = challenge_id
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.module = module
        self.concept = concept
        self.hints: List[str] = []
        self.test_cases: List[Dict] = []
        self.expected_outputs: List[Any] = []

    @abstractmethod
    def get_template(self) -> str:
        ...

    @abstractmethod
    def get_solution(self) -> str:
        ...

    def add_hint(self, hint: str):
        self.hints.append(hint)

    def add_test_case(self, test_case: Dict, expected_output: Any):
        self.test_cases.append(test_case)
        self.expected_outputs.append(expected_output)


class CorePythonChallenge(Challenge):
    def get_template(self) -> str:
        if self.concept == "functions":
            return f'''# {self.title}
# {self.description}

def solution(a, b):
    """Write your function here"""
    # return a + b
    pass
'''
        return f'''# {self.title}
# {self.description}

def solution(data):
    """Write your function here"""
    pass
'''

    def get_solution(self) -> str:
        return '''def solution(a, b):
    return a + b
'''


class DataStructuresChallenge(Challenge):
    def get_template(self) -> str:
        return f'''# {self.title}
# {self.description}

def solution(data):
    """Return [x*2 for x in data if x % 2 == 0]"""
    pass
'''

    def get_solution(self) -> str:
        return '''def solution(data):
    return [x * 2 for x in data if x % 2 == 0]
'''


class OOPChallenge(Challenge):
    def get_template(self) -> str:
        return f'''# {self.title}
# {self.description}

class Solution:
    def __init__(self):
        self.data = []

    def process(self, data):
        return f"Processed: {{data}}"
'''
    def get_solution(self) -> str:
        return '''class Solution:
    def __init__(self):
        self.data = []

    def process(self, data):
        return f"Processed: {data}"
'''


# ──────────────────────────────────────────────────────────────────────────────
# Import new modules
# ──────────────────────────────────────────────────────────────────────────────

import pymaster_gamification
import pymaster_quests
import pymaster_arcade


# ──────────────────────────────────────────────────────────────────────────────
# Main App
# ──────────────────────────────────────────────────────────────────────────────

class PyMaster:
    def __init__(self):
        self.console = Console()
        self.db_manager = DatabaseManager()
        self.validator = ChallengeValidator()
        self.current_user: Optional[str] = None
        self.session_id: Optional[str] = None
        self.challenges = self._load_challenges()

    def _load_challenges(self) -> List[Challenge]:
        challenges: List[Challenge] = []

        ch1 = CorePythonChallenge(
            "core_001", "Basic Function Implementation",
            "Implement a function that adds two numbers",
            1, "core_python", "functions"
        )
        ch1.add_test_case({'function': 'solution', 'args': [2, 3]}, 5)
        ch1.add_test_case({'function': 'solution', 'args': [-1, 1]}, 0)
        ch1.add_hint("Use the + operator")
        challenges.append(ch1)

        ch2 = DataStructuresChallenge(
            "ds_001", "List Comprehension Practice",
            "Create a list of even numbers doubled",
            3, "data_structures", "list_comprehension"
        )
        ch2.add_test_case({'function': 'solution', 'args': [[1, 2, 3, 4, 5]]}, [4, 8])
        ch2.add_test_case({'function': 'solution', 'args': [[1, 3, 5]]}, [])
        challenges.append(ch2)

        ch3 = OOPChallenge(
            "oop_001", "Class Implementation",
            "Create a class that processes input data",
            5, "object_oriented", "classes"
        )
        # NOTE: dotted target works (Solution().process)
        ch3.add_test_case({'function': 'Solution().process', 'args': ["test"]}, "Processed: test")
        challenges.append(ch3)

        return challenges

    def start(self):
        self.console.print(PYMASTER_ART, style="bold blue")
        self.console.print("\n[bold green]Welcome to PyMaster - Your Advanced Python Learning Assistant![/bold green]\n")
        self.current_user = Prompt.ask("[bold yellow]Enter your username[/bold yellow]") or "anonymous_user"
        self.session_id = self.db_manager.start_session(self.current_user)
        self._main_menu()

    def _main_menu(self):
        while True:
            self.console.print("\n[bold cyan]=== PyMaster Main Menu ===[/bold cyan]")
            self.console.print("1. Start Challenge")
            self.console.print("2. View Progress")
            self.console.print("3. Generate Report")
            self.console.print("4. Exit")
            self.console.print("5. Gamification Hub (XP & Badges)")
            self.console.print("6. Quest Campaign Mode")
            self.console.print("7. Arcade / Speedrun Mode")
            choice = Prompt.ask("[bold yellow]Select an option[/bold yellow]", choices=["1", "2", "3", "4", "5", "6", "7"])
            if choice == "1":
                self._start_challenge()
            elif choice == "2":
                self._view_progress()
            elif choice == "3":
                self._generate_report()
            elif choice == "4":
                self._exit()
                break
            elif choice == "5":
                pymaster_gamification.run_gamification_hub(self.console, self.db_manager, self.current_user)
            elif choice == "6":
                pymaster_quests.run_quest_campaign(self.console, self.db_manager, self.validator, self.current_user)
            elif choice == "7":
                pymaster_arcade.run_arcade_mode(self.console, self.db_manager, self.validator, self.current_user)

    def _start_challenge(self):
        self.console.print("\n[bold cyan]=== Available Challenges ===[/bold cyan]")
        for i, ch in enumerate(self.challenges, start=1):
            self.console.print(f"{i}. [bold]{ch.title}[/bold] (Difficulty: {ch.difficulty}/10)")
            self.console.print(f"   Module: {ch.module} | Concept: {ch.concept}")

        idx = int(Prompt.ask("[bold yellow]Select a challenge[/bold yellow]", choices=[str(i) for i in range(1, len(self.challenges)+1)]))
        challenge = self.challenges[idx - 1]

        self._run_challenge(challenge)

    def _run_challenge(self, challenge: Challenge):
        self.console.print(f"\n[bold green]Starting Challenge: {challenge.title}[/bold green]")
        self.console.print(f"[italic]{challenge.description}[/italic]\n")
        self.console.print(Panel(challenge.get_template(), title="Code Template", border_style="blue"))

        self.console.print("\n[bold yellow]Enter your solution (type 'END' alone on a line to finish):[/bold yellow]")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        user_code = "\n".join(lines).strip()
        if not user_code:
            self.console.print("[red]No code entered. Challenge cancelled.[/red]")
            return

        ok, syn_feedback = CodeAnalyzer.validate_syntax(user_code)
        if not ok:
            self.console.print("[red]Syntax Errors:[/red]")
            for e in syn_feedback:
                self.console.print(f"  [red]{e}[/red]")
            return

        passed, feedback = self.validator.validate_solution(user_code, challenge.test_cases, challenge.expected_outputs)
        self.console.print("\n[bold cyan]=== Test Results ===[/bold cyan]")
        for line in feedback:
            if line.startswith("✅"):
                self.console.print(f"[green]{line}[/green]")
            elif line.startswith("❌"):
                self.console.print(f"[red]{line}[/red]")
            elif line.startswith("🎉"):
                self.console.print(f"[bold green]{line}[/bold green]")
            else:
                self.console.print(line)

        pep8_score, pep8_fb = CodeAnalyzer.check_pep8(user_code)
        for item in pep8_fb:
            self.console.print(f"[dim]{item}[/dim]")

        # (Optional) simple perf timing via executor roundtrip
        start = time.time()
        _ = SafeCodeExecutor(timeout=5).execute(user_code)
        exec_time = time.time() - start
        perf_score = max(0.0, 1.0 - min(exec_time / 2.0, 1.0))  # naive scoring

        result = ChallengeResult(
            challenge_id=challenge.challenge_id,
            user_code=user_code,
            passed=passed,
            syntax_valid=True,
            performance_score=perf_score,
            pep8_score=pep8_score,
            execution_time=exec_time,
            feedback=feedback + pep8_fb
        )
        self.db_manager.save_challenge_result(result, self.current_user)
        self._update_progress(challenge, passed)

    def _update_progress(self, challenge: Challenge, passed: bool):
        prog = self.db_manager.get_user_progress(self.current_user, challenge.module, challenge.concept)
        if prog:
            p = prog[0]
            p.attempts += 1
            if passed:
                p.correct_attempts += 1
                p.mastery_level = min(1.0, p.mastery_level + 0.1)
            p.last_attempt = datetime.now()
        else:
            p = UserProgress(
                user_id=self.current_user,
                module=challenge.module,
                concept=challenge.concept,
                attempts=1,
                correct_attempts=1 if passed else 0,
                last_attempt=datetime.now(),
                mastery_level=0.1 if passed else 0.0
            )
        self.db_manager.save_progress(p)

    def _view_progress(self):
        self.console.print("\n[bold cyan]=== Your Progress ===[/bold cyan]")
        items = self.db_manager.get_user_progress(self.current_user)
        if not items:
            self.console.print("[yellow]No progress yet.[/yellow]")
            return
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Module", style="cyan")
        table.add_column("Concept", style="green")
        table.add_column("Attempts", style="yellow")
        table.add_column("Success Rate", style="blue")
        table.add_column("Mastery", style="red")
        for pr in items:
            sr = (pr.correct_attempts / pr.attempts * 100) if pr.attempts else 0
            table.add_row(pr.module, pr.concept, str(pr.attempts), f"{sr:.1f}%", f"{pr.get_mastery_percentage()}%")
        self.console.print(table)

        stats = self.db_manager.get_user_stats(self.current_user)
        self.console.print(f"\n[bold]Overall Stats:[/bold]")
        self.console.print(f"Total Challenges: {stats['total_challenges']}")
        self.console.print(f"Success Rate: {stats['success_rate']:.1f}%")
        self.console.print(f"Average PEP8 Score: {stats['avg_pep8_score']:.1f}%")

    def _generate_report(self):
        self.console.print("\n[bold cyan]=== Generating Report ===[/bold cyan]")
        reports_dir = Path(CONFIG['REPORTS_DIR'])
        reports_dir.mkdir(exist_ok=True)

        progress_list = self.db_manager.get_user_progress(self.current_user)
        stats = self.db_manager.get_user_stats(self.current_user)

        content = f"""# PyMaster Progress Report

## User: {self.current_user}
## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Statistics
- Total Challenges: {stats['total_challenges']}
- Success Rate: {stats['success_rate']:.1f}%
- Average PEP8 Score: {stats['avg_pep8_score']:.1f}%
- Average Performance Score: {stats['avg_performance_score']:.1f}%
- Average Execution Time: {stats['avg_execution_time']:.3f}s
- Total Sessions: {stats['total_sessions']}

## Progress by Module/Concept
"""
        for p in progress_list:
            sr = (p.correct_attempts / p.attempts * 100) if p.attempts else 0
            content += f"- {p.module}/{p.concept}: {p.attempts} attempts, {sr:.1f}% success, {p.get_mastery_percentage()}% mastery\n"

        fname = reports_dir / f"pymaster_report_{self.current_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
        self.console.print(f"[green]Report saved to: {fname}[/green]")

    def _exit(self):
        if self.session_id:
            self.db_manager.end_session(self.session_id, 0)
        self.console.print("\n[bold green]Thank you for using PyMaster! Arrivederci![/bold green]")


def main():
    try:
        app = PyMaster()
        app.start()
    except KeyboardInterrupt:
        print("\n\nPyMaster interrupted. Arrivederci!")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
