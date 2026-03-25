# Log Analysis

Shared skill for analyzing logs across any domain. Used by all SRE subagents.

## Workflow

1. **Identify log sources**: journalctl, application logs, container logs, syslog
2. **Time-bound the search**: Focus on the incident window (15 min before first alert)
3. **Filter for severity**: Errors and warnings first, then info for context
4. **Correlate across sources**: Match timestamps between system and application logs
5. **Extract patterns**: Repeated errors, rate changes, new error types

## Techniques

```bash
# Journalctl time-bounded search
journalctl --since "2024-01-15 14:00" --until "2024-01-15 15:00" -p err

# Frequency analysis
journalctl -u <unit> --since "1 hour ago" --no-pager | grep -i error | sort | uniq -c | sort -rn | head -20

# Container logs with timestamps
kubectl logs <pod> -n <ns> --timestamps --since=1h | grep -i -E "error|warn|fatal"
```

## Output Format

When analyzing logs, always include:
- **Time window**: Exact range analyzed
- **Log sources**: Which logs were checked
- **Key findings**: Error messages with timestamps and frequency
- **Correlation**: How findings relate to the reported symptom
