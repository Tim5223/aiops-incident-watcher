import os

# When "true" (default), remediation actions are only decided and logged,
# never actually executed against the cluster. Flip to "false" once you've
# set up kubeconfig access from wherever this app runs.
DRY_RUN = os.getenv("REMEDIATION_DRY_RUN", "true").lower() != "false"

_k8s_client = None


def _get_k8s_client():
    """Lazily initializes the Kubernetes client, only when actually needed."""
    global _k8s_client
    if _k8s_client is None:
        from kubernetes import client, config

        config.load_kube_config()  # reads from ~/.kube/config
        _k8s_client = client.CoreV1Api()
    return _k8s_client


# --- Safety policy -----------------------------------------------------
# This is the single most important design decision in the whole project:
# which alerts are safe to auto-remediate, and which should only ever alert.
# Keep this list conservative and explicit — never guess for unknown alerts.

SAFE_TO_AUTO_REMEDIATE = {
    "PodCrashLooping": "restart_pod",
}


def decide_and_act(alert_name: str, labels: dict) -> tuple[str, str]:
    """
    Given an alert name and its labels, decides what action to take.

    Returns a tuple: (action_taken, outcome)
      - action_taken: "restarted_pod", "alerted_only", or "dry_run_would_restart_pod"
      - outcome: free-text description of what happened (or would happen)
    """
    action = SAFE_TO_AUTO_REMEDIATE.get(alert_name)

    if action is None:
        return "alerted_only", f"No auto-remediation rule for '{alert_name}'. Manual review needed."

    if action == "restart_pod":
        pod_name = labels.get("pod")
        namespace = labels.get("namespace", "default")

        if not pod_name:
            return "alerted_only", "Alert matched restart_pod policy but no pod name in labels."

        if DRY_RUN:
            return (
                "dry_run_would_restart_pod",
                f"[DRY RUN] Would have restarted pod '{pod_name}' in namespace '{namespace}'.",
            )

        return _restart_pod(pod_name, namespace)

    return "alerted_only", f"Unrecognized action '{action}' in policy."


def _restart_pod(pod_name: str, namespace: str) -> tuple[str, str]:
    """
    Actually deletes the pod via the Kubernetes API. In a Deployment/ReplicaSet,
    deleting a pod causes Kubernetes to automatically create a fresh replacement
    — this is the standard, safe way to "restart" a pod.
    """
    try:
        k8s = _get_k8s_client()
        k8s.delete_namespaced_pod(name=pod_name, namespace=namespace)
        return "restarted_pod", f"Deleted pod '{pod_name}' in namespace '{namespace}'; Kubernetes will recreate it."
    except Exception as e:
        return "remediation_failed", f"Failed to restart pod '{pod_name}': {e}"
