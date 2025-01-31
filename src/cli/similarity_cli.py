"""Command-line interface for code similarity analysis."""

import argparse
import glob
import json
import os
from typing import Dict, List, Tuple

from src.analyzers.similarity_analyzer import (
    CodeFragment,
    SimilarityAnalyzer
)

def collect_python_files(paths: List[str]) -> List[str]:
    """Collect all Python files from the given paths."""
    python_files = []
    for path in paths:
        if os.path.isfile(path) and path.endswith('.py'):
            python_files.append(path)
        elif os.path.isdir(path):
            python_files.extend(
                glob.glob(os.path.join(path, '**/*.py'), recursive=True)
            )
    return python_files

def format_results(results: Dict[str, List[Tuple[CodeFragment, float]]]) -> Dict:
    """Format analysis results for JSON output."""
    formatted = {}
    for key, fragments in results.items():
        formatted[key] = [
            {
                'file': fragment.location.file_path,
                'start_line': fragment.location.start_line,
                'end_line': fragment.location.end_line,
                'type': fragment.type.value,
                'similarity': score,
                'source': fragment.source
            }
            for fragment, score in fragments
        ]
    return formatted

def main():
    """Main entry point for the similarity analyzer CLI."""
    parser = argparse.ArgumentParser(
        description='Analyze Python code for similar patterns.'
    )
    parser.add_argument(
        'paths',
        nargs='+',
        help='Paths to Python files or directories to analyze'
    )
    parser.add_argument(
        '--min-lines',
        type=int,
        default=5,
        help='Minimum number of lines for code fragments (default: 5)'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.8,
        help='Similarity threshold (0.0-1.0, default: 0.8)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    args = parser.parse_args()
    
    # Collect Python files
    python_files = collect_python_files(args.paths)
    if not python_files:
        print("No Python files found in the specified paths.")
        return
    
    # Initialize and run analyzer
    analyzer = SimilarityAnalyzer(
        min_fragment_size=args.min_lines,
        similarity_threshold=args.threshold
    )
    results = analyzer.analyze(python_files)
    
    # Output results
    if args.json:
        formatted = format_results(results)
        print(json.dumps(formatted, indent=2))
    else:
        for key, fragments in results.items():
            print(f"\nSimilar code found in {key}:")
            for fragment, score in fragments:
                print(f"\n  Similar to {fragment.location.file_path}:"
                      f"{fragment.location.start_line}-{fragment.location.end_line}")
                print(f"  Type: {fragment.type.value}")
                print(f"  Similarity: {score:.2f}")
                print("  Code:")
                for line in fragment.source.splitlines():
                    print(f"    {line}")

if __name__ == '__main__':
    main() 