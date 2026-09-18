import sys
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config import settings

# Adjust sys.path to find the policies module since it's mounted in the container
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
try:
    from policies.policy_evaluator import CedarEvaluator
    evaluator = CedarEvaluator()
except ImportError:
    evaluator = None
    print("WARNING: policies.policy_evaluator not found. Authorization will fail.")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Mock JWT decoding. For demo purposes, we will accept mock tokens
    or extract a 'role' and 'sub' directly if provided via a custom header or simple token.
    If no token is provided, default to a simulated Citizen.
    """
    if not token:
        # Default mock user for offline usage or easy demonstration
        return {"sub": "citizen_1", "role": "Citizen"}
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        # If decode fails, fallback to using the token string as the role for easy UI testing
        if token in ["Citizen", "FieldInspector", "DistrictOfficer"]:
            return {"sub": f"mock_user_{token}", "role": token}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_action(action_name: str, resource_type: str, resource_id: str = "default"):
    def role_checker(user: dict = Depends(get_current_user)):
        if evaluator is None:
            raise HTTPException(status_code=500, detail="Cedar Evaluator not initialized.")
            
        principal = f'User::"{user["sub"]}"'
        action = f'Action::"{action_name}"'
        resource = f'{resource_type}::"{resource_id}"'
        
        # We pass a modified principal containing the role so the evaluator fallback works easily
        # In a real app, the evaluator loads entities including user roles
        res = evaluator.evaluate(f'{user["role"]}::{user["sub"]}', action, resource)
        
        if res["decision"] != "ALLOW":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Access denied by Cedar policy. Diagnostics: {res.get('diagnostics')}"
            )
        return user
    return role_checker
