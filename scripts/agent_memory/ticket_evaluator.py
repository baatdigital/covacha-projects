"""Sistema de auto-evaluacion de tickets para el Agent Swarm.

Ejecuta quality gates automaticos antes de release, QA review,
PO acceptance y post-merge. Cada evaluacion retorna EvalResult
con checks individuales.
"""
import os
import re
import subprocess
from dataclasses import dataclass, field


@dataclass
class EvalCheck:
    """Resultado de un check individual."""

    name: str
    passed: bool
    detail: str = ""


@dataclass
class EvalResult:
    """Resultado completo de una evaluacion."""

    task_id: str
    evaluation_type: str
    passed: bool
    checks: list[EvalCheck] = field(default_factory=list)
    summary: str = ""


# Timeout para subprocess (segundos)
CMD_TIMEOUT: int = 120


class TicketEvaluator:
    """Evalua si un ticket cumple quality gates automaticos."""

    def evaluate(
        self,
        task_id: str,
        eval_type: str,
        repo_path: str | None = None,
        pr_url: str | None = None,
    ) -> EvalResult:
        """Dispatcher que llama al metodo correcto segun eval_type."""
        dispatch = {
            "pre_release": self._eval_pre_release,
            "qa_review": self._eval_qa_review,
            "po_acceptance": self._eval_po_acceptance,
            "post_merge": self._eval_post_merge,
        }
        handler = dispatch.get(eval_type)
        if handler is None:
            return EvalResult(
                task_id=task_id,
                evaluation_type=eval_type,
                passed=False,
                summary=f"Tipo de evaluacion invalido: {eval_type}",
            )
        return handler(task_id=task_id, repo_path=repo_path)

    # ── Pre-release ──────────────────────────────────────────

    def _eval_pre_release(
        self, task_id: str, repo_path: str | None = None
    ) -> EvalResult:
        """Evaluacion antes de hacer release_task."""
        if not repo_path:
            return self._missing_repo(task_id, "pre_release")

        checks = [
            self._check_tests_pass(repo_path),
            self._check_coverage(repo_path),
            self._check_lint(repo_path),
            self._check_no_large_files(repo_path),
            self._check_no_large_functions(repo_path),
            self._check_type_hints(repo_path),
            self._check_commit_format(repo_path),
            self._check_branch_pushed(repo_path),
            self._check_no_secrets(repo_path),
        ]
        return self._build_result(task_id, "pre_release", checks)

    # ── QA Review ────────────────────────────────────────────

    def _eval_qa_review(
        self, task_id: str, repo_path: str | None = None
    ) -> EvalResult:
        """Evaluacion QA: tests cubren happy path y errores."""
        if not repo_path:
            return self._missing_repo(task_id, "qa_review")

        checks = [
            self._check_test_files_exist(repo_path),
            self._check_happy_path_tests(repo_path),
            self._check_error_case_tests(repo_path),
            self._check_no_hardcoded_data(repo_path),
        ]
        return self._build_result(task_id, "qa_review", checks)

    # ── PO Acceptance ────────────────────────────────────────

    def _eval_po_acceptance(
        self, task_id: str, repo_path: str | None = None
    ) -> EvalResult:
        """Evaluacion de criterios de aceptacion por PO."""
        checks = [
            self._check_checklist_complete(task_id),
            self._check_tests_pass(repo_path) if repo_path else EvalCheck(
                name="tests_pass", passed=True, detail="Sin repo, skip"
            ),
            self._check_no_pending_todos(task_id, repo_path),
        ]
        return self._build_result(task_id, "po_acceptance", checks)

    # ── Post-merge ───────────────────────────────────────────

    def _eval_post_merge(
        self, task_id: str, repo_path: str | None = None
    ) -> EvalResult:
        """Evaluacion despues de merge a main."""
        if not repo_path:
            return self._missing_repo(task_id, "post_merge")

        checks = [
            self._check_main_updated(repo_path),
            self._check_tests_pass_main(repo_path),
            self._check_no_merge_conflicts(repo_path),
        ]
        return self._build_result(task_id, "post_merge", checks)

    # ── Checks individuales (pre-release) ────────────────────

    def _check_tests_pass(self, repo_path: str) -> EvalCheck:
        """Ejecuta pytest y verifica exit_code == 0."""
        result = self._run(["pytest", "-v", "--tb=short"], repo_path)
        return EvalCheck(
            name="tests_pass",
            passed=result.returncode == 0,
            detail=result.stdout[-500:] if result.stdout else result.stderr[-500:],
        )

    def _check_coverage(self, repo_path: str) -> EvalCheck:
        """Ejecuta pytest --cov y verifica coverage >= 98%."""
        result = self._run(
            ["pytest", "--cov", "--cov-report=term-missing"], repo_path
        )
        coverage = self._parse_coverage(result.stdout or "")
        return EvalCheck(
            name="coverage_98",
            passed=coverage >= 98.0,
            detail=f"{coverage}%",
        )

    def _check_lint(self, repo_path: str) -> EvalCheck:
        """Ejecuta ruff check y verifica exit_code == 0."""
        result = self._run(["ruff", "check", "."], repo_path)
        return EvalCheck(
            name="lint_clean",
            passed=result.returncode == 0,
            detail=result.stdout[-500:] if result.stdout else "",
        )

    def _check_no_large_files(self, repo_path: str) -> EvalCheck:
        """Busca archivos .py con mas de 1000 lineas."""
        large: list[str] = []
        for root, _dirs, files in os.walk(repo_path):
            if ".git" in root or "__pycache__" in root:
                continue
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                fpath = os.path.join(root, fname)
                count = self._count_lines(fpath)
                if count > 1000:
                    large.append(f"{fpath}:{count}")
        return EvalCheck(
            name="no_large_files",
            passed=len(large) == 0,
            detail=", ".join(large) if large else "OK",
        )

    def _check_no_large_functions(self, repo_path: str) -> EvalCheck:
        """Busca funciones con mas de 50 lineas (regex simple)."""
        large: list[str] = []
        for root, _dirs, files in os.walk(repo_path):
            if ".git" in root or "__pycache__" in root:
                continue
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                fpath = os.path.join(root, fname)
                large.extend(self._find_large_functions(fpath))
        return EvalCheck(
            name="no_large_functions",
            passed=len(large) == 0,
            detail=", ".join(large) if large else "OK",
        )

    def _check_type_hints(self, repo_path: str) -> EvalCheck:
        """Busca funciones sin type hints en archivos modificados."""
        result = self._run(
            ["git", "diff", "--name-only", "HEAD~1"], repo_path
        )
        files = [
            f for f in (result.stdout or "").strip().split("\n")
            if f.endswith(".py")
        ]
        missing: list[str] = []
        for fname in files:
            fpath = os.path.join(repo_path, fname)
            if os.path.exists(fpath):
                missing.extend(self._find_missing_hints(fpath))
        return EvalCheck(
            name="type_hints",
            passed=len(missing) == 0,
            detail=", ".join(missing) if missing else "OK",
        )

    def _check_commit_format(self, repo_path: str) -> EvalCheck:
        """Verifica ultimo commit matchea formato obligatorio."""
        result = self._run(
            ["git", "log", "-1", "--format=%s"], repo_path
        )
        msg = (result.stdout or "").strip()
        pattern = r"^(feat|fix|refactor|docs|test|chore|perf|style)\(ISS-\d+\):"
        valid = bool(re.match(pattern, msg))
        return EvalCheck(
            name="commit_format",
            passed=valid,
            detail=msg,
        )

    def _check_branch_pushed(self, repo_path: str) -> EvalCheck:
        """Verifica que la branch local esta pusheada."""
        result = self._run(
            ["git", "status", "-sb"], repo_path
        )
        output = result.stdout or ""
        # Si tiene "ahead" significa que hay commits no pusheados
        is_pushed = "ahead" not in output
        return EvalCheck(
            name="branch_pushed",
            passed=is_pushed,
            detail=output.strip().split("\n")[0] if output else "",
        )

    def _check_no_secrets(self, repo_path: str) -> EvalCheck:
        """Busca patrones de secrets en archivos staged."""
        result = self._run(
            ["git", "diff", "--cached", "--name-only"], repo_path
        )
        staged = [
            f for f in (result.stdout or "").strip().split("\n") if f
        ]
        found: list[str] = []
        patterns = [
            r"API_KEY\s*=\s*['\"]",
            r"password\s*=\s*['\"]",
            r"token\s*=\s*['\"]",
            r"SECRET\s*=\s*['\"]",
        ]
        for fname in staged:
            fpath = os.path.join(repo_path, fname)
            if not os.path.exists(fpath):
                continue
            try:
                with open(fpath, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                for pat in patterns:
                    if re.search(pat, content, re.IGNORECASE):
                        found.append(f"{fname}: matches {pat}")
            except OSError:
                continue
        # Tambien buscar archivos .env staged
        env_files = [f for f in staged if f.endswith(".env") or ".env." in f]
        found.extend([f"{f}: archivo .env" for f in env_files])
        return EvalCheck(
            name="no_secrets",
            passed=len(found) == 0,
            detail=", ".join(found) if found else "OK",
        )

    # ── Checks individuales (QA review) ──────────────────────

    def _check_test_files_exist(self, repo_path: str) -> EvalCheck:
        """Verifica que archivos modificados tienen test correspondiente."""
        result = self._run(
            ["git", "diff", "--name-only", "HEAD~1"], repo_path
        )
        files = [
            f for f in (result.stdout or "").strip().split("\n")
            if f.endswith(".py") and not f.startswith("test_")
            and "/tests/" not in f
        ]
        missing: list[str] = []
        for fname in files:
            base = os.path.basename(fname)
            test_name = f"test_{base}"
            if not self._find_test_file(repo_path, test_name):
                missing.append(fname)
        return EvalCheck(
            name="test_files_exist",
            passed=len(missing) == 0,
            detail=", ".join(missing) if missing else "OK",
        )

    def _check_happy_path_tests(self, repo_path: str) -> EvalCheck:
        """Busca tests de happy path en archivos de test."""
        pattern = r"test_.*(?:exitoso|success|ok|correcto)"
        return self._check_test_pattern(
            repo_path, "happy_path_tests", pattern
        )

    def _check_error_case_tests(self, repo_path: str) -> EvalCheck:
        """Busca tests de caso de error en archivos de test."""
        pattern = r"test_.*(?:error|falla|invalid|sin_)"
        return self._check_test_pattern(
            repo_path, "error_case_tests", pattern
        )

    def _check_no_hardcoded_data(self, repo_path: str) -> EvalCheck:
        """Busca datos hardcodeados en tests (IPs, URLs)."""
        found: list[str] = []
        patterns = [
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
            r"http://(?!localhost|127\.0\.0\.1)",
            r"https://(?!example\.com|test\.)",
        ]
        tests_dir = os.path.join(repo_path, "tests")
        if not os.path.isdir(tests_dir):
            return EvalCheck(
                name="no_hardcoded_data", passed=True, detail="Sin dir tests"
            )
        for root, _dirs, files in os.walk(tests_dir):
            for fname in files:
                if not fname.startswith("test_"):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, encoding="utf-8") as f:
                        content = f.read()
                    for pat in patterns:
                        matches = re.findall(pat, content)
                        if matches:
                            found.append(f"{fname}: {matches[0]}")
                except OSError:
                    continue
        return EvalCheck(
            name="no_hardcoded_data",
            passed=len(found) == 0,
            detail=", ".join(found) if found else "OK",
        )

    # ── Checks individuales (PO acceptance) ──────────────────

    def _check_checklist_complete(self, task_id: str) -> EvalCheck:
        """Verifica checklist del issue (busca - [ ] vs - [x])."""
        result = self._run_global(
            ["gh", "issue", "view", task_id, "--json", "body", "-q", ".body"]
        )
        body = result.stdout or ""
        unchecked = len(re.findall(r"- \[ \]", body))
        checked = len(re.findall(r"- \[x\]", body, re.IGNORECASE))
        total = unchecked + checked
        if total == 0:
            return EvalCheck(
                name="checklist_complete",
                passed=True,
                detail="Sin checklist en el issue",
            )
        return EvalCheck(
            name="checklist_complete",
            passed=unchecked == 0,
            detail=f"{checked}/{total} completados",
        )

    def _check_no_pending_todos(
        self, task_id: str, repo_path: str | None
    ) -> EvalCheck:
        """Busca TODO(ISS-{task_id}) sin resolver en el repo."""
        if not repo_path:
            return EvalCheck(
                name="no_pending_todos", passed=True, detail="Sin repo"
            )
        result = self._run(
            ["grep", "-r", f"TODO(ISS-{task_id})", "--include=*.py", "."],
            repo_path,
        )
        matches = (result.stdout or "").strip()
        found = [l for l in matches.split("\n") if l.strip()]
        return EvalCheck(
            name="no_pending_todos",
            passed=len(found) == 0,
            detail=", ".join(found[:5]) if found else "OK",
        )

    # ── Checks individuales (post-merge) ─────────────────────

    def _check_main_updated(self, repo_path: str) -> EvalCheck:
        """Verifica que main esta actualizada."""
        result = self._run(
            ["git", "pull", "--dry-run"], repo_path
        )
        output = (result.stdout or "") + (result.stderr or "")
        up_to_date = (
            "Already up to date" in output
            or "Already up-to-date" in output
            or result.returncode == 0
        )
        return EvalCheck(
            name="main_updated",
            passed=up_to_date,
            detail=output.strip()[:200],
        )

    def _check_tests_pass_main(self, repo_path: str) -> EvalCheck:
        """Ejecuta tests en main."""
        check = self._check_tests_pass(repo_path)
        check.name = "tests_pass_main"
        return check

    def _check_no_merge_conflicts(self, repo_path: str) -> EvalCheck:
        """Busca marcadores de conflicto de merge."""
        result = self._run(
            ["grep", "-r", "<<<<<<< ", "--include=*.py", "."],
            repo_path,
        )
        found = (result.stdout or "").strip()
        has_conflicts = bool(found)
        return EvalCheck(
            name="no_merge_conflicts",
            passed=not has_conflicts,
            detail=found[:200] if has_conflicts else "OK",
        )

    # ── Helpers ───────────────────────────────────────────────

    def _run(
        self, cmd: list[str], cwd: str
    ) -> subprocess.CompletedProcess:
        """Ejecuta un comando en el directorio dado."""
        try:
            return subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=CMD_TIMEOUT,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            return subprocess.CompletedProcess(
                args=cmd, returncode=1, stdout="", stderr=str(exc)
            )

    def _run_global(
        self, cmd: list[str]
    ) -> subprocess.CompletedProcess:
        """Ejecuta un comando sin cwd especifico."""
        try:
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=CMD_TIMEOUT,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            return subprocess.CompletedProcess(
                args=cmd, returncode=1, stdout="", stderr=str(exc)
            )

    @staticmethod
    def _parse_coverage(output: str) -> float:
        """Parsea el porcentaje de coverage del output de pytest --cov."""
        # Busca "TOTAL ... XX%" al final
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
        if match:
            return float(match.group(1))
        # Fallback: busca cualquier "XX%"
        matches = re.findall(r"(\d+)%", output)
        if matches:
            return float(matches[-1])
        return 0.0

    @staticmethod
    def _count_lines(fpath: str) -> int:
        """Cuenta lineas de un archivo."""
        try:
            with open(fpath, encoding="utf-8", errors="ignore") as f:
                return sum(1 for _ in f)
        except OSError:
            return 0

    @staticmethod
    def _find_large_functions(fpath: str) -> list[str]:
        """Encuentra funciones con mas de 50 lineas."""
        large: list[str] = []
        try:
            with open(fpath, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except OSError:
            return []
        func_name: str | None = None
        func_start: int = 0
        for i, line in enumerate(lines):
            match = re.match(r"^(\s*)def (\w+)", line)
            if match:
                if func_name is not None:
                    length = i - func_start
                    if length > 50:
                        large.append(f"{fpath}:{func_name}({length}L)")
                func_name = match.group(2)
                func_start = i
        # Ultima funcion
        if func_name is not None:
            length = len(lines) - func_start
            if length > 50:
                large.append(f"{fpath}:{func_name}({length}L)")
        return large

    @staticmethod
    def _find_missing_hints(fpath: str) -> list[str]:
        """Encuentra funciones sin return type hint."""
        missing: list[str] = []
        try:
            with open(fpath, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except OSError:
            return []
        # Busca 'def func(...)' sin '->'
        pattern = r"def (\w+)\([^)]*\)\s*:"
        for match in re.finditer(pattern, content):
            full = content[match.start():match.end()]
            if "->" not in full and match.group(1) != "__init__":
                missing.append(f"{fpath}:{match.group(1)}")
        return missing

    @staticmethod
    def _find_test_file(repo_path: str, test_name: str) -> bool:
        """Busca si existe un archivo de test en el repo."""
        for root, _dirs, files in os.walk(repo_path):
            if ".git" in root:
                continue
            if test_name in files:
                return True
        return False

    def _check_test_pattern(
        self, repo_path: str, check_name: str, pattern: str
    ) -> EvalCheck:
        """Verifica que al menos un test matchea el patron dado."""
        tests_dir = os.path.join(repo_path, "tests")
        if not os.path.isdir(tests_dir):
            return EvalCheck(
                name=check_name, passed=False, detail="Sin dir tests"
            )
        found = False
        for root, _dirs, files in os.walk(tests_dir):
            for fname in files:
                if not fname.startswith("test_"):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, encoding="utf-8") as f:
                        content = f.read()
                    if re.search(pattern, content):
                        found = True
                        break
                except OSError:
                    continue
            if found:
                break
        return EvalCheck(
            name=check_name,
            passed=found,
            detail="OK" if found else f"No se encontro patron: {pattern}",
        )

    @staticmethod
    def _missing_repo(task_id: str, eval_type: str) -> EvalResult:
        """Retorna resultado de error cuando falta repo_path."""
        return EvalResult(
            task_id=task_id,
            evaluation_type=eval_type,
            passed=False,
            summary="repo_path es requerido para esta evaluacion",
        )

    @staticmethod
    def _build_result(
        task_id: str, eval_type: str, checks: list[EvalCheck]
    ) -> EvalResult:
        """Construye EvalResult a partir de lista de checks."""
        passed = all(c.passed for c in checks)
        failed = [c.name for c in checks if not c.passed]
        if passed:
            summary = f"Todos los checks pasaron ({len(checks)})"
        else:
            summary = f"Fallaron {len(failed)}/{len(checks)}: {', '.join(failed)}"
        return EvalResult(
            task_id=task_id,
            evaluation_type=eval_type,
            passed=passed,
            checks=checks,
            summary=summary,
        )
