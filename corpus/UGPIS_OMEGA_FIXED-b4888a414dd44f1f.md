@app.post("/process_comprehensive")
async def process_comprehensive_endpoint(payload: Dict[str, Any]):
    """
    Comprehensive endpoint that accepts full domain context.
    DOMAIN KNOWLEDGE CONFIGURATION:
    - Expects metrics named: daily_census, false_positive_count
    - Expects clinical signal with temporal markers
    - Returns full audit trail + all subsystem outputs
    """
    try:
        inbound_title = payload.get("title", "Comprehensive Request")
        inbound_text = payload.get("text", "")
        
        # Parse incoming metrics
        metrics_input = payload.get("metrics", {})
        context_input = payload.get("context", {})
        
        telemetry_snapshot = TelemetrySnapshot(
            timestamp=dt.utcnow(),
            metric_rate_a=metrics_input.get("metric_rate_a", 1.0),
            metric_rate_b=metrics_input.get("metric_rate_b", 0.5),
            ratio_metric_c=metrics_input.get("ratio_metric_c", 0.2),
            scalar_metric_d=metrics_input.get("scalar_metric_d", 0.1),
            vector_subset_e=metrics_input.get("vector_subset_e", 0.0),
            vector_subset_f=metrics_input.get("vector_subset_f", 0.0),
            scalar_metric_g=metrics_input.get("scalar_metric_g", 0.0),
            data_source_id=context_input.get("source_id", "hardware_stream"),
        )

transaction_context = TransactionContext(
            source_identifier=context_input.get("source_id", "source-device-001"),
            scale_factor_alpha=context_input.get("scale_factor_alpha", 1.0),
            scale_factor_beta=context_input.get("scale_factor_beta"),
            unit_assignment=OperationalUnit[context_input.get("unit", "STANDARD_WARD")],
            execution_stage=ExecutionStage[context_input.get("stage", "INITIAL_STAGE")],
            signal_classification=SignalClassification[context_input.get("classification", "GENERAL")],
            interval_index=context_input.get("interval_index"),
            temporal_modifier=context_input.get("temporal_modifier", "cycle_period_1"),
        )

baseline_metrics_input = payload.get("baseline_metrics", {})
        current_metrics_input = payload.get("current_metrics", {})
        
        baseline_metrics = SystemMetricsTelemetry(
            containment_efficiency=baseline_metrics_input.get("containment_efficiency", 0.85),
            processing_latency=baseline_metrics_input.get("processing_latency", 50.0),
            recurrent_action_rate=baseline_metrics_input.get("recurrent_action_rate", 0.01),
            dropout_rate=baseline_metrics_input.get("dropout_rate", 0.01),
            automation_trigger_rate=baseline_metrics_input.get("automation_trigger_rate", 0.02),
            determinism_index=baseline_metrics_input.get("determinism_index", 1.0),
            repeat_step_rate=baseline_metrics_input.get("repeat_step_rate", 0.005),
            reentry_rate=baseline_metrics_input.get("reentry_rate", 0.01),
            escalation_rate=baseline_metrics_input.get("escalation_rate", 0.01),
            abrupt_disconnect_rate=baseline_metrics_input.get("abrupt_disconnect_rate", 0.0),
            backlog_depth=baseline_metrics_input.get("backlog_depth", 2.0),
        )
        
        current_metrics = SystemMetricsTelemetry(
            containment_efficiency=current_metrics_input.get("containment_efficiency", 0.82),
            processing_latency=current_metrics_input.get("processing_latency", 75.0),
            recurrent_action_rate=current_metrics_input.get("recurrent_action_rate", 0.02),
            dropout_rate=current_metrics_input.get("dropout_rate", 0.05),
            automation_trigger_rate=current_metrics_input.get("automation_trigger_rate", 0.05),
            determinism_index=current_metrics_input.get("determinism_index", 0.95),
            repeat_step_rate=current_metrics_input.get("repeat_step_rate", 0.02),
            reentry_rate=current_metrics_input.get("reentry_rate", 0.03),
            escalation_rate=current_metrics_input.get("escalation_rate", 0.1),
            abrupt_disconnect_rate=current_metrics_input.get("abrupt_disconnect_rate", 0.001),
            backlog_depth=current_metrics_input.get("backlog_depth", 10.0),
        )

