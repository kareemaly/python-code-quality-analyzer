"""
Similarity analyzer for detecting similar code patterns.
Uses Locality Sensitive Hashing (LSH) for efficient similarity detection.
"""

import ast
from dataclasses import dataclass
from enum import Enum
import tokenize
from typing import List, Set, Dict, Optional, Tuple, Any
import hashlib
from pathlib import Path
import io

from .base_analyzer import BaseAnalyzer


class FragmentType(Enum):
    """Types of code fragments that can be analyzed for similarity."""
    CLASS = "class"
    FUNCTION = "function" 
    METHOD = "method"
    BLOCK = "block"


@dataclass(frozen=True)
class Location:
    """Location of a code fragment in source code."""
    file_path: str
    start_line: int
    end_line: int


@dataclass(frozen=True)
class Token:
    """Normalized token used for similarity comparison."""
    type: str
    value: str
    
    def __hash__(self):
        return hash((self.type, self.value))


@dataclass(frozen=True)
class CodeFragment:
    """A fragment of code to analyze for similarity."""
    type: FragmentType
    location: Location
    source: str
    tokens: Optional[Tuple[Token, ...]] = None
    hash: Optional[str] = None
    
    def __hash__(self):
        if self.hash is not None:
            return hash(self.hash)
        return hash((self.type, self.location, self.source))
    
    def __eq__(self, other):
        if not isinstance(other, CodeFragment):
            return False
        if self.hash is not None and other.hash is not None:
            return self.hash == other.hash
        return (self.type == other.type and 
                self.location == other.location and 
                self.source == other.source)


class TokenProcessor:
    """Process and normalize tokens for similarity comparison."""
    
    def __init__(self):
        self.name_counter = 0
        self.name_map: Dict[str, str] = {}
        
    def normalize_name(self, name: str) -> str:
        """Normalize variable/function names to generic placeholders."""
        if name not in self.name_map:
            self.name_map[name] = f"NAME_{self.name_counter}"
            self.name_counter += 1
        return self.name_map[name]
    
    def process(self, source: str) -> List[Token]:
        """Process source code into normalized tokens."""
        tokens = []
        try:
            # Normalize whitespace and remove comments
            lines = [line.strip() for line in source.splitlines()]
            source = "\n".join(line for line in lines if line and not line.startswith('#'))
            
            # Process tokens
            for tok in tokenize.generate_tokens(io.StringIO(source).readline):
                token_type = tok.type
                token_value = tok.string.strip()
                
                # Skip whitespace and empty tokens
                if not token_value or token_type in (tokenize.NEWLINE, tokenize.INDENT, 
                                                   tokenize.DEDENT, tokenize.NL, 
                                                   tokenize.COMMENT):
                    continue
                
                # Normalize based on token type
                if token_type == tokenize.NAME:
                    # Keep Python keywords as is
                    if token_value not in {'def', 'class', 'return', 'if', 'else', 'for', 
                                         'while', 'try', 'except', 'finally', 'with', 'as',
                                         'import', 'from', 'raise', 'pass', 'break', 'continue'}:
                        token_value = self.normalize_name(token_value)
                elif token_type == tokenize.STRING:
                    token_value = "STRING"
                elif token_type == tokenize.NUMBER:
                    token_value = "NUMBER"
                
                tokens.append(Token(str(token_type), token_value))
        except:
            # Fall back to simple string splitting if tokenize fails
            words = source.split()
            tokens = [Token("WORD", word) for word in words if word]
            
        return tokens


