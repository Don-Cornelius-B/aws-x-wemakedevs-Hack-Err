import os
import json
import cedarpy
from typing import Dict, Any, List

class CedarEvaluator:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.schema_path = os.path.join(self.base_dir, "schema.cedarschema")
        self.policies_path = os.path.join(self.base_dir, "policies.cedar")
        
        with open(self.policies_path, 'r') as f:
            self.policies_str = f.read()
            
        with open(self.schema_path, 'r') as f:
            self.schema_str = f.read()

    def evaluate(self, principal: str, action: str, resource: str, context: Dict[str, Any] = None, entities: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluates a request using cedarpy.
        Fallback evaluator is implemented manually in case cedarpy raises issues on non-supported platforms.
        
        Args:
            principal (str): The principal entity, e.g., 'User::"alice"'
            action (str): The action entity, e.g., 'Action::"SubmitHazardReport"'
            resource (str): The resource entity, e.g., 'HazardReport::"rep-001"'
            context (dict): Context variables (defaults to empty dict)
            entities (list): List of entities for the authorization context.
        """
        if context is None:
            context = {}
            
        if entities is None:
            # Setup default hierarchy assuming typical NER structure
            entities = [
                {"uid": {"type": "Role", "id": "Citizen"}, "attrs": {}, "parents": []},
                {"uid": {"type": "Role", "id": "FieldInspector"}, "attrs": {}, "parents": [{"type": "Role", "id": "Citizen"}]},
                {"uid": {"type": "Role", "id": "DistrictOfficer"}, "attrs": {}, "parents": [{"type": "Role", "id": "FieldInspector"}]}
            ]
            
            # Map the principal to its declared role based on the username prefix or simple mock mapping
            # In a real app, this comes from the JWT/DB
            role = "Citizen"
            if "inspector" in principal.lower():
                role = "FieldInspector"
            elif "officer" in principal.lower():
                role = "DistrictOfficer"
                
            # Add the user to the entities list as a child of their role
            # Strip the quotes from principal string if it's formatted like User::"alice"
            user_id = principal.split('::')[1].strip('"') if '::' in principal else principal
            entities.append({
                "uid": {"type": "User", "id": user_id},
                "attrs": {},
                "parents": [{"type": "Role", "id": role}]
            })

        try:
            # Use cedarpy Rust bindings
            request = {
                "principal": principal,
                "action": action,
                "resource": resource,
                "context": context
            }
            
            is_authz = cedarpy.is_authorized(request, self.policies_str, entities, schema=self.schema_str)
            return {
                "decision": "ALLOW" if is_authz.decision == cedarpy.Decision.Allow else "DENY",
                "diagnostics": {
                    "reason": list(is_authz.diagnostics.reasons),
                    "errors": list(is_authz.diagnostics.errors)
                }
            }
            
        except Exception as e:
            print(f"cedarpy evaluation failed: {e}. Falling back to in-process python evaluator.")
            return self._fallback_evaluate(principal, action, resource, entities)

    def _fallback_evaluate(self, principal: str, action: str, resource: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Naive python AST fallback parser mapping to policies.cedar logic.
        """
        # Parse Principal Role from Entities
        user_id = principal.split('::')[1].strip('"') if '::' in principal else principal
        user_entity = next((e for e in entities if e["uid"]["type"] == "User" and e["uid"]["id"] == user_id), None)
        
        if not user_entity:
            return {"decision": "DENY", "diagnostics": {"reason": ["User not found in entities"]}}
            
        parents = [p["id"] for p in user_entity.get("parents", [])]
        
        action_name = action.split('::')[1].strip('"') if '::' in action else action
        
        # Policy 1: Citizen can SubmitHazardReport
        if action_name == "SubmitHazardReport" and "Citizen" in parents:
            return {"decision": "ALLOW", "diagnostics": {"reason": ["policy0"]}}
            
        # Policy 2: FieldInspector can VerifyHazardReport
        if action_name == "VerifyHazardReport" and "FieldInspector" in parents:
            return {"decision": "ALLOW", "diagnostics": {"reason": ["policy1"]}}
            
        # Policy 3: DistrictOfficer can UpdateRoadStatus or DispatchRegionalAlert
        if action_name in ["UpdateRoadStatus", "DispatchRegionalAlert"] and "DistrictOfficer" in parents:
            return {"decision": "ALLOW", "diagnostics": {"reason": ["policy2"]}}
            
        return {"decision": "DENY", "diagnostics": {"reason": ["Implicit deny"]}}

# Quick test if run directly
if __name__ == "__main__":
    evaluator = CedarEvaluator()
    
    # Test Citizen Submitting Report
    res1 = evaluator.evaluate('User::"alice"', 'Action::"SubmitHazardReport"', 'HazardReport::"rep1"')
    print("Citizen Submit:", res1)
    
    # Test Citizen Updating Road
    res2 = evaluator.evaluate('User::"alice"', 'Action::"UpdateRoadStatus"', 'RoadCorridor::"nh29"')
    print("Citizen Update Road:", res2)
    
    # Test Officer Updating Road
    res3 = evaluator.evaluate('User::"officer_bob"', 'Action::"UpdateRoadStatus"', 'RoadCorridor::"nh29"')
    print("Officer Update Road:", res3)