eddp_raw_data = {
            "source_id": context_input.get("source_id", "source-device-001"),
            "timestamp": time.time(),
            "metrics": {
                "daily_census": metrics_input.get("daily_census", 80000),
                "false_positive_count": metrics_input.get("false_positive_count", 2500),
            },
            "attributes": payload.get("attributes", {}),
            "execution_context": context_input.get("execution_context", "standard_evaluation_profile"),
            "metadata": payload.get("metadata", {}),
        }

result = await controller.process_inbound(
            inbound_title=inbound_title,
            inbound_text=inbound_text,
            telemetry_snapshot=telemetry_snapshot,
            transaction_context=transaction_context,
            live_signal_value=payload.get("live_signal_value", 100.0),
            baseline_metrics=baseline_metrics,
            current_metrics=current_metrics,
            eddp_raw_data=eddp_raw_data,
            eddp_context_key=context_input.get("execution_context", "standard_evaluation_profile"),
        )

return JSONResponse(result)
    
    except Exception as e:
        logger.error(f"Comprehensive processing failed: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=400)

@app.get("/audit_trail")
def get_audit_trail():
    """Export complete audit trail for compliance review."""
    return JSONResponse({
        "audit_entries": len(controller.audit_trail),
        "chain_integrity_verified": controller.audit_trail.verify_chain_integrity(),
        "ledger_export": controller.audit_trail.export_serialized_ledger(),
        "gsa_state_transitions": controller.global_state.state_transition_history,
        "fortress_state_transitions": [vars(t) for t in controller.fortress.state_transitions],
    })

@app.get("/system_diagnostics")
def get_system_diagnostics():
    """Real-time system state and diagnostics."""
    return JSONResponse({
        "timestamp": dt.utcnow().isoformat(),
        "global_state": {
            "health_index": controller.global_state.system_health_index,
            "sustainability_score": controller.global_state.sustainability_score,
            "emergency_escalation_tier": controller.global_state.emergency_escalation_tier,
            "integrity_debt_balance": controller.global_state.integrity_debt_balance,
            "trajectory_vectors": controller.global_state.current_trajectory_vectors,
        },
        "fortress_state": {
            "current_mode": "OVERRIDE" if controller.fortress.is_state_override_engaged else "NOMINAL",
            "blending_coefficient": round(controller.fortress.blending_coefficient, 3),
            "error_history_size": len(controller.fortress.error_history),
            "total_transitions": len(controller.fortress.state_transitions),
        },
        "audit_trail_integrity": {
            "total_entries": len(controller.audit_trail),
            "chain_verified": controller.audit_trail.verify_chain_integrity(),
        },
        "eddp_pipeline_health": {
            "processing_uniqueness_ratio": controller.eddp_ledger.verify_processing_uniqueness(),
            "total_transactions": len(controller.eddp_ledger.audit_history),
        },
    })

@app.post("/validate_clinical_signal")
async def validate_clinical_signal_endpoint(payload: Dict[str, Any]):
    """Validate a clinical signal for minimum coherence requirements."""
    signal_text = payload.get("text", "")
    is_valid, failures = controller.clinical_validator.validate_signal(signal_text)
    
    return JSONResponse({
        "signal_text": signal_text[:200],
        "is_clinically_valid": is_valid,
        "validation_failures": failures,
        "validation_log": controller.clinical_validator.validation_log[-5:],  # Last 5 validations
    })

if __name__ == "__main__":
    import uvicorn
    logger.info("UGPIS-Ω starting up...")
    logger.info("Available endpoints:")
    logger.info("  POST /process_inbound - Basic processing")
    logger.info("  POST /process_comprehensive - Full context processing")
    logger.info("  POST /validate_clinical_signal - Clinical signal validation")
    logger.info("  GET /audit_trail - Compliance audit export")
    logger.info("  GET /system_diagnostics - Real-time system state")
    logger.info("  GET /health - Health check")
    logger.info("  GET /metrics - Prometheus metrics")
    uvicorn.run(app, host="0.0.0.0", port=8000)
