# Logs Monitoring

This guide covers logging, monitoring, and debugging in the A2A LangGraph Boilerplate system.

## Logging Architecture

### Logging Components

The system uses a structured logging approach with:

- **Application Logs**: Core application events and operations
- **Agent Logs**: AI agent interactions and decisions
- **MCP Server Logs**: Tool usage and external service calls
- **Performance Logs**: Execution times and resource usage
- **Error Logs**: Exceptions and failure diagnostics

### Log Levels

```python
# Log levels used throughout the system
LOG_LEVELS = {
    "DEBUG": "Detailed debugging information",
    "INFO": "General operational messages", 
    "WARNING": "Warning conditions that may need attention",
    "ERROR": "Error conditions that prevent normal operation",
    "CRITICAL": "Critical conditions that may cause system failure"
}
```

## Log Configuration

### Basic Logging Setup

The logging configuration is defined in `app/core/logging.py`:

```python
import logging
import sys

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
```

### Enhanced Logging Configuration

For production environments, consider this enhanced configuration:

```python
import logging
import logging.handlers
import os
from datetime import datetime

def setup_enhanced_logging():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=f"{log_dir}/app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger
```

## Running with Logging

### Development Mode

```bash
# Run with console logging
uvicorn app.main:app --reload --log-level info

# Run with file logging
uvicorn app.main:app --reload --log-level info > server.log 2>&1

# Run in background with logging
uvicorn app.main:app --reload --log-level info > server.log 2>&1 &
```

### Production Mode

```bash
# Run with structured logging
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info --access-log

# Run with process management
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 \
  --access-logfile access.log --error-logfile error.log --log-level info
```

## Log Monitoring

### Real-time Log Monitoring

```bash
# Monitor all logs in real-time
tail -f server.log

# Monitor specific log levels
tail -f server.log | grep "ERROR\|WARNING"

# Monitor agent-specific logs
tail -f server.log | grep "app.services.crew"

# Monitor MCP-related logs
tail -f server.log | grep "MCP\|mcp"
```

### Log Analysis Commands

```bash
# Count log entries by level
grep -c "INFO" server.log
grep -c "ERROR" server.log
grep -c "WARNING" server.log

# Find errors in the last hour
grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" server.log | grep ERROR

# Search for specific operations
grep "execute_prompt" server.log
grep "MCP server" server.log
grep "agent" server.log
```

## Key Log Messages

### Crew Execution Logs

```python
# Example crew execution log sequence
log_sequence = [
    "Starting execute_prompt for crew_id {crew_id} with prompt: {prompt_preview}...",
    "Found crew: {crew_name} with {agent_count} agents",
    "Found supervisor agent: {supervisor_name}",
    "Initializing agent tools",
    "Fetching all MCP servers from database",
    "Found {server_count} MCP servers in database",
    "Creating resilient MCP tools",
    "Added {tool_count} MCP tools to agent toolset",
    "Creating agents for crew",
    "Creating supervisor agent",
    "Creating agent graph",
    "Agent graph compilation took {duration:.2f} seconds",
    "Starting async workflow execution",
    "Async workflow execution completed in {duration:.2f} seconds",
    "Total execution time: {duration:.2f} seconds"
]
```

### MCP Server Logs

```python
# MCP server interaction logs
mcp_logs = [
    "Connecting to MCP server: {server_url}",
    "Successfully connected to MCP server and retrieved {tool_count} tools",
    "MCP tool {tool_name} failed (attempt {attempt}/{max_attempts}): {error}",
    "Created {tool_count} resilient MCP tools with {max_retries} max retries",
    "Failed connecting to MCP server: {error}"
]
```

### Agent Activity Logs

```python
# Agent-specific logs
agent_logs = [
    "Creating agent: {agent_name} with role: {agent_role}",
    "Using custom model for agent {agent_name}: {model}",
    "Added agent {agent_name} to crew",
    "Agent {agent_name} executing task: {task_description}",
    "Agent {agent_name} completed task in {duration:.2f} seconds"
]
```

