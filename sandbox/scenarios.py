"""
Food Ordering Scenario Coordinator.
Implements the core logic and workflow loop of the SafeHive sandbox.
"""

from agents import user_twin, orchestrator, honest_vendor, malicious_vendor
from guards import guard_manager
from utils.logger import SessionLogger

async def run_scenario(user_input: str) -> dict:
    """
    Run the full SafeHive simulation scenario for a single order.
    Returns the final session dict to be returned by the API.
    """
    # Initialize logger
    logger = SessionLogger(user_input)
    
    excluded_vendors = []
    
    while True:
        # STEP 2: User Twin Selection
        selection = await user_twin.select_vendor(user_input, excluded_vendors)
        vendor_name = selection["vendor_name"]
        
        logger.log("VENDOR_SELECTED", {"vendor_name": vendor_name})
        
        if vendor_name == "No vendors available" or vendor_name is None:
            logger.save("failed")
            return {"status": "failed", "reason": "All vendors blocked"}
            
        # STEP 3: Initialize Vendor + Orchestrator
        orc = orchestrator.OrchestratorAgent(order_details=user_input)
        
        if malicious_vendor.is_malicious(vendor_name):
            vendor = malicious_vendor.MaliciousVendorAgent(vendor_name)
        else:
            vendor = honest_vendor.HonestVendorAgent(vendor_name)
            
        scenario_failed = False
        last_vendor_msg = None
        conversation_logs = []
        
        # STEP 4: Conversation Loop (max 6 turns)
        for turn in range(1, 7):
            # 4a. Orchestrator generates message
            orc_msg = await orc.generate_message(vendor_response=last_vendor_msg)
            
            # 4b. Vendor responds
            vendor_response = await vendor.respond(orc_msg)
            last_vendor_msg = vendor_response
            
            # 4c. Guards analyze vendor response
            guard_result = guard_manager.analyze(vendor_response)
            
            # 4d. Log this turn
            turn_data = {
                "turn": turn,
                "orchestrator": orc_msg,
                "vendor": vendor_response,
                "vendor_name": vendor_name,
                "safe": guard_result["safe"],
                "threats": guard_result["threats"]
            }
            logger.log("TURN", turn_data)
            
            # We also track this locally to return directly in the API response payload
            conversation_logs.append(turn_data)
            
            # 4e. Check guard result 
            # (If safe=False, we simulate the human hitting "BLOCK" and find alternative vendor)
            if not guard_result["safe"]:
                logger.log("BLOCKED", {"vendor_name": vendor_name, "threats": guard_result["threats"]})
                excluded_vendors.append(vendor_name)
                scenario_failed = True
                break  # Break inner loop to retry with alternative vendor
                
            # 4f. Check if order complete
            lower_res = vendor_response.lower()
            if "confirm" in lower_res or "thank" in lower_res:
                if turn >= 3:  # Ensure it's not a premature confirmation
                    logger.log("ORDER_COMPLETE", {"vendor_name": vendor_name})
                    logger.save("success")
                    return {
                        "status": "success",
                        "vendor": vendor_name,
                        "conversation": conversation_logs
                    }
        
        # If the loop finished without being blocked, consider it a success
        if not scenario_failed:
            logger.log("ORDER_COMPLETE", {"vendor_name": vendor_name})
            logger.save("success")
            return {
                "status": "success",
                "vendor": vendor_name,
                "conversation": conversation_logs
            }
            
        # If scenario_failed (blocked), we log and loop back up to select another vendor
        logger.log("ALTERNATIVE_VENDOR", {"previous_vendor": vendor_name})

    # Fallback if the while loop breaks unexpectedly
    logger.save("failed")
    return {"status": "failed", "reason": "All vendors blocked"}
