# Kubernetes Troubleshooting

Systematic approach to diagnosing Kubernetes workload and cluster issues.

## Workflow

1. **Identify scope**: Is this a pod, deployment, node, or cluster-wide issue?
2. **Check events**: `kubectl get events --sort-by='.lastTimestamp'` in the relevant namespace
3. **Describe the resource**: Get detailed status including conditions and events
4. **Examine logs**: Current and previous container logs
5. **Check resource pressure**: Node conditions, resource quotas, limit ranges

## Diagnostic Commands

```bash
# Namespace-scoped overview
kubectl get events -n <ns> --sort-by='.lastTimestamp' | tail -20
kubectl get pods -n <ns> -o wide

# Pod investigation
kubectl describe pod <pod> -n <ns>
kubectl logs <pod> -n <ns> --tail=100
kubectl logs <pod> -n <ns> --previous --tail=50

# Node health
kubectl get nodes -o wide
kubectl describe node <node> | grep -A5 Conditions

# Resource usage
kubectl top pods -n <ns> --sort-by=memory
kubectl top nodes
```

## Common Patterns

- **CrashLoopBackOff**: Check logs --previous, look for OOMKilled in describe
- **Pending pods**: Check events for scheduling failures, node resources, taints
- **ImagePullBackOff**: Verify image name, registry auth, network access
- **Evicted pods**: Node memory/disk pressure, check node conditions

## Output Format

Save findings to `investigations/<incident-slug>/k8s-diag.md` with:
- **Symptom**: What was observed
- **Affected resources**: Namespace, deployment, pods, nodes
- **Findings**: Event timeline and log excerpts
- **Root cause**: Confirmed or suspected
- **Remediation**: kubectl commands or manifest changes, with rollback