## Log Analysis Scripts

### Python Log Analysis

```python
import re
from collections import defaultdict, Counter
from datetime import datetime

def analyze_logs(log_file_path):
    """Analyze log file for patterns and statistics."""
    
    stats = {
        "total_lines": 0,
        "log_levels": Counter(),
        "components": Counter(),
        "errors": [],
        "performance_metrics": [],
        "crew_executions": [],
        "mcp_operations": []
    }
    
    with open(log_file_path, 'r') as f:
        for line in f:
            stats["total_lines"] += 1
            
            # Parse log level
            if " - INFO - " in line:
                stats["log_levels"]["INFO"] += 1
            elif " - ERROR - " in line:
                stats["log_levels"]["ERROR"] += 1
                stats["errors"].append(line.strip())
            elif " - WARNING - " in line:
                stats["log_levels"]["WARNING"] += 1
            elif " - DEBUG - " in line:
                stats["log_levels"]["DEBUG"] += 1
            
            # Parse component
            component_match = re.search(r' - ([^-]+) - ', line)
            if component_match:
                component = component_match.group(1)
                stats["components"][component] += 1
            
            # Parse performance metrics
            duration_match = re.search(r'took ([\d.]+) seconds', line)
            if duration_match:
                duration = float(duration_match.group(1))
                stats["performance_metrics"].append(duration)
            
            # Parse crew executions
            if "Starting execute_prompt" in line:
                crew_match = re.search(r'crew_id ([a-f0-9-]+)', line)
                if crew_match:
                    stats["crew_executions"].append(crew_match.group(1))
            
            # Parse MCP operations
            if "MCP" in line or "mcp" in line:
                stats["mcp_operations"].append(line.strip())
    
    return stats

def generate_log_report(stats):
    """Generate a comprehensive log analysis report."""
    
    report = []
    report.append("LOG ANALYSIS REPORT")
    report.append("=" * 50)
    report.append(f"Total log lines: {stats['total_lines']}")
    report.append("")
    
    # Log levels distribution
    report.append("Log Levels Distribution:")
    for level, count in stats["log_levels"].most_common():
        percentage = (count / stats['total_lines']) * 100
        report.append(f"  {level}: {count} ({percentage:.1f}%)")
    report.append("")
    
    # Component activity
    report.append("Most Active Components:")
    for component, count in stats["components"].most_common(10):
        report.append(f"  {component}: {count} log entries")
    report.append("")
    
    # Performance metrics
    if stats["performance_metrics"]:
        avg_duration = sum(stats["performance_metrics"]) / len(stats["performance_metrics"])
        max_duration = max(stats["performance_metrics"])
        min_duration = min(stats["performance_metrics"])
        
        report.append("Performance Metrics:")
        report.append(f"  Average operation time: {avg_duration:.2f} seconds")
        report.append(f"  Maximum operation time: {max_duration:.2f} seconds")
        report.append(f"  Minimum operation time: {min_duration:.2f} seconds")
        report.append("")
    
    # Crew activity
    if stats["crew_executions"]:
        unique_crews = set(stats["crew_executions"])
        report.append(f"Crew Activity: {len(stats['crew_executions'])} executions across {len(unique_crews)} crews")
        report.append("")
    
    # MCP operations
    if stats["mcp_operations"]:
        report.append(f"MCP Operations: {len(stats['mcp_operations'])} MCP-related log entries")
        report.append("")
    
    # Recent errors
    if stats["errors"]:
        report.append("Recent Errors:")
        for error in stats["errors"][-5:]:  # Last 5 errors
            report.append(f"  {error}")
        report.append("")
    
    return "\n".join(report)

# Usage example
if __name__ == "__main__":
    stats = analyze_logs("server.log")
    report = generate_log_report(stats)
    print(report)
    
    # Save report to file
    with open("log_analysis_report.txt", "w") as f:
        f.write(report)
```

### Bash Log Analysis

