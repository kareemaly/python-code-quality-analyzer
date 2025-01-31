"""Unit tests for the similarity analyzer module."""

import pytest
from pathlib import Path
from src.analyzers.similarity_analyzer import (
    FragmentType,
    Location,
    Token,
    CodeFragment,
    TokenProcessor,
    LSHIndex,
    SimilarityEngine,
    SimilarityAnalyzer
)

def test_token_processor():
    """Test token processing and normalization."""
    processor = TokenProcessor()
    
    # Test basic tokenization
    source = "def test_func(x, y):\n    return x + y"
    tokens = processor.process(source)
    
    assert len(tokens) > 0
    assert all(isinstance(t, Token) for t in tokens)
    
    # Test name normalization
    assert any(t.value.startswith("NAME_") for t in tokens)
    
    # Test string/number normalization
    source = 'x = "test" + 42'
    tokens = processor.process(source)
    assert any(t.value == "STRING" for t in tokens)
    assert any(t.value == "NUMBER" for t in tokens)
    
    # Test complex code patterns
    source = '''
    def complex_func(x: int, y: float = 1.0) -> float:
        """Test docstring."""
        try:
            result = x * y
            if result > 10:
                return result / 2
            else:
                return result
        except Exception as e:
            raise ValueError("Invalid input") from e
    '''
    tokens = processor.process(source)
    
    # Verify keywords are preserved
    assert "def" in {t.value for t in tokens}
    assert "try" in {t.value for t in tokens}
    assert "if" in {t.value for t in tokens}
    assert "else" in {t.value for t in tokens}
    assert "raise" in {t.value for t in tokens}
    
    # Verify type hints and defaults are normalized
    assert "NUMBER" in {t.value for t in tokens}
    assert any(t.value.startswith("NAME_") for t in tokens)
    
    # Test edge cases
    edge_cases = [
        # Empty string
        "",
        # Only whitespace
        "   \n\t  ",
        # Only comments
        "# Comment\n# Another comment",
        # Invalid syntax
        "def invalid(:"
    ]
    for case in edge_cases:
        tokens = processor.process(case)
        assert isinstance(tokens, list)

def test_code_fragment():
    """Test code fragment functionality."""
    fragment = CodeFragment(
        type=FragmentType.FUNCTION,
        location=Location("test.py", 1, 5),
        source="def test():\n    pass"
    )
    
    processor = TokenProcessor()
    fragment = fragment.with_tokens(processor)
    assert len(fragment.tokens) > 0
    
    fragment = fragment.with_hash()
    assert fragment.hash is not None
    
    # Test equality
    fragment2 = fragment.with_hash()
    assert fragment == fragment2
    assert hash(fragment) == hash(fragment2)
    
    # Test different fragments with same structure
    fragment1 = CodeFragment(
        type=FragmentType.FUNCTION,
        location=Location("test1.py", 1, 5),
        source="""
        def process_data(items):
            result = []
            for item in items:
                if item > 0:
                    result.append(item * 2)
            return result
        """
    )
    
    fragment2 = CodeFragment(
        type=FragmentType.FUNCTION,
        location=Location("test2.py", 1, 5),
        source="""
        def filter_values(data):
            output = []
            for value in data:
                if value > 10:
                    output.append(value + 1)
            return output
        """
    )
    
    fragment1 = fragment1.with_tokens(processor).with_hash()
    fragment2 = fragment2.with_tokens(processor).with_hash()
    
    # Different source but similar structure should have different hashes
    assert fragment1.hash != fragment2.hash

def test_lsh_index():
    """Test LSH indexing and candidate finding."""
    index = LSHIndex(num_bands=10, band_size=2)  # Match implementation parameters
    processor = TokenProcessor()
    
    # Create similar fragments
    fragment1 = CodeFragment(
        type=FragmentType.FUNCTION,
        location=Location("test1.py", 1, 5),
        source="def func1(x):\n    return x + 1"
    )
    fragment1 = fragment1.with_tokens(processor).with_hash()
    
    fragment2 = CodeFragment(
        type=FragmentType.FUNCTION,
        location=Location("test2.py", 1, 5),
        source="def func2(y):\n    return y + 1"
    )
    fragment2 = fragment2.with_tokens(processor).with_hash()
    
    # Add fragments to index
    index.add_fragment(fragment1)
    index.add_fragment(fragment2)
    
    # Test candidate finding
    candidates = index.find_candidates(fragment1)
    assert fragment2 in candidates
    
    # Test with more complex similar fragments
    fragment3 = CodeFragment(
        type=FragmentType.FUNCTION,
        location=Location("test3.py", 1, 10),
        source="""
        def process_items(items, threshold=0):
            results = []
            for item in items:
                if item > threshold:
                    results.append(item * 2)
            return results
        """
    )
    
    fragment4 = CodeFragment(
        type=FragmentType.FUNCTION,
        location=Location("test4.py", 1, 10),
        source="""
        def filter_data(data, min_value=10):
            filtered = []
            for value in data:
                if value > min_value:
                    filtered.append(value + 1)
            return filtered
        """
    )
    
    fragment3 = fragment3.with_tokens(processor).with_hash()
    fragment4 = fragment4.with_tokens(processor).with_hash()
    
    index.add_fragment(fragment3)
    index.add_fragment(fragment4)
    
    # Test finding structurally similar code
    candidates = index.find_candidates(fragment3)
    assert fragment4 in candidates

