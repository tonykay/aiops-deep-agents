# DNS Troubleshooting

Diagnosing name resolution issues across infrastructure.

## Workflow

1. **Test resolution**: dig/nslookup from the affected host
2. **Check resolver config**: /etc/resolv.conf, systemd-resolved status
3. **Trace the query path**: recursive resolution through each nameserver
4. **Verify zone data**: SOA, NS records, TTLs, DNSSEC validation
5. **Check for split-horizon**: Internal vs external resolution differences

## Diagnostic Commands

```bash
# Basic resolution
dig <domain> A +short
dig <domain> AAAA +short
dig <domain> @<nameserver> A +trace

# Resolver configuration
cat /etc/resolv.conf
resolvectl status

# Reverse DNS
dig -x <ip>

# Zone transfer test (if authorized)
dig @<nameserver> <domain> AXFR

# Kubernetes DNS (CoreDNS)
kubectl -n kube-system logs -l k8s-app=kube-dns --tail=50
kubectl run -it --rm dns-test --image=busybox -- nslookup <service>.<namespace>.svc.cluster.local
```

## Output Format

Save findings to `investigations/<incident-slug>/dns-diag.md` with symptom, findings, root cause, and remediation.