```bash
#!/bin/bash

# log_analysis.sh - Comprehensive log analysis script

LOG_FILE="server.log"
REPORT_FILE="log_report.txt"

echo "A2A LangGraph Boilerplate - Log Analysis Report" > $REPORT_FILE
echo "Generated: $(date)" >> $REPORT_FILE
echo "=============================================" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Basic statistics
echo "BASIC STATISTICS:" >> $REPORT_FILE
echo "Total log lines: $(wc -l < $LOG_FILE)" >> $REPORT_FILE
echo "Log file size: $(du -h $LOG_FILE | cut -f1)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Log level distribution
echo "LOG LEVEL DISTRIBUTION:" >> $REPORT_FILE
echo "INFO: $(grep -c " - INFO - " $LOG_FILE)" >> $REPORT_FILE
echo "WARNING: $(grep -c " - WARNING - " $LOG_FILE)" >> $REPORT_FILE
echo "ERROR: $(grep -c " - ERROR - " $LOG_FILE)" >> $REPORT_FILE
echo "DEBUG: $(grep -c " - DEBUG - " $LOG_FILE)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Component activity
echo "COMPONENT ACTIVITY:" >> $REPORT_FILE
echo "Crew service: $(grep -c "app.services.crew" $LOG_FILE)" >> $REPORT_FILE
echo "Agent service: $(grep -c "app.services.agent" $LOG_FILE)" >> $REPORT_FILE
echo "MCP operations: $(grep -c "MCP\|mcp" $LOG_FILE)" >> $REPORT_FILE
echo "API requests: $(grep -c "Request:" $LOG_FILE)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Recent activity (last 100 lines)
echo "RECENT ACTIVITY (Last 100 lines):" >> $REPORT_FILE
tail -100 $LOG_FILE | head -10 >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Error summary
echo "ERROR SUMMARY:" >> $REPORT_FILE
if grep -q " - ERROR - " $LOG_FILE; then
    echo "Recent errors found:" >> $REPORT_FILE
    grep " - ERROR - " $LOG_FILE | tail -5 >> $REPORT_FILE
else
    echo "No errors found in log file" >> $REPORT_FILE
fi
echo "" >> $REPORT_FILE

# Performance indicators
echo "PERFORMANCE INDICATORS:" >> $REPORT_FILE
echo "Crew executions: $(grep -c "Starting execute_prompt" $LOG_FILE)" >> $REPORT_FILE
echo "Completed executions: $(grep -c "Total execution time" $LOG_FILE)" >> $REPORT_FILE
echo "MCP tool creations: $(grep -c "Created.*resilient MCP tools" $LOG_FILE)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "Report saved to: $REPORT_FILE"
```

## Monitoring Dashboards

### Simple Dashboard Script

