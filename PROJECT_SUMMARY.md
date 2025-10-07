# Classrooms 2.0 - Project Summary

## Overview
Classrooms 2.0 is an intelligent classroom assignment service that optimally assigns students to classrooms using multiple configurable algorithms. The system features a modern strategy-pattern architecture with environment-based configuration, comprehensive validation, and detailed quality metrics. It supports both fast greedy assignment and advanced constraint programming optimization.

## Technology Stack
- **Backend**: Python with Flask web framework
- **Assignment Algorithms**: Multiple strategies (Greedy, CP-SAT)
- **Optimization**: Google OR-Tools for constraint programming (optional)
- **Data Processing**: Pandas for data manipulation, NetworkX for graph operations
- **Architecture**: Strategy pattern with modular design
- **Configuration**: Environment variable based deployment control
- **Production Server**: Gunicorn WSGI server
- **API**: RESTful JSON API with CORS support
- **Quality Assurance**: Comprehensive validation and solution evaluation

## Project Structure

```
classrooms2.0/
├── src/
│   ├── main.py                          # Development server entry point
│   ├── wsgi.py                          # Production WSGI entry point
│   ├── server/
│   │   ├── app.py                       # Flask application and API endpoints
│   │   └── dto.py                       # Data Transfer Objects and enums
│   ├── service/
│   │   ├── class_assignment_service.py  # Modernized assignment orchestrator
│   │   ├── summary_service.py           # Class analysis and reporting
│   │   ├── strategies/                  # Strategy pattern implementation
│   │   │   ├── base_strategy.py         # Abstract base class
│   │   │   ├── greedy_strategy.py       # Fast graph-based algorithm
│   │   │   ├── cp_sat_strategy.py       # Constraint programming algorithm
│   │   │   └── strategy_factory.py     # Strategy creation and configuration
│   │   ├── validators/                  # Input validation system
│   │   │   └── input_validator.py       # Data validation and constraints
│   │   └── evaluators/                  # Solution quality assessment
│   │       └── solution_evaluator.py    # Assignment quality metrics
│   ├── cli/
│   │   ├── assign_classes.py            # Command-line interface tool
│   │   └── example_usage.py             # Usage examples
│   └── data/
│       ├── template-en.json             # English data template
│       └── template-he.json             # Hebrew data template
├── tests/
│   └── test_new_assignment_service.py   # Comprehensive test suite
├── requirements.txt                     # Python dependencies (includes OR-Tools)
├── gunicorn_config.py                  # Production server configuration
├── ENVIRONMENT_CONFIG.md               # Environment variable guide
├── ALGORITHM_NAMING.md                 # Naming convention documentation
└── README.md                           # Setup and usage documentation
```

## Core Features

### 1. Multi-Strategy Assignment Architecture
- **Strategy Selection**: Choose between Greedy (fast) or CP-SAT (optimal) algorithms
- **Environment Configuration**: Control algorithms via environment variables
- **Runtime Strategy Switching**: Change algorithms without restart
- **Automatic Fallback**: Gracefully degrade to Greedy if CP-SAT unavailable
- **Quality Metrics**: Comprehensive solution evaluation and scoring

### 2. Assignment Algorithm Features
- **Hard Constraints**: Guaranteed zero friendless students (when solvable)
- **Friendship Networks**: Uses NetworkX graph analysis to maintain and optimize student friendships
- **Academic Balance**: Distributes students across classes based on academic performance (HIGH/MEDIUM/LOW)
- **Behavioral Considerations**: Balances behavioral performance across classrooms
- **Gender Distribution**: Ensures balanced gender representation
- **Not-With Restrictions**: Respects "not with" constraints between specific students
- **Cluster Groupings**: Supports predefined student clusters that should stay together

### 3. Algorithm Types

#### Greedy Strategy
- **Approach**: Fast graph-based greedy assignment
- **Performance**: <1 second execution
- **Best For**: Real-time scenarios, development, large datasets
- **Guarantees**: Best-effort optimization

#### CP-SAT Strategy
- **Approach**: Constraint programming with mathematical optimization
- **Performance**: 1-30 seconds depending on problem size
- **Best For**: High-quality solutions, production scenarios
- **Guarantees**: Optimal or near-optimal solutions with hard constraint satisfaction

### 4. REST API Endpoints
- **POST /classrooms**: Main assignment endpoint
  - Accepts JSON array of student data
  - Requires `classesNumber` query parameter
  - Returns detailed class assignments and analytics
- **GET /template**: Data template endpoint
  - Supports multiple languages (English/Hebrew)
  - Provides structured student data format

### 5. Input Validation & Quality Assurance
- **Pre-Assignment Validation**: Comprehensive input data validation
- **Hard Constraint Checking**: Ensures no friendless students in input
- **Solution Evaluation**: Detailed quality metrics and scoring
- **Constraint Violation Detection**: Identifies and reports all violations
- **Performance Monitoring**: Execution time and algorithm performance tracking

### 6. Command Line Interface
- Standalone CLI tool for testing and analysis
- CSV file input support
- Detailed assignment reports with statistics
- Strategy comparison capabilities
- Useful for development and testing scenarios

### 7. Multi-language Support
- Template data structures available in multiple languages
- Extensible language support system

