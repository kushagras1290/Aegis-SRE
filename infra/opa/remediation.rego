package aegis.remediation
default allow := false
allow if {
  input.environment != "production"
  input.action in {"restart_pod", "invalidate_cache"}
}
allow if {
  input.environment == "production"
  input.approved == true
  input.role in {"SRE", "INCIDENT_COMMANDER", "ADMIN"}
  input.action in {"restart_pod", "rollback_deployment", "scale_deployment", "pause_rollout", "resume_rollout"}
}
