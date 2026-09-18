// Anyone authenticated as Citizen or above can submit hazard reports
permit(
    principal in Role::"Citizen",
    action == Action::"SubmitHazardReport",
    resource
);

// Field Inspectors can verify field reports
permit(
    principal in Role::"FieldInspector",
    action == Action::"VerifyHazardReport",
    resource
);

// Only District Officers can close roads or broadcast regional alerts
permit(
    principal in Role::"DistrictOfficer",
    action in [Action::"UpdateRoadStatus", Action::"DispatchRegionalAlert"],
    resource
);
