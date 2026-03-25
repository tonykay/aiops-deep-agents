# Layer 2 Networking

Diagnosing L2 connectivity, VLAN, and switching issues.

## Workflow

1. **Verify link state**: Interface up/down, speed/duplex negotiation
2. **Check VLAN config**: Tagged/untagged ports, trunk configuration
3. **ARP/NDP tables**: Verify MAC address resolution
4. **Spanning tree**: Check for blocked ports, topology changes
5. **MAC flooding/loops**: Look for broadcast storms or duplicate MACs

## Diagnostic Commands

```bash
# Interface status
ip link show
ethtool <iface>

# VLAN configuration
ip -d link show | grep vlan
bridge vlan show

# ARP table
ip neigh show
arp -an

# Bridge/switching
bridge fdb show
bridge link show
```

## Output Format

Save findings to `investigations/<incident-slug>/l2-diag.md` with symptom, findings, root cause, and remediation.
