# Layer 3 Networking

Diagnosing IP routing, firewall, and L3 connectivity issues.

## Workflow

1. **Verify IP configuration**: Addresses, subnets, default gateway
2. **Test reachability**: ping, traceroute to isolate where traffic drops
3. **Check routing table**: Expected routes present, correct next-hops
4. **Examine firewalls**: iptables/nftables rules, security groups
5. **Routing protocols**: OSPF/BGP neighbor status, route advertisements

## Diagnostic Commands

```bash
# IP and routing
ip addr show
ip route show
ip route get <destination>
traceroute -n <destination>

# Firewall rules
iptables -L -n -v
nft list ruleset

# OSPF diagnostics (if applicable)
vtysh -c "show ip ospf neighbor"
vtysh -c "show ip route ospf"

# BGP diagnostics (if applicable)
vtysh -c "show bgp summary"
vtysh -c "show bgp neighbors <peer>"
```

## MTU Path Discovery

```bash
ping -M do -s 1472 <destination>  # Standard MTU test
tracepath <destination>            # Discovers MTU along path
```

## Output Format

Save findings to `investigations/<incident-slug>/l3-diag.md` with symptom, findings, root cause, and remediation.