def test_similarity_engine():
    """Test similarity computation and fragment finding."""
    engine = SimilarityEngine(min_fragment_size=2, similarity_threshold=0.7)
    
    # Create similar fragments
    fragment1 = CodeFragment(
        type=FragmentType.FUNCTION,
        location=Location("test1.py", 1, 5),
        source="def add(x, y):\n    return x + y"
    )
    
    fragment2 = CodeFragment(
        type=FragmentType.FUNCTION,
        location=Location("test2.py", 1, 5),
        source="def sum(a, b):\n    return a + b"
    )
    
    # Add fragments
    engine.add_fragment(fragment1)
    engine.add_fragment(fragment2)
    
    # Test similarity finding
    similar = engine.find_similar(fragment1)
    assert len(similar) > 0
    assert similar[0][0] == fragment2
    assert similar[0][1] >= 0.7
    
    # Test with more complex similar fragments
    fragment3 = CodeFragment(
        type=FragmentType.CLASS,
        location=Location("test3.py", 1, 15),
        source="""
        class DataProcessor:
            def __init__(self, threshold=0):
                self.threshold = threshold
                
            def process(self, items):
                results = []
                for item in items:
                    if item > self.threshold:
                        results.append(item * 2)
                return results
        """
    )
    
    fragment4 = CodeFragment(
        type=FragmentType.CLASS,
        location=Location("test4.py", 1, 15),
        source="""
        class ValueFilter:
            def __init__(self, min_value=10):
                self.min_value = min_value
                
            def filter(self, data):
                filtered = []
                for value in data:
                    if value > self.min_value:
                        filtered.append(value + 1)
                return filtered
        """
    )
    
    engine.add_fragment(fragment3)
    engine.add_fragment(fragment4)
    
    # Test finding similar classes
    similar = engine.find_similar(fragment3)
    assert len(similar) > 0
    assert similar[0][0] == fragment4
    assert similar[0][1] >= 0.7

@pytest.fixture
def temp_python_files(tmp_path):
    """Create temporary Python files for testing."""
    file1 = tmp_path / "test1.py"
    file2 = tmp_path / "test2.py"
    
    # More complex test files with similar patterns
    file1.write_text("""
class DataProcessor:
    def __init__(self, threshold=0):
        self.threshold = threshold
        
    def process(self, items):
        results = []
        for item in items:
            if item > self.threshold:
                results.append(item * 2)
        return results

def helper_function(x):
    return x * 2
""")
    
    file2.write_text("""
class ValueFilter:
    def __init__(self, min_value=10):
        self.min_value = min_value
        
    def filter(self, data):
        filtered = []
        for value in data:
            if value > self.min_value:
                filtered.append(value + 1)
        return filtered

def utility_function(y):
    return y + 1
""")
    
    return [str(file1), str(file2)]

def test_similarity_analyzer(temp_python_files):
    """Test end-to-end similarity analysis."""
    analyzer = SimilarityAnalyzer(min_fragment_size=2, similarity_threshold=0.7)
    results = analyzer.analyze(temp_python_files)
    
    assert len(results) > 0
    
    # Check that similar classes and functions were found
    class_found = False
    func_found = False
    
    for fragments in results.values():
        for fragment, score in fragments:
            if fragment.type == FragmentType.CLASS:
                if "DataProcessor" in fragment.source or "ValueFilter" in fragment.source:
                    class_found = True
            elif fragment.type == FragmentType.FUNCTION:
                if "helper_function" in fragment.source or "utility_function" in fragment.source:
                    func_found = True
            assert score >= 0.7
    
    assert class_found and func_found

def test_fragment_collection():
    """Test code fragment collection from source."""
    analyzer = SimilarityAnalyzer()
    source = """
class TestClass:
    def method1(self):
        pass

def function1():
    pass
"""
    
    fragments = analyzer.collect_fragments("test.py", source)
    assert len(fragments) == 3  # Class + method + function
    
    types = [f.type for f in fragments]
    assert FragmentType.CLASS in types
    assert FragmentType.METHOD in types
    assert FragmentType.FUNCTION in types
    
    # Test with more complex source
    source = """
class ComplexClass:
    def __init__(self, value):
        self.value = value
    
    def method1(self, x):
        try:
            return self.value * x
        except TypeError:
            return 0
    
    @property
    def doubled(self):
        return self.value * 2

def standalone_function(items):
    results = []
    for item in items:
        if isinstance(item, (int, float)):
            results.append(item * 2)
    return results
"""
    
    fragments = analyzer.collect_fragments("test.py", source)
    assert len(fragments) == 5  # Class + 3 methods + function
    
    types = [f.type for f in fragments]
    assert types.count(FragmentType.METHOD) == 3
    assert types.count(FragmentType.FUNCTION) == 1
    assert types.count(FragmentType.CLASS) == 1

def test_invalid_source_handling():
    """Test handling of invalid source code."""
    analyzer = SimilarityAnalyzer()
    
    # Invalid syntax
    source = "def invalid_func("
    fragments = analyzer.collect_fragments("test.py", source)
    assert len(fragments) > 0  # Should fall back to line-based fragmentation
    assert all(f.type == FragmentType.BLOCK for f in fragments)
    
    # Empty source
    fragments = analyzer.collect_fragments("test.py", "")
    assert len(fragments) == 0
    
    # More complex invalid cases
    invalid_cases = [
        # Incomplete class
        "class Test:\ndef method1(self):",
        # Invalid indentation
        """
        def test():
                print(1)
            print(2)
        """,
        # Mixed tabs and spaces
        """
        def test():
        \tprint(1)
            print(2)
        """
    ]
    
    for source in invalid_cases:
        fragments = analyzer.collect_fragments("test.py", source)
        assert len(fragments) > 0  # Should fall back to line-based fragmentation
        assert all(f.type == FragmentType.BLOCK for f in fragments) 