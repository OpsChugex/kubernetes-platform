# OCX-PLAT-001: Kubernetes Platform Reference

[![Validate Kubernetes reference](https://github.com/OpsChugex/kubernetes-platform/actions/workflows/validate.yml/badge.svg)](https://github.com/OpsChugex/kubernetes-platform/actions/workflows/validate.yml)

**Classification:** Reference implementation

**Deployment status:** Documented and validated, not presented as a customer production environment.

This repository defines a security-focused Kubernetes application namespace pattern with:

- restricted Pod Security enforcement
- dedicated ServiceAccount with token automount disabled
- non-root workload execution
- RuntimeDefault seccomp
- privilege escalation disabled
- Linux capabilities dropped
- read-only root filesystem
- CPU and memory requests and limits
- readiness and liveness probes
- two-replica baseline
- PodDisruptionBudget
- HorizontalPodAutoscaler
- ClusterIP-only service exposure
- default-deny ingress and egress network policy

## Reproduce the validation

The validator reads the Kubernetes YAML offline. It does not connect to a Kubernetes cluster.

```bash
python -m pip install PyYAML==6.0.3
python validate_platform.py
```

The GitHub Actions workflow repeats the same checks with read-only repository permissions and actions pinned to immutable commit SHAs.

## Evidence interpretation

A passing workflow proves that the checked manifest contains the documented security and reliability controls for that commit.

It does not prove that a customer cluster is running this manifest, that a production cluster is compliant, or that an external security assessment has been completed.

## Operational note

The baseline uses default-deny ingress and egress, then adds one explicit rule allowing traffic to the reference application only from pods in the same namespace on TCP 8080. External ingress remains blocked until an environment-specific policy is added. Production DNS, egress, ingress-controller, service-mesh and observability rules should be defined explicitly for the target environment.
