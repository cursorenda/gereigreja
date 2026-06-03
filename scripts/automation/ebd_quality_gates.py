import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable
SETTINGS = os.getenv('EBD_TEST_SETTINGS', 'core.settings_test')
MIN_EBD_TESTS = int(os.getenv('MIN_EBD_TESTS', '12'))

# These tests are the release gates for critical EBD behavior.
REQUIRED_TEST_MARKERS = [
    'test_get_chamada_respeita_orcamento_queries',
    'test_get_dashboard_respeita_orcamento_queries',
    'test_carga_get_chamada_turma_grande_periodo_extenso',
    'test_carga_get_dashboard_periodo_extenso',
    'test_chamada_post_duplicado_e_ignorado_por_idempotencia',
    'test_chamada_post_concorrente_e_ignorado_por_processing_lock',
]


def run_cmd(args):
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.stdout:
        print(proc.stdout, end='')
    if proc.stderr:
        print(proc.stderr, end='', file=sys.stderr)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.stdout + proc.stderr


def assert_ran_tests(output):
    match = re.search(r'Ran\s+(\d+)\s+tests?', output)
    if not match:
        raise SystemExit('Quality gate failed: unable to parse total tests executed.')

    total = int(match.group(1))
    if total < MIN_EBD_TESTS:
        raise SystemExit(
            f'Quality gate failed: expected at least {MIN_EBD_TESTS} EBD tests, got {total}.'
        )


def assert_required_markers(output):
    missing = [name for name in REQUIRED_TEST_MARKERS if name not in output]
    if missing:
        missing_str = ', '.join(missing)
        raise SystemExit(
            'Quality gate failed: required critical tests not found in execution output: '
            f'{missing_str}'
        )


def main():
    print('==> EBD quality gate: django check')
    run_cmd([PYTHON, 'manage.py', 'check', f'--settings={SETTINGS}'])

    print('==> EBD quality gate: focused regression suite')
    output = run_cmd(
        [
            PYTHON,
            'manage.py',
            'test',
            'escola_biblica.tests.test_pontos_ebd',
            'escola_biblica.tests.test_chamada_fluxo',
            f'--settings={SETTINGS}',
            '-v',
            '2',
        ]
    )

    assert_ran_tests(output)
    assert_required_markers(output)
    print('==> EBD quality gates passed')


if __name__ == '__main__':
    main()
