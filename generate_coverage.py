import json

data = json.load(open('htmlcov/status.json'))
files = data['files']

total_stmts = 0
total_missing = 0

print('File'.ljust(50) + 'Stmts'.rjust(8) + 'Missing'.rjust(10) + 'Pct'.rjust(6))
print('-' * 74)

for k, v in files.items():
    idx = v.get('index', {})
    nums = idx.get('nums', {})
    s = nums.get('n_statements', 0)
    m = nums.get('n_missing', 0)
    pct = round((s - m) / s * 100) if s > 0 else 100
    total_stmts += s
    total_missing += m
    name = v.get('file', k).replace('\\', '/')
    print(f'{name:50s}{s:8d}{m:10d}{pct:5d}%')

print(f'\nTOTAL: {total_stmts} statements, {total_missing} missing, {round((total_stmts-total_missing)/total_stmts*100)}% coverage')

# Save to file for reference
import os
os.makedirs('.copilot-tracking/reports', exist_ok=True)
with open('.copilot-tracking/reports/coverage-report.md', 'w') as f:
    f.write("# Test Coverage Report\n\n")
    f.write(f"**Generated**: 2026-09-23\n")
    f.write(f"**Overall Coverage**: {round((total_stmts-total_missing)/total_stmts*100)}%\n\n")
    f.write("## Per-File Coverage\n\n")
    f.write("| File | Statements | Missing | Coverage |\n")
    f.write("|------|-----------|---------|----------|\n")
    for k, v in files.items():
        idx = v.get('index', {})
        nums = idx.get('nums', {})
        s = nums.get('n_statements', 0)
        m = nums.get('n_missing', 0)
        pct = round((s - m) / s * 100) if s > 0 else 100
        name = v.get('file', k).replace('\\', '/')
        f.write(f"| {name} | {s} | {m} | {pct}% |\n")

print("\nReport saved to .copilot-tracking/reports/coverage-report.md")
