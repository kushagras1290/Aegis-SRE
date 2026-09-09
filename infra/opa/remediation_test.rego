package aegis.remediation

test_allow_production_rollback_with_approval if {
    allow with input as {
        "environment": "production",
        "approved": true,
        "role": "SRE",
        "action": "rollback_deployment"
    }
}

test_deny_production_rollback_without_approval if {
    not allow with input as {
        "environment": "production",
        "approved": false,
        "role": "SRE",
        "action": "rollback_deployment"
    }
}

test_allow_nonproduction_safe_restart if {
    allow with input as {
        "environment": "staging",
        "approved": false,
        "role": "ENGINEER",
        "action": "restart_pod"
    }
}
