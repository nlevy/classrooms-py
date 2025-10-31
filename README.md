# Classroom Assignment Service

An intelligent classroom assignment service that optimally assigns students to classrooms using configurable algorithms. Features multiple assignment strategies, comprehensive validation, and environment-based configuration for production deployments.

## Features

### 🎯 Multi-Strategy Architecture
- **Two Assignment Algorithms**: Choose between fast greedy or optimal constraint programming
- **Environment Configuration**: Control algorithms via environment variables
- **Automatic Fallback**: Graceful degradation if optimization fails
- **Quality Metrics**: Comprehensive solution evaluation and scoring

### 📊 Assignment Capabilities
- **Hard Constraints**: Guaranteed zero friendless students (when solvable)
- **Friend Preferences**: Maintains and optimizes student friendships
- **Gender Balance**: Ensures balanced gender distribution across classes
- **Academic Performance**: Distributes academic levels evenly
- **Behavioral Considerations**: Balances behavioral performance
- **"Not With" Restrictions**: Respects student separation requirements
- **Cluster Groupings**: Supports predefined student groups

### 🛠️ Technical Features
- **REST API**: Production-ready endpoints with structured error responses
- **Multilingual Error Handling**: Error codes with client-side translation support
- **CLI Tools**: Command-line interface for testing and analysis
- **Input Validation**: Comprehensive data validation with 18+ specific error codes
- **Quality Assurance**: Real-time solution evaluation and constraint checking
- **Multi-language Support**: Template data and error messages in multiple languages

### 🔧 Algorithm Options

#### Greedy Strategy (`greedy`)
- **Performance**: <1 second execution time
- **Best for**: Real-time scenarios, development, large datasets (300+ students)
- **Approach**: Fast graph-based greedy assignment
- **Guarantees**: Best-effort optimization

#### CP-SAT Strategy (`cp_sat`) - Default
- **Performance**: 1-30 seconds depending on problem size
- **Best for**: High-quality solutions, production scenarios
- **Approach**: Constraint programming with mathematical optimization
- **Guarantees**: Optimal or near-optimal solutions with hard constraint satisfaction

## Quick Start

### 1. Setup Environment
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Algorithm (Optional)
```bash
# Use CP-SAT for optimal results (default)
export ASSIGNMENT_ALGORITHM=cp_sat
export ASSIGNMENT_TIMEOUT=30

# Or use Greedy for speed
export ASSIGNMENT_ALGORITHM=greedy

# Enable fallback (recommended)
export ASSIGNMENT_FALLBACK=true
```

### 3. Run the Service

#### Development Mode
```bash
python src/main.py
```
Service available at: http://localhost:5000

#### Production Mode
```bash
gunicorn -c gunicorn_config.py src.wsgi:app
```
Service available at: http://0.0.0.0:8000

## API Usage

### Assign Students to Classes
```bash
curl -X POST "http://localhost:5000/classrooms?classesNumber=3" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "Alice",
      "school": "Example School",
      "gender": "FEMALE",
      "academicPerformance": "HIGH",
      "behavioralPerformance": "MEDIUM",
      "friend1": "Bob",
      "friend2": "Charlie",
      "notWith": "David",
      "clusterId": 1
    }
  ]'
```

### Get Data Template
```bash
# English template
curl http://localhost:5000/template

# Hebrew template
curl http://localhost:5000/template?lang=he
```

## Error Handling

The API returns structured error responses with error codes for multilingual client support.

### Error Response Format

All errors return a structured JSON response:

```json
{
  "error": {
    "code": "STUDENT_NO_FRIENDS",
    "params": {
      "studentName": "Alice"
    },
    "message": "Student 'Alice' has no friends listed"
  }
}
```

- **`code`**: Error identifier for client-side translation (e.g., `STUDENT_NO_FRIENDS`)
- **`params`**: Dynamic parameters to substitute in translated messages
- **`message`**: English debug message for logging/debugging

### Client-Side Translation

Clients can translate errors to any language using the error code and parameters:

```typescript
// English
"Student '{studentName}' has no friends listed. All students must have at least one friend."

// Hebrew
"לתלמיד '{studentName}' אין חברים רשומים. כל תלמיד חייב לרשום לפחות חבר אחד."
```

**See [`client_examples/`](client_examples/)** for complete integration examples including:
- Translation files for English and Hebrew
- TypeScript/JavaScript implementation
- React component examples
- Integration guides for various frameworks

### Common Error Codes

