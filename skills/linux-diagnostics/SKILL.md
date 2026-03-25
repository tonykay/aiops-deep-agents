# Linux Diagnostics

Systematic approach to diagnosing Linux host issues.

## Workflow

1. **Gather context**: What symptom triggered this? (alert, user report, monitoring)
2. **Check system health**: Load average, memory pressure, disk usage, OOM kills
3. **Examine services**: systemd unit status, failed units, recent restarts
4. **Review logs**: journalctl for the relevant time window, dmesg for kernel issues
5. **Profile if needed**: CPU (perf/top), memory (vmstat/slabtop), disk (iostat/iotop), network (ss/netstat)

## Diagnostic Commands

```bash
# Quick health check
uptime && free -h && df -h && systemctl --failed

# Recent kernel messages
dmesg --since "1 hour ago" | tail -50

# Service investigation
systemctl status <unit> && journalctl -u <unit> --since "1 hour ago" --no-pager

# Performance snapshot
vmstat 1 5 && iostat -xz 1 5
```

## Output Format

Save findings to `investigations/<incident-slug>/linux-diag.md` with:
- **Symptom**: What was observed
- **Findings**: What the diagnostics revealed (include command output excerpts)
- **Root cause**: Confirmed or suspected
- **Remediation**: Exact commands to fix, with rollback steps
