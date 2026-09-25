# OCX-PLAT-001: Kubernetes Platform Reference

[![Validate Kubernetes reference](https://github.com/OpsChugex/kubernetes-platform/actions/workflows/validate.yml/badge.svg)](https://github.com/OpsChugex/kubernetes-platform/actions/workflows/validate.yml)

**Classification:** Reference implementation

**Deployment claim:** None

This repository defines and validates the operating shape of a security-conscious Kubernetes application namespace.

## Controls represented

- restricted Pod Security admission label
- dedicated service account
- automatic service-account token mounting disabled
- non-root container execution
- privilege escalation disabled
- all Linux capabilities dropped
- RuntimeDefault seccomp profile
- read-only root filesystem
- CPU and memory requests and limits
- readiness and liveness probes
- multiple replicas
- PodDisruptionBudget
- HorizontalPodAutoscaler
- ingress and egress NetworkPolicy

## Reproduce validation

```bash
python -m pip install -r requirements.txt
python validate_platform.py
```

The validator parses the Kubernetes YAML and checks the documented resource and workload controls.

## Automated evidence

GitHub Actions repeats the same validation on pushes, pull requests and manual runs. The workflow has read-only repository permissions and uses immutable action SHAs.

## Limitations

This repository is a reviewed reference pattern, not evidence of a customer cluster or production SLO. It deliberately avoids claiming workload performance, uptime or customer outcomes.