| Error Code | Description | Parameters |
|------------|-------------|------------|
| `EMPTY_STUDENT_DATA` | No students provided | `count` |
| `STUDENT_NO_FRIENDS` | Student has no friends listed | `studentName` |
| `UNKNOWN_FRIEND` | Friend not in student list | `studentName`, `friendName` |
| `DUPLICATE_STUDENT_NAMES` | Duplicate names found | `duplicates` (array) |
| `TOO_MANY_CLASSES` | More classes than students | `classCount`, `studentCount` |
| `INVALID_CLASS_COUNT` | Invalid number of classes | `classCount` |
| `MISSING_PARAMETER` | Required parameter missing | `parameter` |

**Complete list**: See [`client_examples/README.md`](client_examples/README.md) for all 18 error codes.

### Example Error Handling

```bash
# Request with invalid data
curl -X POST "http://localhost:5000/classrooms?classesNumber=10" \
  -H "Content-Type: application/json" \
  -d '[{"name": "Alice", "gender": "FEMALE"}]'

# Response (400 Bad Request)
{
  "error": {
    "code": "TOO_MANY_CLASSES",
    "params": {
      "classCount": 10,
      "studentCount": 1
    },
    "message": "Cannot create 10 classes with only 1 students"
  }
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ASSIGNMENT_ALGORITHM` | `cp_sat` | Algorithm: `cp_sat` (optimal) or `greedy` (fast) |
| `ASSIGNMENT_TIMEOUT` | `30` | Timeout in seconds for optimization |
| `ASSIGNMENT_FALLBACK` | `true` | Auto-fallback to greedy if CP-SAT fails |

### Algorithm Selection Guide

| Problem Size | Recommended | Timeout |
|--------------|-------------|---------|
| <50 students | CP-SAT | 10s |
| 50-150 students | CP-SAT | 30s |
| 150-300 students | CP-SAT | 60s |
| >300 students | Greedy or CP-SAT (120s) |

## CLI Usage

```bash
# Assign students from CSV
python src/cli/assign_classes.py -csv students.csv -classes 3

# Compare algorithms
python src/cli/example_usage.py
```

## Dependencies

### Core Requirements
- **Python 3.9+**
- **pandas**: Data processing
- **networkx**: Graph algorithms
- **flask**: Web framework
- **flask-cors**: API CORS support
- **gunicorn**: Production server

### Optional (Auto-fallback if missing)
- **ortools**: Google OR-Tools for CP-SAT optimization

## Troubleshooting

### Common Issues

**Issue**: `ImportError: ortools`
**Solution**: `pip install ortools` or use `ASSIGNMENT_ALGORITHM=greedy`

**Issue**: CP-SAT timeout
**Solution**: Increase `ASSIGNMENT_TIMEOUT` or use greedy algorithm

**Issue**: Students without friends
**Solution**: Verify input data has valid friendships, use CP-SAT algorithm

**Issue**: Poor solution quality
**Solution**: Switch from greedy to CP-SAT: `ASSIGNMENT_ALGORITHM=cp_sat`

### Monitoring

The service provides detailed metrics for monitoring assignment quality:

```python
from src.service.class_assignment_service import ClassAssignmentService

service = ClassAssignmentService(df, strategy='cp_sat')
classes = service.assign_classes(3)

# Get detailed assignment info
info = service.get_last_assignment_info()
print(f"Algorithm used: {info['strategy_used']}")
print(f"Solution quality: {info['solution_quality']}/100")
print(f"Execution time: {info['execution_time']:.2f}s")

# Check if fallback was used
if info['metadata'].get('fallback_used'):
    print(f"Fallback reason: {info['metadata']['fallback_reason']}")
```

## Documentation

- **[Environment Configuration Guide](ENVIRONMENT_CONFIG.md)** - Detailed configuration options
- **[Project Summary](PROJECT_SUMMARY.md)** - Complete technical overview
- **[Error Handling Guide](client_examples/README.md)** - Client-side error translation examples
- **[Error Handling Implementation](ERROR_HANDLING_IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## Production Deployment

For production deployments:

1. **Set environment variables** for your infrastructure
2. **Use CP-SAT algorithm** for optimal results
3. **Enable monitoring** via assignment metadata
4. **Configure timeouts** based on your performance requirements
5. **Enable fallback** for reliability: `ASSIGNMENT_FALLBACK=true`

The service is designed for high availability with automatic fallback mechanisms and comprehensive error handling.

