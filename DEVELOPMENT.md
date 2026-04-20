# Development Standards and Best Practices

## Code Organization

### Backend Module Structure
All backend modules follow this organization:
```python
# 1. Imports (standard library, third-party, local)
import logging
from typing import Optional

from logger import get_logger

# 2. Module-level constants and configuration
logger = get_logger(__name__)

# 3. Helper functions (private, start with _)
def _helper_function():
    pass

# 4. Public classes
class PublicClass:
    pass

# 5. Public functions
def public_function():
    pass
```

### Error Handling

**Always use structured error handling:**
```python
try:
    result = operation()
except ValueError as e:
    logger.error(f"Invalid input: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    raise
```

**Never use bare except:**
```python
# ❌ BAD
except:
    pass

# ✅ GOOD
except Exception as e:
    logger.error(str(e))
```

### Logging

**Use structured logging with appropriate levels:**
```python
logger.debug("Detailed diagnostic information")     # Development
logger.info("Informational messages")               # Normal operation
logger.warning("Warning conditions")                # May need attention
logger.error("Error conditions")                    # Something failed
logger.critical("Critical conditions")              # System failing
```

**Include context in log messages:**
```python
# ❌ BAD
logger.error("Error occurred")

# ✅ GOOD
logger.error(f"Failed to process upload {upload_id}: {error_msg}")
```

### Type Hints

**Always use type hints for function parameters and returns:**
```python
from typing import Optional, Dict, List

def process_data(
    df: pd.DataFrame,
    config: Optional[Dict[str, Any]] = None
) -> List[float]:
    """Process dataframe and return results."""
    pass
```

## Configuration Management

### Using Config Module
```python
from config import get_config

config = get_config()
ttl_minutes = config.upload.TTL_MINUTES
debug_mode = config.flask.DEBUG
```

### Adding New Configuration
1. Add to `.env.example` with description
2. Add to `config.py` in appropriate dataclass
3. Document in `backend/README.md`

## Testing

### Unit Test Template
```python
import unittest
from unittest.mock import patch, MagicMock

class TestMyModule(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_happy_path(self):
        """Test successful operation."""
        result = my_function()
        self.assertEqual(result, expected)
    
    def test_error_handling(self):
        """Test error cases."""
        with self.assertRaises(ValueError):
            my_function(invalid_input)
```

### Running Tests
```bash
cd backend
python -m pytest .              # Run all tests
python -m pytest -v             # Verbose output
python -m pytest tests/test_*.py # Run specific test file
```

## Documentation Standards

### Docstring Format
```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief one-line description.
    
    Longer description if needed, explaining what the function does,
    any important side effects, or special behavior.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When validation fails
        LookupError: When data not found
    
    Example:
        >>> result = my_function("test", 42)
        >>> assert result is True
    """
    pass
```

### README Format
- Start with brief description
- Include installation instructions
- Show usage examples
- List API endpoints or functions
- Link to related documentation

## Git Workflow

### Commit Message Format
```
<type>(<scope>): <subject>

<body (optional)>

<footer (optional)>
```

**Types**: `feat`, `fix`, `perf`, `docs`, `refactor`, `test`, `chore`

**Examples**:
```
feat(app): add request timeout handling
fix(ai_engine): resolve config loading inefficiency
perf(ensemble): optimize model training
docs(backend): add module documentation
refactor(config): centralize environment variables
```

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `perf/description` - Performance improvements
- `docs/description` - Documentation

### Commit Best Practices
1. Make commits atomic (one logical change per commit)
2. Write clear, descriptive commit messages
3. Reference issue numbers: `fix: issue #123`
4. Don't commit sensitive data or compiled artifacts
5. Keep commits focused and reviewable

## Performance Considerations

### Before Writing Code
- Consider algorithmic complexity
- Think about database queries (if applicable)
- Plan for caching of expensive operations

### During Code Review
- Look for N+1 query problems
- Check for unnecessary loops or iterations
- Verify proper use of caching
- Validate error handling doesn't leak secrets

### After Deployment
- Monitor performance metrics
- Use profiling tools to find bottlenecks
- Optimize hot paths based on monitoring data

## Security Checklist

### Data Handling
- [ ] Never log sensitive data (API keys, tokens, passwords)
- [ ] Validate and sanitize all user inputs
- [ ] Use parameterized queries if using database
- [ ] Implement rate limiting for public endpoints

### API Security
- [ ] Validate request Content-Type
- [ ] Implement request timeout
- [ ] Check file upload sizes and types
- [ ] Hash sensitive data before storage

### Deployment
- [ ] Set FLASK_DEBUG=false in production
- [ ] Use environment variables for secrets
- [ ] Add HTTPS/TLS for data in transit
- [ ] Implement request logging (without sensitive data)
- [ ] Regular dependency security updates

## Future Improvements

### Short Term
- [ ] Add unit test coverage (target 80%+)
- [ ] Implement integration tests
- [ ] Add API rate limiting
- [ ] Database optimization (if applicable)

### Medium Term
- [ ] Async request handling with Celery
- [ ] Distributed caching with Redis
- [ ] Microservices separation
- [ ] Kubernetes deployment configuration

### Long Term
- [ ] Machine learning model A/B testing
- [ ] Advanced analytics dashboard
- [ ] Real-time collaboration features
- [ ] Mobile application

## Questions or Need Help?

Refer to:
- `backend/README.md` - Backend module documentation
- `OPTIMIZATION_GUIDE.md` - Performance tuning guide
- `BUGFIXES.md` - Bug fixes and improvements
- `explain.md` - Detailed project documentation
