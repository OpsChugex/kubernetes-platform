from pathlib import Path

import yaml

documents = [
    doc for doc in yaml.safe_load_all(Path("platform.yaml").read_text(encoding="utf-8"))
    if doc
]

by_kind = {}
for doc in documents:
    by_kind.setdefault(doc.get("kind"), []).append(doc)

required_kinds = {
    "Namespace",
    "ServiceAccount",
    "Deployment",
    "Service",
    "PodDisruptionBudget",
    "HorizontalPodAutoscaler",
    "NetworkPolicy",
}
missing = required_kinds - set(by_kind)
assert not missing, f"Missing Kubernetes resources: {sorted(missing)}"

namespace = by_kind["Namespace"][0]
labels = namespace["metadata"].get("labels", {})
assert labels.get("pod-security.kubernetes.io/enforce") == "restricted"

service_account = by_kind["ServiceAccount"][0]
assert service_account.get("automountServiceAccountToken") is False

deployment = by_kind["Deployment"][0]
spec = deployment["spec"]
pod = spec["template"]["spec"]
container = pod["containers"][0]

assert spec.get("replicas", 0) >= 2
assert pod.get("automountServiceAccountToken") is False
assert pod["securityContext"]["seccompProfile"]["type"] == "RuntimeDefault"

security = container["securityContext"]
assert security["allowPrivilegeEscalation"] is False
assert security["readOnlyRootFilesystem"] is True
assert security["runAsNonRoot"] is True
assert security["capabilities"]["drop"] == ["ALL"]

resources = container["resources"]
assert resources["requests"]["cpu"]
assert resources["requests"]["memory"]
assert resources["limits"]["cpu"]
assert resources["limits"]["memory"]
assert container.get("readinessProbe")
assert container.get("livenessProbe")

hpa = by_kind["HorizontalPodAutoscaler"][0]["spec"]
assert hpa["minReplicas"] >= 2
assert hpa["maxReplicas"] >= hpa["minReplicas"]

pdb = by_kind["PodDisruptionBudget"][0]["spec"]
assert pdb.get("minAvailable") == 1

network_policy = by_kind["NetworkPolicy"][0]["spec"]
assert "Ingress" in network_policy["policyTypes"]
assert "Egress" in network_policy["policyTypes"]
assert network_policy["podSelector"] == {}

print("KUBERNETES_REFERENCE=PASS")
print(f"DOCUMENTS={len(documents)}")