class LSHIndex:
    """Locality Sensitive Hashing index for fast similarity search."""
    
    def __init__(self, num_bands: int = 10, band_size: int = 2):
        self.num_bands = num_bands
        self.band_size = band_size
        self.signature_size = num_bands * band_size
        self.band_buckets: List[Dict[str, Set[CodeFragment]]] = [
            {} for _ in range(num_bands)
        ]
    
    def compute_minhash_signature(self, tokens: Tuple[Token, ...]) -> List[int]:
        """Compute MinHash signature for a set of tokens."""
        signature = []
        token_strs = [f"{t.type}:{t.value}" for t in tokens]
        
        # Use multiple hash functions (simulated with different seeds)
        for i in range(self.signature_size):
            min_hash = float('inf')
            for token_str in token_strs:
                # Combine token with signature index for different hash functions
                hash_val = int(hashlib.sha256(
                    f"{token_str}:{i}".encode()
                ).hexdigest(), 16) % (2**32)  # Limit hash size
                min_hash = min(min_hash, hash_val)
            signature.append(min_hash)
            
        return signature
    
    def add_fragment(self, fragment: CodeFragment):
        """Add a code fragment to the LSH index."""
        if not fragment.tokens:
            return
            
        signature = self.compute_minhash_signature(fragment.tokens)
        
        # Split signature into bands and hash each band
        for i in range(self.num_bands):
            start = i * self.band_size
            end = start + self.band_size
            band = tuple(signature[start:end])
            band_str = ":".join(str(x) for x in band)
            
            if band_str not in self.band_buckets[i]:
                self.band_buckets[i][band_str] = set()
            self.band_buckets[i][band_str].add(fragment)
    
    def find_candidates(self, fragment: CodeFragment) -> Set[CodeFragment]:
        """Find candidate similar fragments using LSH."""
        if not fragment.tokens:
            return set()
            
        signature = self.compute_minhash_signature(fragment.tokens)
        candidates = set()
        
        for i in range(self.num_bands):
            start = i * self.band_size
            end = start + self.band_size
            band = tuple(signature[start:end])
            band_str = ":".join(str(x) for x in band)
            
            if band_str in self.band_buckets[i]:
                candidates.update(self.band_buckets[i][band_str])
        
        return candidates - {fragment}  # Exclude self


class SimilarityAnalyzer(BaseAnalyzer):
    """Analyzer for detecting similar code patterns."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the analyzer.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        similarity_config = config.get("analysis", {}).get("similarity", {})
        self.min_lines = similarity_config.get("min_lines", 6)
        self.min_tokens = similarity_config.get("min_tokens", 20)
        self.similarity_threshold = similarity_config.get("similarity_threshold", 0.8)
        self.processor = TokenProcessor()
        self.lsh_index = LSHIndex()
        self.fragments: List[CodeFragment] = []

    def analyze(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Analyze files for similar code patterns.
        
        Args:
            file_paths: List of paths to analyze
            
        Returns:
            Dict containing similarity metrics
        """
        similar_groups = []
        fragments = []
        
        # First pass: extract fragments from all files
        for file_path in file_paths:
            if self.should_ignore_file(file_path):
                continue
                
            try:
                file_fragments = self._extract_fragments(file_path)
                fragments.extend(file_fragments)
                
                # Add fragments to LSH index
                for fragment in file_fragments:
                    self.lsh_index.add_fragment(fragment)
                    
            except Exception as e:
                self._log_error(f"Error extracting fragments from {file_path}: {str(e)}")
                
        # Second pass: find similar fragments
        for fragment in fragments:
            candidates = self.lsh_index.find_candidates(fragment)
            similar = []
            
            for candidate in candidates:
                similarity = self._calculate_similarity(fragment, candidate)
                if similarity >= self.similarity_threshold:
                    similar.append({
                        'file': candidate.location.file_path,
                        'start_line': candidate.location.start_line,
                        'end_line': candidate.location.end_line,
                        'similarity': similarity
                    })
            
            if similar:
                group = {
                    'fragments': [{
                        'file': fragment.location.file_path,
                        'start_line': fragment.location.start_line,
                        'end_line': fragment.location.end_line
                    }] + similar,
                    'similarity': max(s['similarity'] for s in similar)
                }
                similar_groups.append(group)

        return {
            'similar_fragments': similar_groups
        }

    def _extract_fragments(self, file_path: Path) -> List[CodeFragment]:
        """Extract code fragments from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of code fragments
        """
        fragments = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    fragment_content = ast.get_source_segment(content, node)
                    if not fragment_content:
                        continue
                        
                    if len(fragment_content.splitlines()) < self.min_lines:
                        continue
                        
                    fragment = CodeFragment(
                        type=FragmentType.FUNCTION if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                        else FragmentType.CLASS,
                        location=Location(
                            file_path=str(file_path),
                            start_line=node.lineno,
                            end_line=node.end_lineno or node.lineno
                        ),
                        source=fragment_content,
                        tokens=tuple(self.processor.process(fragment_content))
                    )
                    fragments.append(fragment)
                    
        except Exception as e:
            self._log_error(f"Error extracting fragments from {file_path}: {str(e)}")
            
        return fragments

    def _calculate_similarity(self, fragment1: CodeFragment, fragment2: CodeFragment) -> float:
        """Calculate similarity between two code fragments.
        
        Args:
            fragment1: First code fragment
            fragment2: Second code fragment
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not fragment1.tokens or not fragment2.tokens:
            return 0.0
            
        # Use token-based similarity
        tokens1 = set(f"{t.type}:{t.value}" for t in fragment1.tokens)
        tokens2 = set(f"{t.type}:{t.value}" for t in fragment2.tokens)
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0 