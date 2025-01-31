#!/usr/bin/env python3
"""
Script to validate code quality of listed projects.
"""

import sys
import warnings
from pathlib import Path
import yaml
from typing import Dict, Any
import colorama
from colorama import Fore, Style

from code_analyzer.analyzers.dead_code_analyzer import DeadCodeAnalyzer
from code_analyzer.analyzers.complexity_analyzer import ComplexityAnalyzer
from code_analyzer.config.config_loader import Config, DeadCodeConfig, ComplexityConfig, AnalysisConfig


def load_validation_config():
    config_path = Path("validate-against.yaml")
    if not config_path.exists():
        print(f"Error: {config_path} not found")
        sys.exit(1)
    
    with open(config_path) as f:
        return yaml.safe_load(f)


def validate_project(project: Dict[str, Any], global_settings: Dict[str, Any]) -> bool:
    project_path = Path(project["path"]).expanduser()
    if not project_path.exists():
        print(f"{Fore.RED}Project path does not exist: {project_path}{Style.RESET_ALL}")
        return False

    print(f"\n{Fore.CYAN}Validating {project['name']}{Style.RESET_ALL}")
    print("=" * 80)
    
    # Suppress syntax warnings during validation
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=SyntaxWarning)
        
        config = Config()
        config.search_paths = [project_path]
        config.analysis = AnalysisConfig()
        
        # Configure dead code analysis
        config.analysis.dead_code = DeadCodeConfig()
        config.analysis.dead_code.ignore_patterns = global_settings["ignore_patterns"]
        config.analysis.dead_code.ignore_private = global_settings["dead_code"]["ignore_private"]
        config.analysis.dead_code.ignore_names = global_settings["dead_code"]["ignore_names"]
        
        # Configure complexity analysis
        config.analysis.complexity = ComplexityConfig()
        config.analysis.complexity.min_complexity = project["complexity_threshold"]
        
        # Run dead code analysis
        dead_code_analyzer = DeadCodeAnalyzer(config)
        unused_symbols = dead_code_analyzer.analyze()
        
        if unused_symbols:
            print(f"\n{Fore.YELLOW}Found {len(unused_symbols)} unused symbols:{Style.RESET_ALL}")
            for symbol in unused_symbols:
                print(f"  - {symbol.name} ({symbol.type.value}) at {symbol.location}")
        
        # Run complexity analysis
        complexity_analyzer = ComplexityAnalyzer(config)
        complex_functions = complexity_analyzer.analyze()
        
        if complex_functions:
            print(f"\n{Fore.YELLOW}Found {len(complex_functions)} functions exceeding " 
                  f"complexity threshold ({project['complexity_threshold']}):{Style.RESET_ALL}")
            for func in complex_functions:
                if func.complexity >= project["complexity_threshold"]:
                    print(f"  - {func.name} (complexity: {func.complexity}) at {func.location}")
        
        has_issues = bool(unused_symbols) or any(
            func.complexity >= project["complexity_threshold"] for func in complex_functions
        )
        
        if has_issues:
            print(f"\n{Fore.RED}✗ Some checks failed{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}✓ All checks passed{Style.RESET_ALL}")
        
        return has_issues


def main():
    """Main entry point."""
    colorama.init()
    
    validation_config = load_validation_config()
    projects = validation_config.get("projects", [])
    settings = validation_config.get("settings", {})
    
    if not projects:
        print("No projects configured for validation")
        sys.exit(1)
    
    found_issues = False
    for project in projects:
        if validate_project(project, settings):
            found_issues = True
    
    if found_issues:
        print(f"\n{Fore.RED}Found code quality issues in one or more projects{Style.RESET_ALL}")
        sys.exit(1)
    else:
        print(f"\n{Fore.GREEN}All projects passed validation!{Style.RESET_ALL}")


if __name__ == '__main__':
    main() 