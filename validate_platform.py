from pathlib import Path
import yaml

docs = [doc for doc in yaml.safe_load_all(Path("platform.yaml").read_text(encoding="utf-8")) if doc]
by_kind = {}
for doc in docs:
    by_kind.setdefault(doc["kind"], []).append(doc)

required = {
    "Namespace", "ServiceAccount", "Deployment", "Service",
    "PodDisruptionBudget", "HorizontalPodAutoscaler", "NetworkPolicy",
}
assert required.issubset(by_kind), f"Missing kinds: {sorted(required - set(by_kind))}"

ns = by_kind["Namespace"][0]
labels = ns["metadata"]["labels"]
assert labels["pod-security.kubernetes.io/enforce"] == "restricted"
assert labels["pod-security.kubernetes.io/audit"] == "restricted"
assert labels["pod-security.kubernetes.io/warn"] == "restricted"

sa = by_kind["ServiceAccount"][0]
assert sa["automountServiceAccountToken"] is False

deployment = by_kind["Deployment"][0]
assert deployment["spec"]["replicas"] >= 2
pod = deployment["spec"]["template"]["spec"]
assert pod["serviceAccountName"] == "evidence-demo"
assert pod["automountServiceAccountToken"] is False
assert pod["securityContext"]["seccompProfile"]["type"] == "RuntimeDefault"
assert pod["topologySpreadConstraints"][0]["topologyKey"] == "kubernetes.io/hostname"

container = pod["containers"][0]
security = container["securityContext"]
assert security["allowPrivilegeEscalation"] is False
assert security["readOnlyRootFilesystem"] is True
assert security["runAsNonRoot"] is True
assert "ALL" in security["capabilities"]["drop"]
assert "requests" in container["resources"] and "limits" in container["resources"]
assert "readinessProbe" in container and "livenessProbe" in container

service = by_kind["Service"][0]
assert service["spec"].get("type", "ClusterIP") == "ClusterIP"

pdb = by_kind["PodDisruptionBudget"][0]
assert pdb["spec"]["minAvailable"] >= 1

hpa = by_kind["HorizontalPodAutoscaler"][0]
assert hpa["spec"]["minReplicas"] >= 2
assert hpa["spec"]["maxReplicas"] >= hpa["spec"]["minReplicas"]

policies = {item["metadata"]["name"]: item["spec"] for item in by_kind["NetworkPolicy"]}
deny = policies["default-deny"]
assert deny["podSelector"] == {}
assert set(deny["policyTypes"]) == {"Ingress", "Egress"}

allow = policies["allow-same-namespace-app-ingress"]
assert allow["podSelector"]["matchLabels"]["app"] == "evidence-demo"
assert allow["ingress"][0]["ports"][0]["port"] == 8080

print("KUBERNETES_REFERENCE=PASS")
print(f"DOCUMENTS={len(docs)}")
print("POD_SECURITY=restricted")
print("SERVICE_ACCOUNT_TOKEN_AUTOMOUNT=false")
print("NETWORK_POLICY=default-deny")
