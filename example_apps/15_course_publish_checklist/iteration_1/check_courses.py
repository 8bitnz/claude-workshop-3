#!/usr/bin/env python3
"""check_courses.py — validate course JSON files against a publishing checklist.

Standard library only.

Reads a folder of course definition files (one .json file per course) and
checks each one against a set of publishing-readiness rules: has a syllabus,
has at least one module, every module has content and learning objectives,
and assessment weights sum to exactly 100. Prints a per-course PASS/FAIL
report plus a final summary, and exits non-zero if any course fails.

Examples:
    python3 check_courses.py                  # checks ./courses
    python3 check_courses.py --path ~/my_courses
"""
import argparse
import json
import os
import sys


def check_course(course):
    """Return a list of issue strings for a course dict. Empty list = pass."""
    issues = []

    if not course.get("has_syllabus"):
        issues.append("Missing syllabus")

    modules = course.get("modules") or []
    if not modules:
        issues.append("Course has no modules")

    for module in modules:
        name = module.get("title", "(untitled module)")
        if not module.get("has_content"):
            issues.append(f"Module '{name}' missing content")
        if not module.get("has_learning_objectives"):
            issues.append(f"Module '{name}' missing learning objectives")

    weights = course.get("assessment_weights") or {}
    total = sum(weights.values()) if weights else 0
    if not weights:
        issues.append("No assessment weights defined")
    elif total != 100:
        issues.append(f"Assessment weights sum to {total}, not 100")

    return issues


def build_parser():
    p = argparse.ArgumentParser(
        description="Check course JSON files against a publishing-readiness checklist.")
    p.add_argument("--path", default="./courses",
                    help="Folder containing course .json files (default: ./courses).")
    return p


def load_courses(folder):
    """Return sorted list of (filename, data_or_None, error_or_None)."""
    results = []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".json"):
            continue
        full = os.path.join(folder, name)
        try:
            with open(full) as f:
                data = json.load(f)
            results.append((name, data, None))
        except (json.JSONDecodeError, OSError) as e:
            results.append((name, None, str(e)))
    return results


def run(args):
    folder = os.path.abspath(os.path.expanduser(args.path))
    if not os.path.isdir(folder):
        print(f"Error: {folder} is not a directory.", file=sys.stderr)
        return 1

    courses = load_courses(folder)
    if not courses:
        print(f"No .json course files found in {folder}.")
        return 0

    print(f"Checking {len(courses)} course(s) in {folder}\n")

    passed = 0
    failed = 0
    for filename, data, error in courses:
        if error is not None:
            print(f"FAIL  {filename}")
            print(f"      Could not read file: {error}")
            failed += 1
            continue

        title = data.get("title", filename)
        issues = check_course(data)
        if issues:
            print(f"FAIL  {title} ({filename})")
            for issue in issues:
                print(f"      - {issue}")
            failed += 1
        else:
            print(f"PASS  {title} ({filename})")
            passed += 1

    total = passed + failed
    print(f"\n{passed}/{total} courses ready to publish")
    return 0 if failed == 0 else 1


def main(argv=None):
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