```python
import time
import os
from collections import deque
import threading

class LogMonitor:
    def __init__(self, log_file="server.log"):
        self.log_file = log_file
        self.metrics = {
            "requests_per_minute": deque(maxlen=60),
            "errors_per_minute": deque(maxlen=60),
            "crew_executions": deque(maxlen=100),
            "average_response_time": deque(maxlen=50)
        }
        self.running = False
    
    def start_monitoring(self):
        """Start monitoring logs in real-time."""
        self.running = True
        threading.Thread(target=self._monitor_logs, daemon=True).start()
        threading.Thread(target=self._display_dashboard, daemon=True).start()
    
    def _monitor_logs(self):
        """Monitor log file for new entries."""
        if not os.path.exists(self.log_file):
            return
        
        with open(self.log_file, 'r') as f:
            f.seek(0, 2)  # Go to end of file
            
            while self.running:
                line = f.readline()
                if line:
                    self._process_log_line(line)
                else:
                    time.sleep(0.1)
    
    def _process_log_line(self, line):
        """Process a single log line for metrics."""
        current_minute = int(time.time()) // 60
        
        # Count requests
        if "Request:" in line:
            self.metrics["requests_per_minute"].append(current_minute)
        
        # Count errors
        if " - ERROR - " in line:
            self.metrics["errors_per_minute"].append(current_minute)
        
        # Track crew executions
        if "Starting execute_prompt" in line:
            self.metrics["crew_executions"].append(time.time())
        
        # Track response times
        if "Total execution time:" in line:
            import re
            match = re.search(r'([\d.]+) seconds', line)
            if match:
                duration = float(match.group(1))
                self.metrics["average_response_time"].append(duration)
    
    def _display_dashboard(self):
        """Display real-time dashboard."""
        while self.running:
            os.system('clear')  # Clear screen
            
            print("A2A LangGraph Boilerplate - Real-time Dashboard")
            print("=" * 50)
            print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("")
            
            # Recent activity
            recent_requests = len([t for t in self.metrics["requests_per_minute"] 
                                 if t >= (int(time.time()) // 60) - 1])
            recent_errors = len([t for t in self.metrics["errors_per_minute"] 
                               if t >= (int(time.time()) // 60) - 1])
            recent_executions = len([t for t in self.metrics["crew_executions"] 
                                   if t >= time.time() - 60])
            
            print(f"Requests (last minute): {recent_requests}")
            print(f"Errors (last minute): {recent_errors}")
            print(f"Crew executions (last minute): {recent_executions}")
            
            if self.metrics["average_response_time"]:
                avg_response = sum(self.metrics["average_response_time"]) / len(self.metrics["average_response_time"])
                print(f"Average response time: {avg_response:.2f}s")
            
            print("")
            print("Press Ctrl+C to stop monitoring")
            
            time.sleep(5)
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.running = False

# Usage
if __name__ == "__main__":
    monitor = LogMonitor()
    try:
        monitor.start_monitoring()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("\nMonitoring stopped")
```

## Error Tracking

### Common Error Patterns

```python
# Common errors and their meanings
error_patterns = {
    "UnboundLocalError": {
        "description": "MCP server connection issues",
        "solution": "Check MCP server availability and network connectivity",
        "log_pattern": "UnboundLocalError.*call_tool_result"
    },
    
    "HTTPStatusError": {
        "description": "HTTP errors when connecting to MCP servers",
        "solution": "Verify MCP server URL and authentication",
        "log_pattern": "HTTPStatusError.*401|403|404|500"
    },
    
    "TimeoutError": {
        "description": "Operations taking too long to complete",
        "solution": "Increase timeout values or optimize operations",
        "log_pattern": "TimeoutError|timeout"
    },
    
    "ValidationError": {
        "description": "Invalid data format or missing required fields",
        "solution": "Check request format and required parameters",
        "log_pattern": "ValidationError|validation error"
    }
}

def detect_error_patterns(log_file):
    """Detect common error patterns in logs."""
    detected_errors = {}
    
    with open(log_file, 'r') as f:
        content = f.read()
        
        for error_type, details in error_patterns.items():
            import re
            matches = re.findall(details["log_pattern"], content, re.IGNORECASE)
            if matches:
                detected_errors[error_type] = {
                    "count": len(matches),
                    "description": details["description"],
                    "solution": details["solution"]
                }
    
    return detected_errors
```

## Best Practices

### Logging Best Practices

1. **Structured Logging**: Use consistent log formats
2. **Appropriate Levels**: Use correct log levels for different types of events
3. **Performance Logging**: Track execution times for optimization
4. **Error Context**: Include relevant context in error messages
5. **Security**: Don't log sensitive information

### Monitoring Best Practices

1. **Real-time Monitoring**: Monitor logs in real-time during development
2. **Automated Alerts**: Set up alerts for critical errors
3. **Regular Analysis**: Regularly analyze logs for patterns and trends
4. **Log Retention**: Implement appropriate log retention policies
5. **Dashboard Creation**: Create dashboards for key metrics

### Troubleshooting Workflow

1. **Identify Issue**: Use logs to identify the root cause
2. **Reproduce**: Try to reproduce the issue using log information
3. **Analyze**: Analyze error patterns and frequency
4. **Fix**: Implement fixes based on log analysis
5. **Monitor**: Monitor logs to verify fixes work correctly

This comprehensive logging and monitoring approach ensures you can effectively track, analyze, and troubleshoot your AI agent system.