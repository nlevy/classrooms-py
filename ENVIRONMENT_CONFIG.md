# Environment Configuration

## Assignment Algorithm Configuration

The classroom assignment service supports multiple algorithms that can be configured via environment variables.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ASSIGNMENT_ALGORITHM` | `cp_sat` | Algorithm to use: `cp_sat`, `greedy` |
| `ASSIGNMENT_TIMEOUT` | `30` | Timeout in seconds for optimization algorithms |
| `ASSIGNMENT_FALLBACK` | `true` | Whether to fallback to greedy if CP-SAT fails |

### Available Algorithms

#### 1. CP-SAT (Default) - `cp_sat`
- **Type**: Constraint Programming with Google OR-Tools
- **Best for**: Optimal solutions with hard constraints
- **Guarantees**:
  - Zero students without friends
  - All "not-with" constraints satisfied
  - Optimal or near-optimal balance
- **Performance**: 1-30 seconds depending on problem size
- **Requirements**: `ortools` package

#### 2. Greedy - `greedy`
- **Type**: Greedy graph-based algorithm
- **Best for**: Fast execution, real-time scenarios
- **Guarantees**: Best-effort optimization
- **Performance**: <1 second
- **Requirements**: Base packages only

### Configuration Examples

#### Production (Optimal Quality)
```bash
export ASSIGNMENT_ALGORITHM=cp_sat
export ASSIGNMENT_TIMEOUT=60
export ASSIGNMENT_FALLBACK=true
```

#### Development (Fast Iteration)
```bash
export ASSIGNMENT_ALGORITHM=greedy
export ASSIGNMENT_TIMEOUT=10
export ASSIGNMENT_FALLBACK=false
```

#### A/B Testing
```bash
# Terminal 1 - CP-SAT
export ASSIGNMENT_ALGORITHM=cp_sat
python src/main.py

# Terminal 2 - Greedy
export ASSIGNMENT_ALGORITHM=greedy
python src/main.py
```

### API Usage

The algorithm can also be specified programmatically:

```python
# Use specific algorithm
service = ClassAssignmentService(df, strategy='cp_sat', timeout_seconds=45)

# Use environment defaults
service = ClassAssignmentService(df)

# Switch algorithms at runtime
service.switch_strategy('greedy')
strategies = service.get_available_strategies()
```

### Docker Configuration

```dockerfile
ENV ASSIGNMENT_ALGORITHM=cp_sat
ENV ASSIGNMENT_TIMEOUT=30
ENV ASSIGNMENT_FALLBACK=true
```

### Monitoring and Debugging

Enable detailed logging to monitor algorithm performance:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Assignment info will be logged automatically
service = ClassAssignmentService(df)
result = service.assign_classes(3)

# Get detailed metrics
info = service.get_last_assignment_info()
print(f"Quality score: {info['solution_quality']}")
print(f"Execution time: {info['execution_time']}s")
```

### Fallback Behavior

When `ASSIGNMENT_FALLBACK=true` (default):
1. Try primary algorithm (CP-SAT)
2. If CP-SAT fails (missing dependencies/timeout), automatically use Greedy
3. Log warning about fallback

When `ASSIGNMENT_FALLBACK=false`:
1. Use only specified algorithm
2. Fail completely if algorithm unavailable

### Performance Guidelines

| Problem Size | Recommended Algorithm | Timeout |
|--------------|----------------------|---------|
| <50 students | CP-SAT | 10s |
| 50-150 students | CP-SAT | 30s |
| 150-300 students | CP-SAT | 60s |
| >300 students | Greedy or CP-SAT with 120s timeout |

### Troubleshooting

**Issue**: `ImportError: ortools`
**Solution**: Install OR-Tools: `pip install ortools>=9.5.0`

**Issue**: CP-SAT timeout
**Solution**: Increase `ASSIGNMENT_TIMEOUT` or use `greedy` algorithm

**Issue**: Poor solution quality with Greedy
**Solution**: Switch to `cp_sat` algorithm for better results