## Data Model

### Student Data Structure
```json
{
  "name": "Student Name",
  "school": "School Name",
  "gender": "MALE|FEMALE",
  "academicPerformance": "HIGH|MEDIUM|LOW",
  "behavioralPerformance": "HIGH|MEDIUM|LOW",
  "comments": "Optional comments",
  "friend1": "Friend name",
  "friend2": "Friend name",
  "friend3": "Friend name",
  "friend4": "Friend name",
  "notWith": "Student to avoid",
  "clusterId": 0
}
```

### Assignment Result Output
- **Class Compositions**: Student assignments with detailed breakdowns
- **Quality Metrics**: Overall solution score (0-100)
- **Constraint Analysis**: Hard constraint satisfaction status
- **Balance Statistics**: Gender, academic, and behavioral distributions
- **Friendship Analysis**: Friendship satisfaction rates
- **Performance Metadata**: Algorithm used, execution time, solver statistics
- **Violation Reports**: Detailed constraint violation information

## Architecture & Algorithm Approaches

### Multi-Strategy Architecture
The service uses a **Strategy Pattern** design enabling multiple assignment algorithms:

1. **Strategy Selection**: Environment-configurable algorithm choice
2. **Validation Pipeline**: Comprehensive input validation before assignment
3. **Assignment Execution**: Strategy-specific algorithm implementation
4. **Quality Evaluation**: Post-assignment solution assessment
5. **Fallback Mechanisms**: Graceful degradation for robustness

### Greedy Strategy Approach
1. **Graph Construction**: Builds friendship networks using NetworkX
2. **Greedy Selection**: Prioritizes students with fewest unassigned friends
3. **Group Assignment**: Moves students with up to 2 friends together
4. **Dynamic Balancing**: Maintains class size balance during assignment
5. **Constraint Validation**: Ensures "not with" restrictions respected

### CP-SAT Strategy Approach
1. **Problem Modeling**: Formulates assignment as constraint satisfaction problem
2. **Hard Constraints**: Each student has ≥1 friend, no "not with" violations
3. **Soft Constraints**: Optimizes class balance, gender distribution, performance spread
4. **Multi-Objective Optimization**: Weighted combination of friendship and balance goals
5. **Solver Execution**: Uses Google OR-Tools CP-SAT solver with timeout handling

## Configuration & Deployment

### Environment Configuration
The system supports runtime configuration via environment variables:

```bash
# Algorithm selection
export ASSIGNMENT_ALGORITHM=cp_sat    # or 'greedy'
export ASSIGNMENT_TIMEOUT=30          # seconds
export ASSIGNMENT_FALLBACK=true       # fallback to greedy if CP-SAT fails
```

### Development
- Run locally with `python src/main.py`
- Available at `http://localhost:5000`
- Debug mode enabled for development
- Strategy switching without restart
- Comprehensive logging for debugging

### Production
- Configured for Gunicorn WSGI server
- Multi-worker process setup (CPU cores × 2 + 1)
- Listens on `0.0.0.0:8000`
- Environment-based algorithm control
- Automatic fallback mechanisms
- Production-ready logging and error handling
- Quality metrics and performance monitoring

## Dependencies

### Core Dependencies
- **pandas**: Data manipulation and analysis
- **networkx**: Graph algorithms for friendship networks
- **flask**: Web framework and API
- **flask-cors**: Cross-origin resource sharing
- **gunicorn**: Production WSGI server
- **numpy**: Numerical computations
- **tabulate**: CLI table formatting

### Optional Dependencies
- **ortools**: Google OR-Tools for CP-SAT strategy (optional, auto-fallback if missing)

## Key Strengths

### Technical Excellence
1. **Multi-Strategy Architecture**: Choose optimal algorithm for each scenario
2. **Production Ready**: Environment-based configuration and robust error handling
3. **Quality Assurance**: Comprehensive validation and solution evaluation
4. **Scalable Design**: Strategy pattern enables easy algorithm additions
5. **Graceful Degradation**: Automatic fallback mechanisms ensure reliability

### User Experience
6. **Developer Friendly**: Comprehensive CLI tools, clear documentation, and extensive testing
7. **Flexible Deployment**: Environment variable configuration for different scenarios
8. **Real-Time Monitoring**: Detailed performance metrics and quality scoring
9. **Backward Compatible**: Existing integrations continue working unchanged

### Algorithm Capabilities
10. **Hard Constraint Satisfaction**: Guaranteed constraint compliance (when solvable)
11. **Multi-Objective Optimization**: Balances friendships, demographics, and performance
12. **Intelligent Graph Analysis**: Sophisticated friendship network processing
13. **Mathematical Optimization**: Advanced constraint programming for optimal solutions

## Use Cases

This system is designed for educational institutions requiring:
- **High-Quality Assignments**: Schools prioritizing optimal student placement
- **Fast Assignments**: Schools needing real-time or large-scale processing
- **Flexible Deployment**: Organizations with varying infrastructure requirements
- **Quality Monitoring**: Institutions requiring detailed assignment analytics
- **Constraint Compliance**: Schools with strict friendship and separation requirements

The dual-strategy approach ensures the system can adapt to different organizational needs while maintaining the highest possible solution quality.